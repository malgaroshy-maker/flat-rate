"use client";

import { useState } from "react";
import { useLanguage } from "@/context/LanguageContext";
import { t } from "@/lib/i18n";

const IconAlertTriangle = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>);
const IconChevronDown = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>);
const IconChevronUp = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><polyline points="18 15 12 9 6 15"/></svg>);

interface OutlierEntry { model: string; anomalies: { value: number; mean: number; sigma: number; deviation: number }[]; }

export default function OutlierPanel({ outliers }: { outliers: OutlierEntry[] }) {
  const { uiLang } = useLanguage();
  const [open, setOpen] = useState(false);
  if (!outliers.length) return null;

  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50">
      <button onClick={() => setOpen(!open)} aria-expanded={open} aria-controls="outlier-details" className="w-full px-4 py-3 text-left text-sm font-semibold text-amber-800 hover:bg-amber-100 rounded-xl transition-colors cursor-pointer flex items-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500">
        <IconAlertTriangle />
        {open ? <IconChevronUp /> : <IconChevronDown />}
        {t("outlierNotice", uiLang)}
      </button>
      {open && (
        <div id="outlier-details" className="px-4 pb-4 space-y-2">
          {outliers.map((o, i) => (
            <div key={i} className="text-sm text-amber-700">
              <strong>{t("model", uiLang)}: {o.model}</strong>
              {o.anomalies.map((a, j) => (
                <div key={j} className="ml-4 mt-1 font-mono">{a.value}h ({a.deviation > 0 ? "+" : ""}{a.deviation}σ)</div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
