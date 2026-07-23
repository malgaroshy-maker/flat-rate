class DictionaryTerm {
  final String id;
  final String arabicTerm;
  final String standardCategory;
  final String englishTerm;
  final String fushaMeaning;
  final String notes;

  const DictionaryTerm({
    required this.id, required this.arabicTerm,
    required this.standardCategory, this.englishTerm = '',
    this.fushaMeaning = '', this.notes = '',
  });

  factory DictionaryTerm.fromJson(Map<String, dynamic> json) {
    return DictionaryTerm(
      id: json['id'] ?? '',
      arabicTerm: json['arabic_term'] ?? '',
      standardCategory: json['standard_category'] ?? '',
      englishTerm: json['english_term'] ?? '',
      fushaMeaning: json['fusha_meaning'] ?? '',
      notes: json['notes'] ?? '',
    );
  }

  Map<String, dynamic> toCreateJson() => {
    'arabic_term': arabicTerm,
    'standard_category': standardCategory,
    'english_term': englishTerm,
    'fusha_meaning': fushaMeaning,
    'notes': notes,
  };

  Map<String, dynamic> toUpdateJson() => {
    'arabic_term': arabicTerm,
    'standard_category': standardCategory,
    'english_term': englishTerm,
    'fusha_meaning': fushaMeaning,
    'notes': notes,
  };
}
