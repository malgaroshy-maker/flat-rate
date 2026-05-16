"use client";

import { useState, useEffect } from "react";
import { useLanguage } from "@/context/LanguageContext";
import { fetchHealth, setMode, type HealthResponse } from "@/lib/api";
import { t } from "@/lib/i18n";

export default function SettingsPanel() {
  const { uiLang, responseLang, setUiLang, setResponseLang } = useLanguage();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [forceLocal, setForceLocal] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => { fetchHealth().then((h) => { setHealth(h); setForceLocal(h.force_local); }).catch(() => {}); }, []);

  const handleModeToggle = async (local: boolean) => {
    setSaving(true);
    try { await setMode(local); setForceLocal(local); const h = await fetchHealth(); setHealth(h); } catch {}
    setSaving(false);
  };

  const btnActive = "border-sky-500 bg-sky-50 text-sky-700";
  const btnInactive = "border-slate-300 text-slate-600 hover:bg-slate-50 cursor-pointer";

  return (
    <div className="max-w-2xl space-y-6">
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-800 mb-3">{uiLang === "ar" ? "لغة الواجهة" : "Interface Language"}</h2>
        <div className="flex gap-2" role="radiogroup" aria-label={uiLang === "ar" ? "لغة الواجهة" : "Interface language"}>
          <button onClick={() => setUiLang("ar")} role="radio" aria-checked={uiLang === "ar"} className={`flex-1 rounded-lg border px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 ${uiLang === "ar" ? btnActive : btnInactive}`}>العربية</button>
          <button onClick={() => setUiLang("en")} role="radio" aria-checked={uiLang === "en"} className={`flex-1 rounded-lg border px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 ${uiLang === "en" ? btnActive : btnInactive}`}>English</button>
        </div>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-800 mb-3">{uiLang === "ar" ? "لغة ردود الذكاء الاصطناعي" : "AI Response Language"}</h2>
        <div className="flex gap-2" role="radiogroup" aria-label={uiLang === "ar" ? "لغة الردود" : "Response language"}>
          <button onClick={() => setResponseLang("ar")} role="radio" aria-checked={responseLang === "ar"} className={`flex-1 rounded-lg border px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 ${responseLang === "ar" ? btnActive : btnInactive}`}>العربية</button>
          <button onClick={() => setResponseLang("en")} role="radio" aria-checked={responseLang === "en"} className={`flex-1 rounded-lg border px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 ${responseLang === "en" ? btnActive : btnInactive}`}>English</button>
        </div>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-800 mb-3">Mode</h2>
        <div className="flex gap-2">
          <button onClick={() => handleModeToggle(false)} disabled={saving} aria-pressed={!forceLocal} className={`flex-1 rounded-lg border px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 ${!forceLocal ? "border-sky-500 bg-sky-50 text-sky-700" : "border-slate-300 text-slate-600 hover:bg-slate-50 cursor-pointer"}`}>Cloud (Gemini)</button>
          <button onClick={() => handleModeToggle(true)} disabled={saving} aria-pressed={forceLocal} className={`flex-1 rounded-lg border px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 ${forceLocal ? "border-emerald-500 bg-emerald-50 text-emerald-700" : "border-slate-300 text-slate-600 hover:bg-slate-50 cursor-pointer"}`}>Local (Offline)</button>
        </div>
      </div>
      {health && (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-slate-800 mb-3">{t("systemInfo", uiLang)}</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-slate-500">{t("mode", uiLang)}</span><span className={`font-semibold ${health.mode === "cloud" ? "text-sky-600" : "text-emerald-600"}`}>{health.mode === "cloud" ? "Cloud (Gemini)" : "Local"}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">{t("localLLM", uiLang)}</span><span className="text-slate-700">{health.local_llm_backend}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">{t("embeddingModel", uiLang)}</span><span className="text-slate-700 text-xs font-mono">{health.embedding_model}</span></div>
          </div>
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="inline-block mt-3 text-xs text-sky-600 hover:text-sky-800 font-medium">{t("apiDocs", uiLang)} →</a>
        </div>
      )}
    </div>
  );
}
