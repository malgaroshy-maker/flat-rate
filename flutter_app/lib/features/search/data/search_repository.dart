import 'package:dio/dio.dart';
import '../../../shared/services/api_client.dart';
import '../domain/query_result.dart';

class SearchRepository {
  final Dio _dio = ApiClient().dio;

  Future<QueryResult> query(String query, {int n = 5, String? department}) async {
    final params = <String, dynamic>{'q': query, 'n': n};
    if (department != null) params['department'] = department;
    final response = await _dio.post('/api/query', queryParameters: params);
    return QueryResult.fromJson(response.data);
  }

  Future<Response> exportPdf(String query, {String lang = 'ar'}) async {
    return _dio.post('/api/export/pdf', queryParameters: {'q': query, 'lang': lang},
        options: Options(responseType: ResponseType.bytes));
  }
}
