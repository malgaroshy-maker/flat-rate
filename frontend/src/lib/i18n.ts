/** Internationalization: Arabic ↔ English translations and RTL helper. */

export type Lang = "ar" | "en";

export const translations: Record<string, Record<Lang, string>> = {
  appTitle: { ar: "مقدّر تكلفة العمل", en: "Labor Cost Estimator" },
  searchPlaceholder: { ar: "اكتب استفسارك... مثال: HD45 تغيير باطني فرامل", en: "Type your query... e.g. HD45 brake pad change" },
  searchButton: { ar: "بحث", en: "Search" },
  clearButton: { ar: "مسح", en: "Clear" },
  estimate: { ar: "التقدير", en: "Estimate" },
  hours: { ar: "ساعة", en: "hours" },
  confidence: { ar: "نطاق الثقة", en: "Confidence Range" },
  median: { ar: "المتوسط", en: "Median" },
  min: { ar: "الحد الأدنى", en: "Minimum" },
  max: { ar: "الحد الأعلى", en: "Maximum" },
  outliers: { ar: "قيم شاذة", en: "Outliers" },
  outlierNotice: { ar: "تنبيه: سجلات غير اعتيادية", en: "Notice: anomalous records" },
  noResults: { ar: "لا توجد نتائج مطابقة", en: "No matching results" },
  loading: { ar: "جاري البحث...", en: "Searching..." },
  error: { ar: "حدث خطأ", en: "An error occurred" },
  retry: { ar: "إعادة المحاولة", en: "Retry" },
  details: { ar: "تفاصيل", en: "Details" },
  hideDetails: { ar: "إخفاء التفاصيل", en: "Hide details" },
  history: { ar: "السجل", en: "History" },
  noHistory: { ar: "لا يوجد سجل", en: "No query history" },
  language: { ar: "اللغة", en: "Language" },
  responseLanguage: { ar: "لغة الرد", en: "Response Language" },
  settings: { ar: "الإعدادات", en: "Settings" },
  records: { ar: "سجل", en: "records" },
  department: { ar: "الورشة", en: "Department" },
  model: { ar: "الموديل", en: "Model" },
  rate: { ar: "السعر/ساعة", en: "Rate/hr" },
  estimatedCost: { ar: "التكلفة التقديرية", en: "Estimated Cost" },
  cost: { ar: "التكلفة", en: "Cost" },
  currency: { ar: "د.ل", en: "LYD" },
  exportPdf: { ar: "تصدير PDF", en: "Export PDF" },
  compoundNotice: { ar: "تنبيه: هذا السجل يشمل عمليات متعددة", en: "Note: this record covers multiple operations" },
  ops: { ar: "عمليات", en: "operations" },
  unitEstimate: { ar: "التقدير لكل عملية", en: "Per-operation estimate" },
  systemInfo: { ar: "معلومات النظام", en: "System Info" },
  mode: { ar: "الوضع", en: "Mode" },
  localLLM: { ar: "النموذج المحلي", en: "Local LLM" },
  embeddingModel: { ar: "نموذج التضمين", en: "Embedding Model" },
  apiDocs: { ar: "توثيق API", en: "API Docs" },
  apiKey: { ar: "مفتاح Gemini API", en: "Gemini API Key" },
  apiKeyHint: { ar: "اتركه فارغاً لاستخدام الوضع المحلي", en: "Leave empty for local mode" },
  offline: { ar: "محلي", en: "Offline" },
  online: { ar: "سحابي", en: "Cloud" },
  notSet: { ar: "غير مضبوط", en: "Not set" },
  set: { ar: "مضبوط", en: "Set" },
};

export function t(key: string, lang: Lang): string {
  return translations[key]?.[lang] ?? key;
}

export function isRTL(lang: Lang): boolean {
  return lang === "ar";
}
