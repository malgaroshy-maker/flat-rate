import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/search_repository.dart';
import '../domain/query_result.dart';

final searchRepositoryProvider = Provider<SearchRepository>((ref) => SearchRepository());

/// True when the last successful search result came from the offline
/// cache rather than a live network response.
final searchFromCacheProvider = StateProvider<bool>((ref) => false);

final searchProvider = FutureProvider.family<QueryResult, String>((ref, query) async {
  final repo = ref.watch(searchRepositoryProvider);
  try {
    final result = await repo.query(query);
    ref.read(searchFromCacheProvider.notifier).state = false;
    return result;
  } catch (e) {
    final cached = await repo.queryFromCache(query);
    if (cached != null) {
      ref.read(searchFromCacheProvider.notifier).state = true;
      return cached;
    }
    rethrow;
  }
});

final pdfExportProvider = FutureProvider.family<List<int>, String>((ref, query) async {
  final repo = ref.watch(searchRepositoryProvider);
  final response = await repo.exportPdf(query);
  return List<int>.from(response.data);
});
