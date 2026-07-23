import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../l10n/app_localizations.dart';
import '../../../shared/widgets/common_widgets.dart';
import '../../pending/providers/pending_provider.dart';
import '../../pending/domain/pending_item.dart';

class PendingScreen extends ConsumerStatefulWidget {
  const PendingScreen({super.key});

  @override
  ConsumerState<PendingScreen> createState() => _PendingScreenState();
}

class _PendingScreenState extends ConsumerState<PendingScreen> {
  final _selectedIds = <String>{};
  final _categoryController = TextEditingController();

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(pendingProvider.notifier).load());
  }

  @override
  void dispose() {
    _categoryController.dispose();
    super.dispose();
  }

  void _resolveOne(PendingItem item) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    final arabic = TextEditingController(text: item.termText);
    final category = TextEditingController();
    final english = TextEditingController();

    void disposeAll() {
      arabic.dispose();
      category.dispose();
      english.dispose();
    }

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(bottom: MediaQuery.of(ctx).viewInsets.bottom, left: 16, right: 16, top: 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(l10n.resolveTerm, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
            Text('"${item.termText}"', style: TextStyle(color: theme.colorScheme.onSurfaceVariant, fontSize: 13)),
            const SizedBox(height: 12),
            TextField(controller: arabic, decoration: InputDecoration(labelText: l10n.arabicTerm)),
            const SizedBox(height: 8),
            TextField(controller: category, decoration: InputDecoration(labelText: l10n.category)),
            const SizedBox(height: 8),
            TextField(controller: english, decoration: InputDecoration(labelText: l10n.englishTerm)),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () async {
                if (category.text.trim().isEmpty) return;
                await ref.read(pendingProvider.notifier).resolve(
                  item.id,
                  ResolvePayload(arabicTerm: arabic.text.trim(), standardCategory: category.text.trim(), englishTerm: english.text.trim()),
                );
                disposeAll();
                if (ctx.mounted) Navigator.pop(ctx);
              },
              child: Text(l10n.save),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    ).whenComplete(disposeAll);
  }

  void _batchResolve() {
    final l10n = AppLocalizations.of(context);
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(bottom: MediaQuery.of(ctx).viewInsets.bottom, left: 16, right: 16, top: 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(l10n.resolveCount(_selectedIds.length), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
            const SizedBox(height: 12),
            TextField(
              controller: _categoryController,
              decoration: InputDecoration(labelText: l10n.categoryForAll),
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () async {
                if (_categoryController.text.trim().isEmpty) return;
                final items = ref.read(pendingProvider).valueOrNull ?? [];
                final batch = <String, ResolvePayload>{};
                for (final id in _selectedIds) {
                  final item = items.firstWhere((p) => p.id == id, orElse: () => items.first);
                  batch[id] = ResolvePayload(arabicTerm: item.termText, standardCategory: _categoryController.text.trim());
                }
                await ref.read(pendingProvider.notifier).batchResolve(batch);
                _selectedIds.clear();
                _categoryController.clear();
                if (ctx.mounted) Navigator.pop(ctx);
              },
              child: Text(l10n.resolveAll),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final pendingState = ref.watch(pendingProvider);
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.pendingTab)),
      body: pendingState.when(
        loading: () => const LoadingIndicator(),
        error: (e, _) => ErrorView(message: '$e', onRetry: () => ref.read(pendingProvider.notifier).load()),
        data: (items) {
          if (items.isEmpty) {
            return EmptyView(message: l10n.noPendingTerms, icon: Icons.check_circle_outline);
          }
          return RefreshIndicator(
            onRefresh: () => ref.read(pendingProvider.notifier).load(),
            child: ListView.builder(
              itemCount: items.length,
              itemBuilder: (_, i) {
                final item = items[i];
                final selected = _selectedIds.contains(item.id);
                return Card(
                  color: selected
                      ? theme.colorScheme.primaryContainer
                      : theme.colorScheme.surfaceContainerHigh,
                  child: ListTile(
                    leading: Checkbox(
                      value: selected,
                      onChanged: (_) {
                        setState(() {
                          if (selected) {
                            _selectedIds.remove(item.id);
                          } else {
                            _selectedIds.add(item.id);
                          }
                        });
                      },
                    ),
                    title: Text(item.termText, style: const TextStyle(fontWeight: FontWeight.w600)),
                    subtitle: Text('${l10n.from}: ${item.queryText}', maxLines: 1, overflow: TextOverflow.ellipsis),
                    trailing: IconButton(
                      icon: const Icon(Icons.check_circle_outline),
                      onPressed: () => _resolveOne(item),
                    ),
                  ),
                );
              },
            ),
          );
        },
      ),
      bottomSheet: _selectedIds.isNotEmpty
          ? Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: theme.colorScheme.surface,
                border: Border(top: BorderSide(color: theme.colorScheme.outlineVariant)),
              ),
              child: Row(
                children: [
                  Text(l10n.selectedCount(_selectedIds.length),
                      style: const TextStyle(fontWeight: FontWeight.w600)),
                  const Spacer(),
                  FilledButton(onPressed: _batchResolve, child: Text(l10n.resolveAll)),
                ],
              ),
            )
          : null,
    );
  }
}
