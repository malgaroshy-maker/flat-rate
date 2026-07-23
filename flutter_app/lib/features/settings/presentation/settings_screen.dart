import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:developer' as dev;
import '../../../core/theme/app_colors.dart';
import '../../../l10n/app_localizations.dart';
import '../../../shared/services/api_client.dart';
import '../../../core/constants/api_config.dart';
import '../../../app.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  String _mode = 'loading';
  String _embeddingModel = '';
  String _llmBackend = '';
  bool _forceLocal = false;

  @override
  void initState() {
    super.initState();
    _loadHealth();
  }

  Future<void> _loadHealth() async {
    try {
      final response = await ApiClient().dio.get('/api/health');
      setState(() {
        _mode = response.data['mode'] ?? 'unknown';
        _embeddingModel = response.data['embedding_model'] ?? '';
        _llmBackend = response.data['local_llm_backend'] ?? '';
        _forceLocal = response.data['force_local'] ?? false;
      });
    } catch (e) {
      dev.log('Health check failed', error: e);
      setState(() => _mode = 'offline');
    }
  }

  Future<void> _toggleMode(bool local) async {
    try {
      await ApiClient().dio.post('/api/settings/mode', data: {'force_local': local});
      await _loadHealth();
    } catch (e) {
      dev.log('Mode toggle failed', error: e);
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentLocale = ref.watch(localeProvider);
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.settingsTab)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(l10n.languageLabel, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                  const SizedBox(height: 12),
                  SegmentedButton<Locale>(
                    segments: const [
                      ButtonSegment(value: Locale('ar'), label: Text('العربية')),
                      ButtonSegment(value: Locale('en'), label: Text('English')),
                    ],
                    selected: {currentLocale},
                    onSelectionChanged: (locales) {
                      ref.read(localeProvider.notifier).state = locales.first;
                    },
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(l10n.themeLabel, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                  const SizedBox(height: 12),
                  SegmentedButton<ThemeMode>(
                    segments: [
                      ButtonSegment(value: ThemeMode.light, label: Text(l10n.themeLight)),
                      ButtonSegment(value: ThemeMode.dark, label: Text(l10n.themeDark)),
                      ButtonSegment(value: ThemeMode.system, label: Text(l10n.themeSystem)),
                    ],
                    selected: {ref.watch(themeModeProvider)},
                    onSelectionChanged: (modes) {
                      ref.read(themeModeProvider.notifier).state = modes.first;
                    },
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(l10n.modeLabel, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: ChoiceChip(
                          label: Text(l10n.cloudMode),
                          selected: !_forceLocal,
                          onSelected: (_) => _toggleMode(false),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: ChoiceChip(
                          label: Text(l10n.localMode),
                          selected: _forceLocal,
                          onSelected: (_) => _toggleMode(true),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(l10n.systemInfo, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                  const SizedBox(height: 12),
                  _infoRow(l10n.modeLabel, _mode == 'offline' ? l10n.offline : _mode),
                  _infoRow(l10n.backendUrl, ApiConfig.baseUrl),
                  _infoRow(l10n.llmBackend, _llmBackend),
                  _infoRow(l10n.embeddingModel, _embeddingModel),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 13, color: AppColors.slate500)),
          Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
