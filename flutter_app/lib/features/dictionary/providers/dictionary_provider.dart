import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/term_repository.dart';
import '../domain/dictionary_term.dart';

final termRepositoryProvider = Provider<TermRepository>((ref) => TermRepository());

final termsProvider = FutureProvider.family<List<DictionaryTerm>, String>((ref, search) {
  return ref.watch(termRepositoryProvider).list(search: search.isNotEmpty ? search : null);
});

class TermNotifier extends Notifier<List<DictionaryTerm>> {
  @override
  List<DictionaryTerm> build() => [];

  Future<void> load({String search = ''}) async {
    final repo = ref.watch(termRepositoryProvider);
    state = await repo.list(search: search.isNotEmpty ? search : null);
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
