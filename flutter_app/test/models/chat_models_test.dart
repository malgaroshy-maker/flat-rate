import 'package:flutter_test/flutter_test.dart';
import 'package:labor_app/features/chat/domain/chat_models.dart';

void main() {
  group('ChatMessage', () {
    test('fromJson creates correct message', () {
      final json = {'role': 'user', 'content': 'Hello'};
      final msg = ChatMessage.fromJson(json);
      expect(msg.role, 'user');
      expect(msg.content, 'Hello');
    });

    test('fromJson handles missing fields', () {
      final msg = ChatMessage.fromJson({});
      expect(msg.role, '');
      expect(msg.content, '');
    });

    test('const constructor', () {
      const msg = ChatMessage(role: 'assistant', content: 'Hi');
      expect(msg.role, 'assistant');
      expect(msg.content, 'Hi');
    });
  });

  group('ChatSession', () {
    test('fromJson creates correct session', () {
      final json = {
        'id': 'abc123',
        'title': 'Test chat',
        'message_count': 2,
        'lang': 'en',
        'messages': [
          {'role': 'user', 'content': 'Q'},
          {'role': 'assistant', 'content': 'A'},
        ],
      };
      final session = ChatSession.fromJson(json);
      expect(session.id, 'abc123');
      expect(session.title, 'Test chat');
      expect(session.messageCount, 2);
      expect(session.messages.length, 2);
      expect(session.lang, 'en');
    });

    test('fromJson handles missing messages', () {
      final json = {'id': 'x', 'title': '', 'message_count': 1};
      final session = ChatSession.fromJson(json);
      expect(session.messages, isEmpty);
    });

    test('fromJson uses message_count from messages list when missing', () {
      final json = {
        'id': 'x',
        'title': '',
        'messages': [
          {'role': 'user', 'content': 'a'},
          {'role': 'user', 'content': 'b'},
          {'role': 'user', 'content': 'c'},
        ],
      };
      final session = ChatSession.fromJson(json);
      expect(session.messageCount, 3);
    });
  });
}
