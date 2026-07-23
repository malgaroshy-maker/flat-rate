import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/services/connectivity_service.dart';
import 'core/theme/app_theme.dart';
import 'features/chat/providers/chat_provider.dart';
import 'l10n/app_localizations.dart';
import 'routes/app_router.dart';

final localeProvider = StateProvider<Locale>((ref) => const Locale('ar'));
final themeModeProvider = StateProvider<ThemeMode>((ref) => ThemeMode.system);

class LaborApp extends ConsumerWidget {
  const LaborApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    final locale = ref.watch(localeProvider);
    final themeMode = ref.watch(themeModeProvider);

    // Whenever connectivity comes back (including the initial check), try
    // sending anything queued in the offline chat outbox.
    ref.listen(connectivityProvider, (previous, next) {
      if (next.value == true) {
        ref.read(chatProvider.notifier).flushOutbox();
      }
    });

    return MaterialApp.router(
      title: 'Labor Cost Estimator',
      routerConfig: router,
      theme: AppTheme.light(languageCode: locale.languageCode),
      darkTheme: AppTheme.dark(languageCode: locale.languageCode),
      themeMode: themeMode,
      debugShowCheckedModeBanner: false,
      locale: locale,
      supportedLocales: const [Locale('ar'), Locale('en')],
      localizationsDelegates: AppLocalizations.localizationsDelegates,
    );
  }
}
