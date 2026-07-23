import 'package:dio/dio.dart';
import '../../../shared/services/api_client.dart';
import '../domain/dictionary_term.dart';

class TermRepository {
  final Dio _dio = ApiClient().dio;

  Future<List<DictionaryTerm>> list({String? search, String? category}) async {
    final params = <String, dynamic>{};
    if (search != null) params['search'] = search;
    if (category != null) params['category'] = category;
    final response = await _dio.get('/api/dictionary', queryParameters: params);
    final list = response.data['terms'] as List<dynamic>? ?? [];
    return list.map((t) => DictionaryTerm.fromJson(t as Map<String, dynamic>)).toList();
  }

  Future<DictionaryTerm> create(DictionaryTerm term) async {
    final response = await _dio.post('/api/dictionary', data: term.toCreateJson());
    return DictionaryTerm.fromJson(response.data);
  }

  Future<DictionaryTerm> update(String id, DictionaryTerm term) async {
    final response = await _dio.put('/api/dictionary/$id', data: term.toUpdateJson());
    return DictionaryTerm.fromJson(response.data);
  }

  Future<void> delete(String id) async {
    await _dio.delete('/api/dictionary/$id');
  }
}
