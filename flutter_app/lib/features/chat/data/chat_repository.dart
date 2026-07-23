import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import '../../../shared/services/api_client.dart';
import '../../../core/services/local_db.dart';
import '../domain/chat_models.dart';

/// Prefix markers used to multiplex out-of-band events (session id, status)
/// onto the plain-text stream the UI consumes. Length-derived stripping
/// (`prefix.length`) avoids the classic off-by-one from a hardcoded magic
/// number.
const String sessionIdEventPrefix = '__session_id:';
const String statusEventPrefix = '__status:';

class ChatRepository {
  final Dio _dio = ApiClient().dio;
  CancelToken? _cancelToken;
  static const String _sessionIdPrefix = sessionIdEventPrefix;
  static const String _statusPrefix = statusEventPrefix;

  /// Server-side sessions (may be empty on ephemeral Render).
  Future<List<ChatSession>> getSessions() async {
    try {
      final response = await _dio.get('/api/chat/sessions');
      final list = response.data['sessions'] as List<dynamic>? ?? [];
      return list
          .map((s) => ChatSession.fromJson(s as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<ChatSession> getSession(String id) async {
    final response = await _dio.get('/api/chat/sessions/$id');
    return ChatSession.fromJson(response.data);
  }

  Future<void> deleteSession(String id) async {
    try {
      await _dio.delete('/api/chat/sessions/$id');
    } catch (_) {}
    await LocalDb().deleteSession(id);
  }

  /// Send message with optional client-provided history for stateless backends.
  Stream<String> sendMessage(
    String message, {
    String? sessionId,
    String lang = 'ar',
    String? history,
  }) {
    _cancelToken?.cancel();
    _cancelToken = CancelToken();

    final controller = StreamController<String>();
    final params = <String, dynamic>{
      'message': message,
      'lang': lang,
    };
    if (sessionId != null) params['session_id'] = sessionId;
    if (history != null && history.isNotEmpty) params['history'] = history;

    () async {
      try {
        final response = await _dio.post(
          '/api/chat/send',
          queryParameters: params,
          options: Options(responseType: ResponseType.stream),
          cancelToken: _cancelToken,
        );

        final stream = response.data.stream as Stream<List<int>>;
        String buffer = '';
        await for (final chunk in stream) {
          buffer += utf8.decode(chunk);
          while (buffer.contains('\n\n') || buffer.contains('\n')) {
            final newline = buffer.contains('\n\n') ? '\n\n' : '\n';
            final idx = buffer.indexOf(newline);
            final line = buffer.substring(0, idx);
            buffer = buffer.substring(idx + newline.length);

            if (line.startsWith('data: ')) {
              final data = line.substring(6);
              if (data == '{"done":true}' || data.contains('"done":true')) {
                continue;
              }
              try {
                final json = jsonDecode(data) as Map<String, dynamic>;
                if (json.containsKey('session_id')) {
                  controller.add('$_sessionIdPrefix${json['session_id']}');
                } else if (json.containsKey('status')) {
                  controller.add('$_statusPrefix${json['status']}');
                } else if (json.containsKey('text')) {
                  controller.add(json['text'] as String);
                }
              } catch (_) {}
            }
          }
        }
      } catch (e) {
        if (e is DioException && e.type == DioExceptionType.cancel) return;
        controller.addError(e);
      } finally {
        await controller.close();
      }
    }();

    return controller.stream;
  }

  void cancelStream() => _cancelToken?.cancel();
  void dispose() => _cancelToken?.cancel();

  /// Fire-and-forget ping to wake a sleeping Render free-tier instance as
  /// soon as the chat screen opens, so the cold start overlaps with the
  /// user typing their first message instead of happening after they send it.
  Future<void> warmUp() async {
    try {
      await _dio.get('/api/health', options: Options(receiveTimeout: const Duration(seconds: 60)));
    } catch (_) {}
  }
}
