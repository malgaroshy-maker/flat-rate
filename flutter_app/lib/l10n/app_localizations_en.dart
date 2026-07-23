// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Labor Cost Estimator';

  @override
  String get searchTab => 'Search';

  @override
  String get chatTab => 'Chat';

  @override
  String get dictionaryTab => 'Dictionary';

  @override
  String get pendingTab => 'Review';

  @override
  String get settingsTab => 'Settings';

  @override
  String get searchHint => 'Search by job, model, or keyword...';

  @override
  String get searchButton => 'Search';

  @override
  String get confidence => 'Confidence';

  @override
  String get high => 'High';

  @override
  String get medium => 'Medium';

  @override
  String get low => 'Low';

  @override
  String get median => 'Median';

  @override
  String get records => 'records';

  @override
  String get details => 'Details';

  @override
  String get noResults => 'No results found';

  @override
  String get enterQuery => 'Enter a query to search historical data';

  @override
  String get loading => 'Loading...';

  @override
  String get retry => 'Retry';

  @override
  String get languageLabel => 'Interface Language';

  @override
  String get modeLabel => 'Mode';

  @override
  String get systemInfo => 'System Info';

  @override
  String get backendUrl => 'Backend URL';

  @override
  String get llmBackend => 'LLM Backend';

  @override
  String get embeddingModel => 'Embedding Model';

  @override
  String get cloudMode => 'Cloud (Gemini)';

  @override
  String get localMode => 'Local (Offline)';

  @override
  String get exportPdf => 'Export PDF';

  @override
  String get sessions => 'Sessions';

  @override
  String get newChat => 'New Chat';

  @override
  String get chatGreeting => 'Hello! Ask me about any maintenance job.';

  @override
  String get send => 'Send';

  @override
  String get typeYourQuery => 'Type your query...';

  @override
  String get aiAssistant => 'AI Assistant';

  @override
  String get addTerm => 'Add Term';

  @override
  String get editTerm => 'Edit Term';

  @override
  String get add => 'Add';

  @override
  String get save => 'Save';

  @override
  String get arabicTerm => 'Arabic term';

  @override
  String get category => 'Category';

  @override
  String get englishTerm => 'English term';

  @override
  String get searchDictionary => 'Search dictionary...';

  @override
  String get noTermsFound => 'No terms found';

  @override
  String get resolveTerm => 'Resolve Term';

  @override
  String resolveCount(int count) {
    return 'Resolve $count terms';
  }

  @override
  String get resolveAll => 'Resolve All';

  @override
  String get categoryForAll => 'Category for all';

  @override
  String get noPendingTerms => 'No pending terms';

  @override
  String selectedCount(int count) {
    return '$count selected';
  }

  @override
  String get from => 'From';

  @override
  String messages(int count) {
    return '$count messages';
  }

  @override
  String get noConversations => 'No conversations';

  @override
  String get laborCostEstimator => 'Labor Cost Estimator';

  @override
  String get language => 'Language';

  @override
  String get offline => 'offline';

  @override
  String get deleteSession => 'Delete session';

  @override
  String get statusSearching => 'Searching data...';

  @override
  String get statusThinking => 'Thinking...';

  @override
  String get themeLabel => 'Theme';

  @override
  String get themeLight => 'Light';

  @override
  String get themeDark => 'Dark';

  @override
  String get themeSystem => 'System';

  @override
  String get copy => 'Copy';

  @override
  String get copied => 'Copied';

  @override
  String get stopGenerating => 'Stop';

  @override
  String get suggestedPrompt1 => 'How many hours to replace front brake pads?';

  @override
  String get suggestedPrompt2 =>
      'How many hours to replace front shock absorbers?';

  @override
  String get suggestedPrompt3 => 'How many hours for a 40,000 km service?';

  @override
  String get suggestedPrompt4 => 'How many hours to replace a water pump?';

  @override
  String get fushaMeaning => 'Fusha Meaning';

  @override
  String get notesOptional => 'Notes (optional)';

  @override
  String get cachedDataBanner => 'Offline — showing cached data';

  @override
  String get queuedMessage => 'Queued — will send when back online';

  @override
  String get noConnection => 'No internet connection';
}
