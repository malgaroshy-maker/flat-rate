import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/services/local_db.dart';
import '../data/chat_repository.dart';
import '../domain/chat_models.dart';

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
    state = AsyncValue.data(messages);
  }

  void send(String message, {String lang = 'ar', bool persistUserMessage = true}) {
    _subscription?.cancel();
    _fullResponse = '';
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
        state = AsyncValue.data([
          ...msgs,
          ChatMessage(role: 'error', content: err.toString()),
        ]);
      },
      onDone: () {
        _ref.read(chatStatusProvider.notifier).state = null;
        if (buffer.isEmpty) {
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
