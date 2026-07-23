import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:labor_app/l10n/app_localizations.dart';
import 'package:labor_app/shared/widgets/common_widgets.dart';

/// ErrorView reads AppLocalizations.of(context) for the retry button label,
/// so tests need the same localization setup as the real app.
Widget _wrap(Widget child) {
  return MaterialApp(
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    home: Scaffold(body: child),
  );
}

void main() {
  group('LoadingIndicator', () {
    testWidgets('renders CircularProgressIndicator', (tester) async {
      await tester.pumpWidget(_wrap(const LoadingIndicator()));
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });
  });

  group('ErrorView', () {
    testWidgets('shows error message and retry button', (tester) async {
      var retried = false;
      await tester.pumpWidget(_wrap(
        ErrorView(
          message: 'Something went wrong',
          onRetry: () => retried = true,
        ),
      ));
      expect(find.text('Something went wrong'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);

      await tester.tap(find.text('Retry'));
      expect(retried, isTrue);
    });

    testWidgets('shows no retry button when onRetry is null', (tester) async {
      await tester.pumpWidget(_wrap(const ErrorView(message: 'Error')));
      expect(find.text('Retry'), findsNothing);
    });
  });

  group('EmptyView', () {
    testWidgets('shows message and default icon', (tester) async {
      await tester.pumpWidget(_wrap(const EmptyView(message: 'Nothing here')));
      expect(find.text('Nothing here'), findsOneWidget);
    });

    testWidgets('shows custom icon', (tester) async {
      await tester.pumpWidget(_wrap(
        const EmptyView(message: 'Empty', icon: Icons.search_off),
      ));
      expect(find.byIcon(Icons.search_off), findsOneWidget);
    });
  });
}
