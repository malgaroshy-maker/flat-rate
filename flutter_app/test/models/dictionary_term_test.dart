import 'package:flutter_test/flutter_test.dart';
import 'package:labor_app/features/dictionary/domain/dictionary_term.dart';

void main() {
  group('DictionaryTerm', () {
    test('fromJson creates correct term', () {
      final json = {
        'id': 't1',
        'arabic_term': 'مسمار ميزان',
        'standard_category': 'Suspension',
        'english_term': 'Stabilizer Link',
      };
      final term = DictionaryTerm.fromJson(json);
      expect(term.id, 't1');
      expect(term.arabicTerm, 'مسمار ميزان');
      expect(term.standardCategory, 'Suspension');
      expect(term.englishTerm, 'Stabilizer Link');
    });

    test('fromJson handles missing fields', () {
      final term = DictionaryTerm.fromJson({});
      expect(term.id, '');
      expect(term.arabicTerm, '');
      expect(term.standardCategory, '');
      expect(term.englishTerm, '');
    });

    test('toCreateJson omits id', () {
      final term = DictionaryTerm(
        id: 't1',
        arabicTerm: 'اختبار',
        standardCategory: 'Test',
        englishTerm: 'Test',
      );
      final json = term.toCreateJson();
      expect(json.containsKey('id'), isFalse);
      expect(json['arabic_term'], 'اختبار');
    });

    test('toUpdateJson matches toCreateJson', () {
      final term = DictionaryTerm(
        id: 't1',
        arabicTerm: 'اختبار',
        standardCategory: 'Test',
      );
      final update = term.toUpdateJson();
      final create = term.toCreateJson();
      expect(update, equals(create));
    });
  });
}
