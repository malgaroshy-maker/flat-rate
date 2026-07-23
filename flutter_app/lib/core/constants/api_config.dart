class ApiConfig {
  ApiConfig._();

  /// Backend URL — set via --dart-define=API_BASE_URL=http://... or fall back to localhost.
  ///
  /// Options:
  ///   flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000     — Android emulator
  ///   flutter run --dart-define=API_BASE_URL=http://192.168.X.X:8000   — Physical device
  ///   flutter run --dart-define=API_BASE_URL=https://xxx.onrender.com  — Render deployment
  ///
  static const String baseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'https://flat-rate.onrender.com');

  static const Duration connectTimeout = Duration(seconds: 10);
  static const Duration receiveTimeout = Duration(seconds: 60);
  static const Duration sendTimeout = Duration(seconds: 10);
}
