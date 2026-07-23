import 'dart:convert';
import 'package:dio/dio.dart';
import '../../../shared/services/api_client.dart';
import '../../../core/services/local_db.dart';
import '../domain/query_result.dart';

class SearchRepository {
  final Dio _dio = ApiClient().dio;

  String cacheKey(String query, int n, String? department) =>
      '${query.trim().toLowerCase()}|$n|${department ?? ''}';

  /// Network-only fetch; caches the result on success. Throws on failure —
  /// callers fall back to [queryFromCache].
  Future<QueryResult> query(String query, {int n = 5, String? department}) async {
    final params = <String, dynamic>{'q': query, 'n': n};
    if (department != null) params['department'] = department;
    final response = await _dio.post('/api/query', queryParameters: params);
    await LocalDb().cacheSearchResult(cacheKey(query, n, department), jsonEncode(response.data));
    return QueryResult.fromJson(response.data);
  }

  Future<QueryResult?> queryFromCache(String query, {int n = 5, String? department}) async {
    final cached = await LocalDb().getCachedSearchResult(cacheKey(query, n, department));
    if (cached == null) return null;
    return QueryResult.fromJson(jsonDecode(cached) as Map<String, dynamic>);
  }

  Future<Response> exportPdf(String query, {String lang = 'ar'}) async {
    return _dio.post('/api/export/pdf', queryParameters: {'q': query, 'lang': lang},
        options: Options(responseType: ResponseType.bytes));
  }
}
