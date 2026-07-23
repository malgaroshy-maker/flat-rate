import 'package:flutter_test/flutter_test.dart';
import 'package:labor_app/features/pending/domain/pending_item.dart';

void main() {
  group('PendingItem', () {
    test('fromJson creates correct item', () {
      final json = {
        'id': 'p1',
        'term_text': 'لفافة',
        'query_text': 'لفافة HD45',
        'status': 'pending',
      };
      final item = PendingItem.fromJson(json);
      expect(item.id, 'p1');
      expect(item.termText, 'لفافة');
      expect(item.queryText, 'لفافة HD45');
      expect(item.status, 'pending');
    });

    test('fromJson defaults status to pending', () {
      final item = PendingItem.fromJson({
        'id': 'p2',
        'term_text': 'x',
        'query_text': 'y',
      });
      expect(item.status, 'pending');
    });
  });

  group('ResolvePayload', () {
    test('toJson serializes correctly', () {
      final payload = ResolvePayload(
        arabicTerm: 'اختبار',
        standardCategory: 'Test',
        englishTerm: 'Testing',
      );
      final json = payload.toJson();
      expect(json['arabic_term'], 'اختبار');
      expect(json['standard_category'], 'Test');
      expect(json['english_term'], 'Testing');
    });

    test('toJson omits empty englishTerm', () {
      final payload = ResolvePayload(
        arabicTerm: 'اختبار',
        standardCategory: 'Test',
      );
      final json = payload.toJson();
      expect(json['english_term'], '');
    });
  });
}
