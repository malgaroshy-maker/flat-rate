import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/search_repository.dart';
import '../domain/query_result.dart';

final searchRepositoryProvider = Provider<SearchRepository>((ref) => SearchRepository());

final searchProvider = FutureProvider.family<QueryResult, String>((ref, query) async {
  final repo = ref.watch(searchRepositoryProvider);
  return repo.query(query);
});

final pdfExportProvider = FutureProvider.family<List<int>, String>((ref, query) async {
  final repo = ref.watch(searchRepositoryProvider);
  final response = await repo.exportPdf(query);
  return List<int>.from(response.data);
});
