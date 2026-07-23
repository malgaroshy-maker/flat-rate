import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../l10n/app_localizations.dart';
import '../../../shared/widgets/common_widgets.dart';
import '../../dictionary/providers/dictionary_provider.dart';
import '../../dictionary/domain/dictionary_term.dart';

class DictionaryScreen extends ConsumerStatefulWidget {
  const DictionaryScreen({super.key});

  @override
  ConsumerState<DictionaryScreen> createState() => _DictionaryScreenState();
}

class _DictionaryScreenState extends ConsumerState<DictionaryScreen> {
  final _searchController = TextEditingController();
  String _search = '';
  Timer? _debounce;

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(termListProvider.notifier).load());
  }

  @override
  void dispose() {
    _searchController.dispose();
    _debounce?.cancel();
    super.dispose();
  }

  void _showForm({DictionaryTerm? term}) {
    final l10n = AppLocalizations.of(context);
    final arabic = TextEditingController(text: term?.arabicTerm ?? '');
    final category = TextEditingController(text: term?.standardCategory ?? '');
    final english = TextEditingController(text: term?.englishTerm ?? '');
    final fusha = TextEditingController(text: term?.fushaMeaning ?? '');
    final notes = TextEditingController(text: term?.notes ?? '');

    void disposeAll() {
      arabic.dispose();
      category.dispose();
      english.dispose();
      fusha.dispose();
      notes.dispose();
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
            Text(term == null ? l10n.addTerm : l10n.editTerm, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
            const SizedBox(height: 16),
            TextField(controller: arabic, decoration: InputDecoration(labelText: l10n.arabicTerm)),
            const SizedBox(height: 8),
            TextField(controller: category, decoration: InputDecoration(labelText: l10n.category)),
            const SizedBox(height: 8),
            TextField(controller: english, decoration: InputDecoration(labelText: l10n.englishTerm)),
            const SizedBox(height: 8),
            TextField(controller: fusha, decoration: InputDecoration(labelText: l10n.fushaMeaning)),
            const SizedBox(height: 8),
            TextField(controller: notes, decoration: InputDecoration(labelText: l10n.notesOptional)),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () async {
                final t = DictionaryTerm(
                  id: term?.id ?? '',
                  arabicTerm: arabic.text.trim(),
                  standardCategory: category.text.trim(),
                  englishTerm: english.text.trim(),
                  fushaMeaning: fusha.text.trim(),
                  notes: notes.text.trim(),
                );
                if (t.arabicTerm.isEmpty || t.standardCategory.isEmpty) return;
                if (term == null) {
                  await ref.read(termListProvider.notifier).create(t);
                } else {
                  await ref.read(termListProvider.notifier).update(term.id, t);
                }
                disposeAll();
                if (ctx.mounted) Navigator.pop(ctx);
              },
              child: Text(term == null ? l10n.add : l10n.save),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    ).whenComplete(disposeAll);
  }

  @override
  Widget build(BuildContext context) {
    final terms = ref.watch(termListProvider);
    final fromCache = ref.watch(dictionaryFromCacheProvider);
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.dictionaryTab)),
      body: Column(
        children: [
          if (fromCache) const OfflineBanner(),
          Padding(
            padding: const EdgeInsets.all(12),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: l10n.searchDictionary,
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _search.isNotEmpty
                    ? IconButton(icon: const Icon(Icons.clear), onPressed: () {
                        _searchController.clear();
                        setState(() => _search = '');
                        ref.read(termListProvider.notifier).load();
                      })
                    : null,
              ),
              onChanged: (v) {
                setState(() => _search = v);
                _debounce?.cancel();
                _debounce = Timer(const Duration(milliseconds: 300), () {
                  ref.read(termListProvider.notifier).load(search: v);
                });
              },
            ),
          ),
          Expanded(
            child: terms.isEmpty
                ? EmptyView(message: l10n.noTermsFound, icon: Icons.book_outlined)
                : RefreshIndicator(
                    onRefresh: () => ref.read(termListProvider.notifier).load(search: _search),
                    child: ListView.separated(
                      itemCount: terms.length,
                      separatorBuilder: (_, __) => const Divider(height: 1, indent: 16),
                      itemBuilder: (_, i) {
                        final t = terms[i];
                        final subtitleParts = [
                          t.standardCategory,
                          if (t.fushaMeaning.isNotEmpty) t.fushaMeaning,
                          if (t.englishTerm.isNotEmpty) t.englishTerm,
                        ];
                        return ListTile(
                          title: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(t.arabicTerm, style: const TextStyle(fontWeight: FontWeight.w500)),
                              if (t.notes.isNotEmpty) ...[
                                const SizedBox(width: 6),
                                Tooltip(
                                  message: t.notes,
                                  child: const Icon(Icons.help_outline, size: 14),
                                ),
                              ],
                            ],
                          ),
                          subtitle: Text(subtitleParts.join(' · '),
                              maxLines: 2, overflow: TextOverflow.ellipsis),
                          isThreeLine: t.fushaMeaning.isNotEmpty && t.englishTerm.isNotEmpty,
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(
                                icon: const Icon(Icons.edit, size: 18),
                                onPressed: () => _showForm(term: t),
                              ),
                              IconButton(
                                icon: const Icon(Icons.delete, size: 18),
                                onPressed: () =>
                                    ref.read(termListProvider.notifier).delete(t.id),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showForm(),
        child: const Icon(Icons.add),
      ),
    );
  }
}
