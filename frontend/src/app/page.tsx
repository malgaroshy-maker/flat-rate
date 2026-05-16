"use client";

import { useState, useCallback } from "react";
import { useLanguage } from "@/context/LanguageContext";
import { searchQuery, type QueryResult } from "@/lib/api";
import { t } from "@/lib/i18n";
import QueryInput from "@/components/QueryInput";
import ResultsCard from "@/components/ResultsCard";

export default function Home() {
  const { uiLang, responseLang } = useLanguage();
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastQuery, setLastQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSearch = useCallback(
    async (query: string) => {
      setLoading(true);
      setError(null);
      setLastQuery(query);
      try {
        const data = await searchQuery({
          q: query,
          n: 5,
          lang: responseLang,
        });
        setResult(data);

        // Save to query history
        const history = JSON.parse(localStorage.getItem("labor_history") || "[]");
        history.unshift({ query, timestamp: Date.now() });
        localStorage.setItem("labor_history", JSON.stringify(history.slice(0, 10)));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    },
    [responseLang]
  );

  const handleExportPdf = useCallback(async () => {
    if (!lastQuery) return;
    const BASE = "http://localhost:8000";
    const sp = new URLSearchParams({ q: lastQuery, n: "5" });
    if (responseLang) sp.set("lang", responseLang);
    try {
      const res = await fetch(`${BASE}/api/export/pdf?${sp.toString()}`, { method: "POST" });
      if (!res.ok) throw new Error("Export failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "labor-estimate.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // ignore
    }
  }, [lastQuery, responseLang]);

  return (
    <div className="mx-auto max-w-[1200px] px-6 py-8">
      <div className="mb-8">
        <QueryInput onSearch={handleSearch} loading={loading} />
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 mb-6">
          {t("error", uiLang)}: {error}
          <button
            onClick={() => setError(null)}
            className="ml-2 underline hover:no-underline"
          >
            {t("retry", uiLang)}
          </button>
        </div>
      )}

      {loading && !result && (
        <div className="flex items-center justify-center py-16 text-slate-400">
          <svg className="animate-spin h-6 w-6 mr-2" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          {t("loading", uiLang)}
        </div>
      )}

      {!loading && !error && !result && (
        <div className="flex items-center justify-center py-16 text-slate-400 text-sm">
          {t("searchPlaceholder", uiLang)}
        </div>
      )}

      {result && (
        <>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-500">
              {t("estimate", uiLang)}: {result.query}
            </h2>
            <button
              onClick={handleExportPdf}
              className="rounded-lg border border-zinc-300 bg-white px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50 transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {uiLang === "ar" ? "تصدير PDF" : "Export PDF"}
            </button>
          </div>
          <ResultsCard
            hits={result.hits}
            confidence={result.confidence_range}
            outliers={result.outliers}
            naturalResponse={result.natural_response}
          />
        </>
      )}
    </div>
  );
}
