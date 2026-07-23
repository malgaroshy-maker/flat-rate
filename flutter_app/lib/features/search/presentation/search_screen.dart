import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../l10n/app_localizations.dart';
import '../../../shared/widgets/common_widgets.dart';
import '../../search/domain/query_result.dart';
import '../../search/providers/search_provider.dart';
import 'widgets/confidence_card.dart';
import 'widgets/hit_card.dart';

class SearchScreen extends ConsumerStatefulWidget {
  const SearchScreen({super.key});

  @override
  ConsumerState<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends ConsumerState<SearchScreen> {
  final _controller = TextEditingController();
  String _query = '';

  void _search() {
    final q = _controller.text.trim();
    if (q.isEmpty) return;
    setState(() => _query = q);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Scaffold(
      appBar: AppBar(title: Text(l10n.appTitle)),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: l10n.searchHint,
                      prefixIcon: const Icon(Icons.search),
                    ),
                    onSubmitted: (_) => _search(),
                  ),
                ),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: _search,
                  child: Text(l10n.searchButton),
                ),
              ],
            ),
          ),
          if (ref.watch(searchFromCacheProvider)) const OfflineBanner(),
          Expanded(child: _query.isEmpty ? EmptyView(message: l10n.enterQuery) : _buildResults()),
        ],
      ),
    );
  }

  Widget _buildResults() {
    final asyncResult = ref.watch(searchProvider(_query));
    return asyncResult.when(
      loading: () => const LoadingIndicator(),
      error: (err, _) => ErrorView(message: err.toString(), onRetry: () => ref.invalidate(searchProvider(_query))),
      data: (result) => _buildData(result),
    );
  }

  Widget _buildData(QueryResult result) {
    final l10n = AppLocalizations.of(context);
    if (result.hits.isEmpty) {
      return EmptyView(message: l10n.noResults, icon: Icons.search_off);
    }
    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      children: [
        if (result.matchedTerms.isNotEmpty) ...[
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: result.matchedTerms.map((t) {
              final desc = [t.fushaMeaning, t.englishTerm].where((s) => s.isNotEmpty).join(' / ');
              return Tooltip(
                message: desc.isEmpty ? t.arabicTerm : desc,
                child: Chip(
                  label: Text(t.arabicTerm, style: const TextStyle(fontSize: 12)),
                  visualDensity: VisualDensity.compact,
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 12),
        ],
        ConfidenceCard(p10: result.p10, p50: result.p50, p90: result.p90,
            hits: result.hits, naturalResponse: result.naturalResponse),
        const SizedBox(height: 16),
        ...result.hits.map((h) => Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: HitCard(hit: h),
        )),
        const SizedBox(height: 80),
      ],
    );
  }
}
