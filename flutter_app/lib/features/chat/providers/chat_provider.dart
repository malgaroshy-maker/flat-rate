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

  void send(String message, {String lang = 'ar'}) {
    _subscription?.cancel();
    _fullResponse = '';
    _ref.read(chatStatusProvider.notifier).state = null;
    final msgs = <ChatMessage>[...(state.valueOrNull ?? [])];
    state = const AsyncValue.loading();

    // Persist user message locally
    final sid = _sessionId;
    if (sid != null) {
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
        _ref.read(chatStatusProvider.notifier).state = null;
        state = AsyncValue.error(err, StackTrace.current);
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
