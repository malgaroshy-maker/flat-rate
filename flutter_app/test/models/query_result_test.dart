import 'package:flutter_test/flutter_test.dart';
import 'package:labor_app/features/search/domain/query_result.dart';

void main() {
  group('QueryHit', () {
    final sampleJson = {
      'id': 'hit-1',
      'model': 'HD45',
      'code': '2000',
      'departments': 'Diesel',
      'franchises': 'Hyundai',
      'qty_count': 50,
      'qty_median': 2.5,
      'qty_mean': 3.0,
      'price_mean': 45.0,
      'similarity': 0.92,
      'confidence_range': {
        'p10': 1.0,
        'p25': 1.5,
        'median': 2.5,
        'p75': 3.5,
        'p90': 4.0,
      },
    };

    test('fromJson creates correct hit', () {
      final hit = QueryHit.fromJson(sampleJson);
      expect(hit.id, 'hit-1');
      expect(hit.model, 'HD45');
      expect(hit.qtyCount, 50);
      expect(hit.p50, 2.5);
      expect(hit.p10, 1.0);
      expect(hit.p90, 4.0);
    });

    test('fromJson handles missing confidence_range', () {
      final json = {'id': 'x', 'model': 'Y', 'code': '1',
        'departments': '', 'franchises': '', 'qty_count': 1,
        'qty_median': 0, 'qty_mean': 0, 'price_mean': 0, 'similarity': 0};
      final hit = QueryHit.fromJson(json);
      expect(hit.p10, 0);
      expect(hit.p50, 0);
      expect(hit.p90, 0);
    });
  });

  group('QueryResult', () {
    test('fromJson creates correct result', () {
      final json = {
        'hits': [],
        'confidence_range': {'p10': 1.5, 'p50': 3.0, 'p90': 5.0},
        'outliers': [],
        'natural_response': 'Estimated 2-4 hours',
        'mode': 'cloud',
      };
      final result = QueryResult.fromJson(json);
      expect(result.hits, isEmpty);
      expect(result.p10, 1.5);
      expect(result.p50, 3.0);
      expect(result.p90, 5.0);
      expect(result.naturalResponse, 'Estimated 2-4 hours');
      expect(result.mode, 'cloud');
    });

    test('fromJson defaults local mode when missing', () {
      final result = QueryResult.fromJson({
        'hits': [],
        'confidence_range': {'p10': 0, 'p50': 0, 'p90': 0},
      });
      expect(result.mode, 'local');
    });
  });
}
