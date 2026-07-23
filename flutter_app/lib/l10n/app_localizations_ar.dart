// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Arabic (`ar`).
class AppLocalizationsAr extends AppLocalizations {
  AppLocalizationsAr([String locale = 'ar']) : super(locale);

  @override
  String get appTitle => 'تقدير تكلفة العمل';

  @override
  String get searchTab => 'بحث';

  @override
  String get chatTab => 'محادثة';

  @override
  String get dictionaryTab => 'القاموس';

  @override
  String get pendingTab => 'مراجعة';

  @override
  String get settingsTab => 'إعدادات';

  @override
  String get searchHint => 'ابحث عن وظيفة، موديل، أو كلمة مفتاحية...';

  @override
  String get searchButton => 'بحث';

  @override
  String get confidence => 'الثقة';

  @override
  String get high => 'مرتفع';

  @override
  String get medium => 'متوسط';

  @override
  String get low => 'منخفض';

  @override
  String get median => 'المتوسط';

  @override
  String get records => 'سجل';

  @override
  String get details => 'تفاصيل';

  @override
  String get noResults => 'لا توجد نتائج';

  @override
  String get enterQuery => 'أدخل استفساراً للبحث في البيانات التاريخية';

  @override
  String get loading => 'جاري التحميل...';

  @override
  String get retry => 'إعادة المحاولة';

  @override
  String get languageLabel => 'لغة الواجهة';

  @override
  String get modeLabel => 'الوضع';

  @override
  String get systemInfo => 'معلومات النظام';

  @override
  String get backendUrl => 'رابط الخادم';

  @override
  String get llmBackend => 'محرك LLM';

  @override
  String get embeddingModel => 'نموذج التضمين';

  @override
  String get cloudMode => 'سحابي (Gemini)';

  @override
  String get localMode => 'محلي (بدون إنترنت)';

  @override
  String get exportPdf => 'تصدير PDF';

  @override
  String get sessions => 'الجلسات';

  @override
  String get newChat => 'محادثة جديدة';

  @override
  String get chatGreeting => 'مرحباً! اسألني عن أي صيانة أو إصلاح.';

  @override
  String get send => 'إرسال';

  @override
  String get typeYourQuery => 'اكتب استفسارك...';

  @override
  String get aiAssistant => 'مساعد ذكي';

  @override
  String get addTerm => 'إضافة مصطلح';

  @override
  String get editTerm => 'تعديل مصطلح';

  @override
  String get add => 'إضافة';

  @override
  String get save => 'حفظ';

  @override
  String get arabicTerm => 'المصطلح العربي';

  @override
  String get category => 'الفئة';

  @override
  String get englishTerm => 'المصطلح الإنجليزي';

  @override
  String get searchDictionary => 'ابحث في القاموس...';

  @override
  String get noTermsFound => 'لا توجد مصطلحات';

  @override
  String get resolveTerm => 'حل المصطلح';

  @override
  String resolveCount(int count) {
    return 'حل $count مصطلحات';
  }

  @override
  String get resolveAll => 'حل الكل';

  @override
  String get categoryForAll => 'الفئة للكل';

  @override
  String get noPendingTerms => 'لا توجد مصطلحات معلقة';

  @override
  String selectedCount(int count) {
    return '$count محدد';
  }

  @override
  String get from => 'من';

  @override
  String messages(int count) {
    return '$count رسائل';
  }

  @override
  String get noConversations => 'لا توجد محادثات';

  @override
  String get laborCostEstimator => 'تقدير تكلفة العمل';

  @override
  String get language => 'اللغة';

  @override
  String get offline => 'غير متصل';

  @override
  String get deleteSession => 'حذف الجلسة';

  @override
  String get statusSearching => 'يبحث في البيانات...';

  @override
  String get statusThinking => 'يفكر...';

  @override
  String get themeLabel => 'المظهر';

  @override
  String get themeLight => 'فاتح';

  @override
  String get themeDark => 'داكن';

  @override
  String get themeSystem => 'تلقائي';

  @override
  String get copy => 'نسخ';

  @override
  String get copied => 'تم النسخ';

  @override
  String get stopGenerating => 'إيقاف';

  @override
  String get suggestedPrompt1 => 'كم ساعة تبديل باطني أمامي؟';

  @override
  String get suggestedPrompt2 => 'كم ساعة تبديل مساعدات أمامية؟';

  @override
  String get suggestedPrompt3 => 'كم ساعة صيانة دورية 40 ألف كم؟';

  @override
  String get suggestedPrompt4 => 'كم ساعة تبديل طرمبة ماء؟';

  @override
  String get fushaMeaning => 'المعنى بالفصحى';

  @override
  String get notesOptional => 'ملاحظات (اختياري)';

  @override
  String get cachedDataBanner => 'غير متصل — بيانات محفوظة مسبقاً';

  @override
  String get queuedMessage => 'في الانتظار — سيتم الإرسال عند توفر الاتصال';

  @override
  String get noConnection => 'لا يوجد اتصال بالإنترنت';
}
