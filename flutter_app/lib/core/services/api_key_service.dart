import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

const _keyStorageKey = 'user_gemini_api_key';

/// Stores the user's personal Gemini API key on-device (Android
/// Keystore-backed via flutter_secure_storage), used only as a fallback
/// when the app's shared key is out of quota or revoked — see
/// ChatRepository.sendMessage's retry-with-key-error handling.
class ApiKeyService {
  static const _storage = FlutterSecureStorage();

  Future<String?> getKey() async {
    final key = await _storage.read(key: _keyStorageKey);
    return (key == null || key.isEmpty) ? null : key;
  }

  Future<void> setKey(String key) async {
    await _storage.write(key: _keyStorageKey, value: key.trim());
  }

  Future<void> clearKey() async {
    await _storage.delete(key: _keyStorageKey);
  }
}

final apiKeyServiceProvider = Provider<ApiKeyService>((ref) => ApiKeyService());

/// Whether a personal key is currently saved — watched by the Settings
/// screen and refreshed after save/clear.
final hasPersonalApiKeyProvider = FutureProvider.autoDispose<bool>((ref) async {
  final key = await ref.watch(apiKeyServiceProvider).getKey();
  return key != null;
});
