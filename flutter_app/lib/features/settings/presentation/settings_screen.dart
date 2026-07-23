import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'dart:developer' as dev;
import '../../../core/services/api_key_service.dart';
import '../../../core/theme/app_colors.dart';
import '../../../l10n/app_localizations.dart';
import '../../../shared/services/api_client.dart';
import '../../../core/constants/api_config.dart';
import '../../../app.dart';

final packageInfoProvider = FutureProvider<PackageInfo>((ref) => PackageInfo.fromPlatform());

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
  final _apiKeyController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadHealth();
  }

  @override
  void dispose() {
    _apiKeyController.dispose();
    super.dispose();
  }

  Future<void> _saveApiKey() async {
    final key = _apiKeyController.text.trim();
    if (key.isEmpty) return;
    await ref.read(apiKeyServiceProvider).setKey(key);
    _apiKeyController.clear();
    ref.invalidate(hasPersonalApiKeyProvider);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(AppLocalizations.of(context).personalApiKeySaved), duration: const Duration(seconds: 1)),
      );
    }
  }

  Future<void> _clearApiKey() async {
    await ref.read(apiKeyServiceProvider).clearKey();
    ref.invalidate(hasPersonalApiKeyProvider);
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
          _buildApiKeyCard(l10n),
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
          const SizedBox(height: 12),
          _buildAboutCard(l10n),
        ],
      ),
    );
  }

  Widget _buildAboutCard(AppLocalizations l10n) {
    final packageInfo = ref.watch(packageInfoProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(l10n.aboutTitle, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
            const SizedBox(height: 12),
            Text(l10n.aboutAppBody, style: const TextStyle(fontSize: 13, height: 1.5)),
            const SizedBox(height: 12),
            _infoRow(
              l10n.appVersionLabel,
              packageInfo.when(
                data: (info) => '${info.version}+${info.buildNumber}',
                loading: () => '…',
                error: (_, __) => '—',
              ),
            ),
            const Divider(height: 24),
            Text(l10n.developedByLabel, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
            const SizedBox(height: 4),
            const Text('Mahamed Algaroshy — محمد الجروشي',
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
            const SizedBox(height: 4),
            Text(l10n.developerBio, style: const TextStyle(fontSize: 12, color: AppColors.slate500, height: 1.5)),
          ],
        ),
      ),
    );
  }

  Widget _buildApiKeyCard(AppLocalizations l10n) {
    final hasKeyAsync = ref.watch(hasPersonalApiKeyProvider);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(l10n.personalApiKeyLabel, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
            const SizedBox(height: 4),
            Text(l10n.personalApiKeyHint, style: const TextStyle(fontSize: 12, color: AppColors.slate500)),
            const SizedBox(height: 12),
            _infoRow(
              l10n.personalApiKeyStatus,
              hasKeyAsync.when(
                data: (has) => has ? l10n.personalApiKeyPresent : l10n.personalApiKeyAbsent,
                loading: () => '…',
                error: (_, __) => l10n.personalApiKeyAbsent,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _apiKeyController,
                    obscureText: true,
                    decoration: InputDecoration(
                      isDense: true,
                      hintText: 'AIza...',
                      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                FilledButton(onPressed: _saveApiKey, child: Text(l10n.save)),
              ],
            ),
            const SizedBox(height: 4),
            Align(
              alignment: Alignment.centerLeft,
              child: TextButton(
                onPressed: () async {
                  await _clearApiKey();
                },
                child: Text(l10n.clear, style: const TextStyle(fontSize: 12)),
              ),
            ),
          ],
        ),
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
