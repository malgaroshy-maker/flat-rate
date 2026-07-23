import 'package:dio/dio.dart';
import '../../../shared/services/api_client.dart';
import '../domain/pending_item.dart';

class PendingRepository {
  final Dio _dio = ApiClient().dio;

  Future<List<PendingItem>> list() async {
    final response = await _dio.get('/api/dictionary/pending');
    final list = response.data['pending'] as List<dynamic>? ?? [];
    return list.map((p) => PendingItem.fromJson(p as Map<String, dynamic>)).toList();
  }

  Future<void> resolve(String id, ResolvePayload payload) async {
    await _dio.post('/api/dictionary/pending/$id/resolve', data: payload.toJson());
  }
}
