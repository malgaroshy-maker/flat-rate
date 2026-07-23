import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../app.dart';
import '../l10n/app_localizations.dart';
import '../features/search/presentation/search_screen.dart';
import '../features/chat/presentation/chat_screen.dart';
import '../features/dictionary/presentation/dictionary_screen.dart';
import '../features/pending/presentation/pending_screen.dart';
import '../features/settings/presentation/settings_screen.dart';

final rootNavigatorKey = GlobalKey<NavigatorState>();
final shellNavigatorKey = GlobalKey<NavigatorState>();

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    navigatorKey: rootNavigatorKey,
    initialLocation: '/search',
    routes: [
      ShellRoute(
        navigatorKey: shellNavigatorKey,
        builder: (context, state, child) {
          return ScaffoldWithNavBar(body: child);
        },
        routes: [
          GoRoute(path: '/search', name: 'search', builder: (_, __) => const SearchScreen()),
          GoRoute(path: '/chat', name: 'chat', builder: (_, __) => const ChatScreen()),
          GoRoute(path: '/dictionary', name: 'dictionary', builder: (_, __) => const DictionaryScreen()),
          GoRoute(path: '/pending', name: 'pending', builder: (_, __) => const PendingScreen()),
          GoRoute(path: '/settings', name: 'settings', builder: (_, __) => const SettingsScreen()),
        ],
      ),
    ],
  );
});

class ScaffoldWithNavBar extends ConsumerWidget {
  final Widget body;
  const ScaffoldWithNavBar({super.key, required this.body});

  int _calculateSelectedIndex(BuildContext context) {
    final location = GoRouterState.of(context).uri.toString();
    if (location.startsWith('/chat')) return 1;
    if (location.startsWith('/dictionary')) return 2;
    if (location.startsWith('/pending')) return 3;
    if (location.startsWith('/settings')) return 4;
    return 0;
  }

  void _onTap(BuildContext context, int index) {
    switch (index) {
      case 0: context.go('/search');
      case 1: context.go('/chat');
      case 2: context.go('/dictionary');
      case 3: context.go('/pending');
      case 4: context.go('/settings');
      default: assert(false, 'Unknown tab index: $index');
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.watch(localeProvider);
    final l10n = AppLocalizations.of(context);
    final selectedIndex = _calculateSelectedIndex(context);

    return Scaffold(
      body: body,
      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex,
        onDestinationSelected: (index) => _onTap(context, index),
        destinations: [
          NavigationDestination(icon: const Icon(Icons.search), label: l10n.searchTab),
          NavigationDestination(icon: const Icon(Icons.chat), label: l10n.chatTab),
          NavigationDestination(icon: const Icon(Icons.book), label: l10n.dictionaryTab),
          NavigationDestination(icon: const Icon(Icons.inbox), label: l10n.pendingTab),
          NavigationDestination(icon: const Icon(Icons.settings), label: l10n.settingsTab),
        ],
      ),
    );
  }
}
