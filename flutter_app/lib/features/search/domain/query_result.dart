class QueryHit {
  final String id, model, code, departments, franchises;
  final int qtyCount;
  final double qtyMedian, qtyMean, priceMean, similarity;
  final double p10, p25, p50, p75, p90;
  final bool compound;
  final int compoundMaxOps;
  final double compoundPct, weightedQtyP50, weightedQtyP90;

  const QueryHit({
    required this.id, required this.model, required this.code,
    required this.departments, required this.franchises,
    required this.qtyCount, required this.qtyMedian, required this.qtyMean,
    required this.priceMean, required this.similarity,
    required this.p10, required this.p25, required this.p50,
    required this.p75, required this.p90,
    this.compound = false, this.compoundMaxOps = 0,
    this.compoundPct = 0, this.weightedQtyP50 = 0, this.weightedQtyP90 = 0,
  });

  factory QueryHit.fromJson(Map<String, dynamic> json) {
    final cr = json['confidence_range'] as Map<String, dynamic>? ?? {};
    return QueryHit(
      id: json['id'] ?? '', model: json['model'] ?? '', code: json['code'] ?? '',
      departments: json['departments'] ?? '', franchises: json['franchises'] ?? '',
      qtyCount: (json['qty_count'] ?? 0).toInt(),
      qtyMedian: (json['qty_median'] ?? 0).toDouble(),
      qtyMean: (json['qty_mean'] ?? 0).toDouble(),
      priceMean: (json['price_mean'] ?? 0).toDouble(),
      similarity: (json['similarity'] ?? 0).toDouble(),
      p10: (cr['p10'] ?? 0).toDouble(), p25: (cr['p25'] ?? 0).toDouble(),
      p50: (cr['median'] ?? 0).toDouble(), p75: (cr['p75'] ?? 0).toDouble(),
      p90: (cr['p90'] ?? 0).toDouble(),
      compound: json['compound'] == true,
      compoundMaxOps: (json['compound_max_ops'] ?? 0).toInt(),
      compoundPct: (json['compound_pct'] ?? 0).toDouble(),
      weightedQtyP50: (json['weighted_qty_p50'] ?? 0).toDouble(),
      weightedQtyP90: (json['weighted_qty_p90'] ?? 0).toDouble(),
    );
  }
}

class MatchedTerm {
  final String arabicTerm, fushaMeaning, englishTerm, notes;

  const MatchedTerm({
    required this.arabicTerm, this.fushaMeaning = '', this.englishTerm = '', this.notes = '',
  });

  factory MatchedTerm.fromJson(Map<String, dynamic> json) {
    return MatchedTerm(
      arabicTerm: json['arabic_term'] ?? '',
      fushaMeaning: json['fusha_meaning'] ?? '',
      englishTerm: json['english_term'] ?? '',
      notes: json['notes'] ?? '',
    );
  }
}

class QueryResult {
  final List<QueryHit> hits;
  final double p10, p50, p90;
  final List<Map<String, dynamic>> outliers;
  final String? naturalResponse;
  final String mode;
  final List<MatchedTerm> matchedTerms;

  const QueryResult({
    required this.hits, required this.p10, required this.p50, required this.p90,
    this.outliers = const [], this.naturalResponse, this.mode = 'local',
    this.matchedTerms = const [],
  });

  factory QueryResult.fromJson(Map<String, dynamic> json) {
    final cr = json['confidence_range'] as Map<String, dynamic>? ?? {};
    return QueryResult(
      hits: ((json['hits'] ?? []) as List).map((h) => QueryHit.fromJson(h)).toList(),
      p10: (cr['p10'] ?? 0).toDouble(), p50: (cr['p50'] ?? 0).toDouble(),
      p90: (cr['p90'] ?? 0).toDouble(),
      outliers: List<Map<String, dynamic>>.from(json['outliers'] ?? []),
      naturalResponse: json['natural_response'],
      mode: json['mode'] ?? 'local',
      matchedTerms: ((json['matched_terms'] ?? []) as List)
          .map((t) => MatchedTerm.fromJson(t as Map<String, dynamic>))
          .toList(),
    );
  }
}
