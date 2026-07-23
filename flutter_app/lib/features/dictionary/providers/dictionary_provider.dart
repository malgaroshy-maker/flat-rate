import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/services/local_db.dart';
import '../data/term_repository.dart';
import '../domain/dictionary_term.dart';

final termRepositoryProvider = Provider<TermRepository>((ref) => TermRepository());

/// True when the currently displayed terms came from the offline cache
/// (device has no network, or the request failed) rather than the API.
final dictionaryFromCacheProvider = StateProvider<bool>((ref) => false);

final termsProvider = FutureProvider.family<List<DictionaryTerm>, String>((ref, search) {
  return ref.watch(termRepositoryProvider).list(search: search.isNotEmpty ? search : null);
});

class TermNotifier extends Notifier<List<DictionaryTerm>> {
  @override
  List<DictionaryTerm> build() => [];

  Future<void> load({String search = ''}) async {
    final repo = ref.watch(termRepositoryProvider);
    try {
      final terms = await repo.list(search: search.isNotEmpty ? search : null);
      state = terms;
      ref.read(dictionaryFromCacheProvider.notifier).state = false;
      // Fire-and-forget: mirror the fresh list into the offline cache.
      LocalDb().cacheDictionaryTerms(terms
          .map((t) => {
                'id': t.id,
                'arabic_term': t.arabicTerm,
                'standard_category': t.standardCategory,
                'english_term': t.englishTerm,
                'fusha_meaning': t.fushaMeaning,
                'notes': t.notes,
              })
          .toList());
    } catch (_) {
      final cached = await LocalDb().getCachedDictionaryTerms(search: search);
      state = cached
          .map((row) => DictionaryTerm(
                id: row['id'] as String,
                arabicTerm: row['arabic_term'] as String,
                standardCategory: row['standard_category'] as String,
                englishTerm: (row['english_term'] as String?) ?? '',
                fushaMeaning: (row['fusha_meaning'] as String?) ?? '',
                notes: (row['notes'] as String?) ?? '',
              ))
          .toList();
      ref.read(dictionaryFromCacheProvider.notifier).state = true;
    }
  }

  Future<void> create(DictionaryTerm term) async {
    final repo = ref.watch(termRepositoryProvider);
    await repo.create(term);
    await load();
  }

  Future<void> update(String id, DictionaryTerm term) async {
    final repo = ref.watch(termRepositoryProvider);
    await repo.update(id, term);
    await load();
  }

  Future<void> delete(String id) async {
    final repo = ref.watch(termRepositoryProvider);
    await repo.delete(id);
    await load();
  }
}

final termListProvider = NotifierProvider<TermNotifier, List<DictionaryTerm>>(TermNotifier.new);
