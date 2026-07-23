class PendingItem {
  final String id;
  final String termText;
  final String queryText;
  final String status;

  const PendingItem({
    required this.id, required this.termText,
    required this.queryText, this.status = 'pending',
  });

  factory PendingItem.fromJson(Map<String, dynamic> json) {
    return PendingItem(
      id: json['id'] ?? '',
      termText: json['term_text'] ?? '',
      queryText: json['query_text'] ?? '',
      status: json['status'] ?? 'pending',
    );
  }
}

class ResolvePayload {
  final String arabicTerm;
  final String standardCategory;
  final String englishTerm;

  const ResolvePayload({
    required this.arabicTerm, required this.standardCategory,
    this.englishTerm = '',
  });

  Map<String, dynamic> toJson() => {
    'arabic_term': arabicTerm,
    'standard_category': standardCategory,
    'english_term': englishTerm,
  };
}
