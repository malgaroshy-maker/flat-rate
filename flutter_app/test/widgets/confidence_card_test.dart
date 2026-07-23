import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:labor_app/features/search/presentation/widgets/confidence_card.dart';
import 'package:labor_app/features/search/domain/query_result.dart';

void main() {
  final hits = [
    QueryHit(
      id: 'h1', model: 'HD45', code: '2000',
      departments: 'Diesel', franchises: 'Hyundai',
      qtyCount: 60, qtyMedian: 2.5, qtyMean: 3.0,
      priceMean: 45.0, similarity: 0.95,
      p10: 1.0, p25: 1.5, p50: 2.5, p75: 3.5, p90: 4.0,
    ),
  ];

  testWidgets('renders confidence range and median', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: ConfidenceCard(p10: 1.0, p50: 2.5, p90: 4.0, hits: []),
        ),
      ),
    );
    expect(find.textContaining('1'), findsWidgets);
    expect(find.textContaining('4'), findsWidgets);
    expect(find.textContaining('2.5'), findsOneWidget);
  });

  testWidgets('shows high confidence with many records', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ConfidenceCard(p10: 1.0, p50: 2.5, p90: 4.0, hits: hits),
        ),
      ),
    );
    expect(find.text('High'), findsOneWidget);
  });

  testWidgets('renders natural response when provided', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ConfidenceCard(
            p10: 1.0, p50: 2.5, p90: 4.0,
            hits: [], naturalResponse: 'Expected 2-3 hours',
          ),
        ),
      ),
    );
    expect(find.text('Expected 2-3 hours'), findsOneWidget);
  });
}
