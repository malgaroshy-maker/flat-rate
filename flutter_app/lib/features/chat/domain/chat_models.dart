class ChatMessage {
  final String role;
  final String content;

  const ChatMessage({required this.role, required this.content});

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(role: json['role'] ?? '', content: json['content'] ?? '');
  }
}

class ChatSession {
  final String id;
  final String title;
  final int messageCount;
  final List<ChatMessage> messages;
  final String lang;

  const ChatSession({
    required this.id,
    required this.title,
    required this.messageCount,
    this.messages = const [],
    this.lang = 'ar',
  });

  factory ChatSession.fromJson(Map<String, dynamic> json) {
    final msgs = (json['messages'] as List<dynamic>?)
        ?.map((m) => ChatMessage.fromJson(m as Map<String, dynamic>))
        .toList() ?? [];
    return ChatSession(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      messageCount: (json['message_count'] ?? msgs.length) as int,
      messages: msgs,
      lang: json['lang'] ?? 'ar',
    );
  }
}
