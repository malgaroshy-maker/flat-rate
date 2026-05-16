"use client";

import { useState, type FormEvent } from "react";
import { useLanguage } from "@/context/LanguageContext";
import { t } from "@/lib/i18n";

/* Lucide icons */
const IconSend = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>);
const IconX = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>);
const Spinner = () => (<svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" aria-hidden="true"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>);

interface Props {
  onSearch: (query: string) => void;
  loading: boolean;
}

export default function QueryInput({ onSearch, loading }: Props) {
  const { uiLang } = useLanguage();
  const [value, setValue] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const q = value.trim();
    if (!q || loading) return;
    onSearch(q);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex gap-2">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={t("searchPlaceholder", uiLang)}
          aria-label={t("searchPlaceholder", uiLang)}
          disabled={loading}
          className="flex-1 rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 shadow-sm focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20 disabled:opacity-50"
          dir={uiLang === "ar" ? "rtl" : "ltr"}
        />
        <button
          type="submit"
          disabled={loading || !value.trim()}
          aria-label={loading ? t("loading", uiLang) : t("searchButton", uiLang)}
          className="flex items-center gap-1.5 rounded-lg bg-sky-600 px-5 py-3 text-sm font-semibold text-white shadow-sm hover:bg-sky-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500"
        >
          {loading ? <Spinner /> : <IconSend />}
          {loading ? t("loading", uiLang) : t("searchButton", uiLang)}
        </button>
        <button
          type="button"
          onClick={() => setValue("")}
          aria-label={t("clearButton", uiLang)}
          className="flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500"
        >
          <IconX />
          {t("clearButton", uiLang)}
        </button>
      </div>
    </form>
  );
}
