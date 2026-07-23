import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:labor_app/features/search/presentation/widgets/hit_card.dart';
import 'package:labor_app/features/search/domain/query_result.dart';

void main() {
  final sampleHit = QueryHit(
    id: 'h1',
    model: 'HD45',
    code: '2000',
    departments: 'Diesel',
    franchises: 'Hyundai',
    qtyCount: 50,
    qtyMedian: 2.5,
    qtyMean: 3.0,
    priceMean: 45.0,
    similarity: 0.92,
    p10: 1.0,
    p25: 1.5,
    p50: 2.5,
    p75: 3.5,
    p90: 4.0,
  );

  testWidgets('renders model and hours', (tester) async {
    await tester.pumpWidget(
      MaterialApp(home: Scaffold(body: HitCard(hit: sampleHit))),
    );
    expect(find.text('HD45'), findsOneWidget);
    expect(find.text('2.5h'), findsOneWidget);
  });

  testWidgets('expands on tap to show details', (tester) async {
    await tester.pumpWidget(
      MaterialApp(home: Scaffold(body: HitCard(hit: sampleHit))),
    );
    // Before tap: details hidden
    expect(find.text('P10'), findsNothing);

    await tester.tap(find.byType(HitCard));
    await tester.pumpAndSettle();

    // After tap: details visible
    expect(find.text('P10'), findsOneWidget);
    expect(find.text('P50'), findsOneWidget);
    expect(find.text('P90'), findsOneWidget);
  });
}
