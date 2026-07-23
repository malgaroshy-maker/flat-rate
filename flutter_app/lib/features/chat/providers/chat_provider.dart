import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/services/api_key_service.dart';
import '../../../core/services/local_db.dart';
import '../data/chat_repository.dart';
import '../domain/chat_models.dart';

bool _isConnectivityError(Object err) {
  return err is DioException &&
      (err.type == DioExceptionType.connectionError ||
          err.type == DioExceptionType.connectionTimeout ||
          err.type == DioExceptionType.unknown);
}

final chatRepositoryProvider =
    Provider<ChatRepository>((ref) => ChatRepository());

/// Latest progress status from the backend ("searching" / "thinking"),
/// null once the first text token arrives. Consumed by the chat screen to
/// show a typing/progress indicator instead of a blank wait.
final chatStatusProvider = StateProvider<String?>((ref) => null);

final sessionsProvider = FutureProvider<List<ChatSession>>((ref) async {
  final rows = await LocalDb().getSessions();
  return rows
      .map((r) => ChatSession(
            id: r['id'] as String,
            title: (r['title'] as String?) ?? '',
            messageCount: 0,
            lang: (r['lang'] as String?) ?? 'ar',
          ))
      .toList();
});

class ChatNotifier extends StateNotifier<AsyncValue<List<ChatMessage>>> {
  final ChatRepository _repo;
  final Ref _ref;
  String? _sessionId;
  StreamSubscription<String>? _subscription;
  String _fullResponse = '';
  List<ChatMessage> _msgsBeforeSend = [];
  bool _keyErrorHandled = false;

  ChatNotifier(this._repo, this._ref) : super(const AsyncValue.data([]));

  String? get sessionId => _sessionId;

  String generateSessionId() =>
      DateTime.now().millisecondsSinceEpoch.toRadixString(36);

  void setSessionId(String? id) {
    _sessionId = id;
  }

  void addUserMessage(ChatMessage msg) {
    final msgs = state.valueOrNull ?? [];
    state = AsyncValue.data([...msgs, msg]);
  }

  void setSessionMessages(List<ChatMessage> msgs) {
    state = AsyncValue.data(msgs);
  }

  void setLoading() {
    state = const AsyncValue.loading();
  }

  Future<void> loadSession(String id) async {
    _sessionId = id;
    final db = LocalDb();
    final rows = await db.getMessages(id);
    final messages = rows
        .map((r) => ChatMessage(
              role: r['role'] as String,
              content: r['content'] as String,
            ))
        .toList();
    // Still-pending outbox entries for this session (app may have been
    // closed before connectivity returned) — show them as queued so the
    // user isn't left wondering whether their message actually sent.
    final pending = (await db.getOutboxMessages()).where((r) => r['session_id'] == id);
    for (final _ in pending) {
      messages.add(const ChatMessage(role: 'queued', content: ''));
    }
    state = AsyncValue.data(messages);
  }

  void send(
    String message, {
    String lang = 'ar',
    bool persistUserMessage = true,
    String? geminiApiKeyOverride,
    bool isKeyRetry = false,
  }) {
    _subscription?.cancel();
    _fullResponse = '';
    _keyErrorHandled = false;
    _ref.read(chatStatusProvider.notifier).state = null;
    final msgs = <ChatMessage>[...(state.valueOrNull ?? [])];
    _msgsBeforeSend = msgs;
    state = const AsyncValue.loading();

    // Persist user message locally (skipped on retry — it's already stored)
    final sid = _sessionId;
    if (sid != null && persistUserMessage) {
      LocalDb().addMessage(
          sessionId: sid, role: 'user', content: message);
    }

    // Build history from previous messages (exclude current)
    String? historyJson;
    if (msgs.isNotEmpty) {
      final prev = msgs.length > 1 ? msgs.sublist(0, msgs.length - 1) : <ChatMessage>[];
      if (prev.isNotEmpty) {
        historyJson = LocalDb().encodeHistory(
          prev.map((m) => {'role': m.role, 'content': m.content} as Map<String, dynamic>).toList(),
        );
      }
    }

    final stream = _repo.sendMessage(
      message,
      sessionId: _sessionId,
      lang: lang,
      history: historyJson,
      geminiApiKey: geminiApiKeyOverride,
    );

    final buffer = StringBuffer();

    _subscription = stream.listen(
      (data) {
        if (data.startsWith(sessionIdEventPrefix)) {
          _sessionId = data.substring(sessionIdEventPrefix.length);
          return;
        }
        if (data.startsWith(statusEventPrefix)) {
          _ref.read(chatStatusProvider.notifier).state =
              data.substring(statusEventPrefix.length);
          return;
        }
        if (data.startsWith(errorTypeEventPrefix)) {
          final errorType = data.substring(errorTypeEventPrefix.length);
          if (errorType == 'gemini_key_error') {
            _handleKeyError(message, lang, msgs, alreadyRetried: isKeyRetry);
          }
          return;
        }
        _ref.read(chatStatusProvider.notifier).state = null;
        buffer.write(data);
        _fullResponse = buffer.toString();
        state = AsyncValue.data([
          ...msgs,
          ChatMessage(role: 'assistant', content: _fullResponse),
        ]);
      },
      onError: (err) {
        // Keep the existing conversation visible — append an error bubble
        // instead of replacing the whole message list with AsyncValue.error,
        // which previously discarded everything on a network hiccup.
        _ref.read(chatStatusProvider.notifier).state = null;
        if (_isConnectivityError(err) && sid != null) {
          // No network at all — queue it instead of just failing. It gets
          // sent automatically once connectivity returns (see flushOutbox).
          LocalDb().queueOutboxMessage(sessionId: sid, message: message, lang: lang);
          state = AsyncValue.data([
            ...msgs,
            const ChatMessage(role: 'queued', content: ''),
          ]);
        } else {
          state = AsyncValue.data([
            ...msgs,
            ChatMessage(role: 'error', content: err.toString()),
          ]);
        }
      },
      onDone: () {
        _ref.read(chatStatusProvider.notifier).state = null;
        // A key-error retry (or the "add your key" prompt) already set
        // state to something other than `msgs` — don't stomp on it just
        // because no text token ever arrived on this particular stream.
        if (buffer.isEmpty && !_keyErrorHandled) {
          state = AsyncValue.data(msgs);
        }
        // Persist assistant response locally
        final sid = _sessionId;
        if (sid != null && _fullResponse.isNotEmpty) {
          LocalDb().addMessage(
              sessionId: sid,
              role: 'assistant',
              content: _fullResponse);
        }
      },
    );
  }

  /// The shared/active key failed (invalid or out of quota). If the user
  /// has a personal key saved, retry automatically with it; otherwise show
  /// a bubble prompting them to add one, with the pending message/lang
  /// captured so a follow-up retry can use it.
  Future<void> _handleKeyError(
    String message,
    String lang,
    List<ChatMessage> msgsBeforeThisSend, {
    required bool alreadyRetried,
  }) async {
    final savedKey = alreadyRetried ? null : await _ref.read(apiKeyServiceProvider).getKey();
    _keyErrorHandled = true;

    if (savedKey != null) {
      send(message, lang: lang, persistUserMessage: false, geminiApiKeyOverride: savedKey, isKeyRetry: true);
      return;
    }

    state = AsyncValue.data([
      ...msgsBeforeThisSend,
      ChatMessage(role: alreadyRetried ? 'key_needed_retry_failed' : 'key_needed', content: message),
    ]);
  }

  /// Retry a pending "key_needed" message once the user has saved a key
  /// (called from the chat screen's prompt action).
  void retryWithSavedKey(String message, {String lang = 'ar'}) {
    final msgs = state.valueOrNull;
    if (msgs == null) return;
    final cleaned = List<ChatMessage>.from(msgs)
      ..removeWhere((m) => m.role == 'key_needed' || m.role == 'key_needed_retry_failed');
    state = AsyncValue.data(cleaned);
    _handleKeyError(message, lang, cleaned, alreadyRetried: false);
  }

  void cancel() {
    _subscription?.cancel();
    _repo.cancelStream();
    _ref.read(chatStatusProvider.notifier).state = null;
    // If a partial response already arrived, keep it; otherwise fall back to
    // whatever the conversation looked like right before this send() call —
    // AsyncValue.loading() has no value to preserve on its own.
    state = AsyncValue.data(state.valueOrNull ?? _msgsBeforeSend);
  }

  /// Strip a trailing error bubble and resend the last user message.
  void retryLast({String lang = 'ar'}) {
    final msgs = state.valueOrNull;
    if (msgs == null || msgs.isEmpty) return;
    final cleaned = List<ChatMessage>.from(msgs);
    while (cleaned.isNotEmpty && cleaned.last.role == 'error') {
      cleaned.removeLast();
    }
    if (cleaned.isEmpty || cleaned.last.role != 'user') return;
    final lastUserText = cleaned.last.content;
    state = AsyncValue.data(cleaned);
    send(lastUserText, lang: lang, persistUserMessage: false);
  }

  void clear() {
    _subscription?.cancel();
    _sessionId = null;
    state = const AsyncValue.data([]);
  }

  /// Send everything queued in the offline outbox. Safe to call whenever
  /// connectivity is regained — a no-op if the outbox is empty, and skipped
  /// entirely while an interactive stream is already in flight so it can't
  /// steal the shared cancel token from a message the user is actively
  /// waiting on.
  Future<void> flushOutbox() async {
    if (_subscription != null) return;
    final outbox = await LocalDb().getOutboxMessages();
    for (final row in outbox) {
      final id = row['id'] as int;
      final sid = row['session_id'] as String;
      final msg = row['message'] as String;
      final lang = (row['lang'] as String?) ?? 'ar';

      final buffer = StringBuffer();
      try {
        await for (final data in _repo.sendMessage(msg, sessionId: sid, lang: lang)) {
          if (data.startsWith(sessionIdEventPrefix) || data.startsWith(statusEventPrefix)) continue;
          buffer.write(data);
        }
      } catch (_) {
        // Still offline (or another failure) — stop and try again on the
        // next connectivity-restored signal, leaving the rest queued.
        return;
      }

      if (buffer.isNotEmpty) {
        await LocalDb().addMessage(sessionId: sid, role: 'assistant', content: buffer.toString());
      }
      await LocalDb().removeOutboxMessage(id);

      if (sid == _sessionId) {
        await loadSession(sid);
      }
    }
  }

  Future<void> newSession() async {
    cancel();
    final sid = generateSessionId();
    await LocalDb().createSession(id: sid);
    _sessionId = sid;
    state = const AsyncValue.data([]);
  }

  @override
  void dispose() {
    _subscription?.cancel();
    _repo.dispose();
    super.dispose();
  }
}

final chatProvider = StateNotifierProvider<ChatNotifier,
    AsyncValue<List<ChatMessage>>>((ref) {
  return ChatNotifier(ref.watch(chatRepositoryProvider), ref);
});
