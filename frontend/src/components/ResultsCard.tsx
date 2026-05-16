"use client";

import { useState } from "react";
import { useLanguage } from "@/context/LanguageContext";
import { t } from "@/lib/i18n";
import type { QueryHit } from "@/lib/api";
import OutlierPanel from "./OutlierPanel";

/* Lucide icons */
const IconChevronDown = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>);
const IconChevronUp = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><polyline points="18 15 12 9 6 15"/></svg>);
const IconAlertTriangle = () => (<svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>);

interface Props {
  hits: QueryHit[];
  confidence: { p10: number; p50: number; p90: number };
  outliers: QueryResult["outliers"];
  naturalResponse?: string;
}

interface QueryResult {
  outliers: { model: string; anomalies: { value: number; mean: number; sigma: number; deviation: number }[] }[];
}

export default function ResultsCard({ hits, confidence, outliers, naturalResponse }: Props) {
  const { uiLang } = useLanguage();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const toggle = (id: string) => setExpanded((p) => ({ ...p, [id]: !p[id] }));
  if (!hits.length) return null;

  const dir = uiLang === "ar" ? "rtl" : "ltr";
  const avgRate = hits[0]?.price_mean || 0;
  const p10Cost = confidence.p10 * avgRate;
  const p50Cost = confidence.p50 * avgRate;
  const p90Cost = confidence.p90 * avgRate;

  const totalRecords = hits.reduce((sum, h) => sum + (h.qty_count || 0), 0);
  const modelCount = new Set(hits.map(h => h.model)).size;
  const topSimilarity = hits[0]?.similarity || 0;
  const confidenceLevel: "high" | "medium" | "low" =
    totalRecords >= 50 && modelCount <= 2 && topSimilarity >= 0.9 ? "high" :
    totalRecords >= 15 ? "medium" : "low";
  const confidenceColors = { high: "bg-emerald-100 text-emerald-700", medium: "bg-amber-100 text-amber-700", low: "bg-red-100 text-red-700" };
  const confidenceLabels: Record<string, string> = { high: uiLang === "ar" ? "موثوق" : "High", medium: uiLang === "ar" ? "متوسط" : "Medium", low: uiLang === "ar" ? "منخفض" : "Low" };

  return (
    <div className="w-full space-y-4" dir={dir}>
      {naturalResponse && (
        <div className="rounded-lg border border-sky-200 bg-sky-50 p-4 text-sm text-sky-900">{naturalResponse}</div>
      )}

      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-emerald-800 mb-2 font-mono tracking-tight flex items-center gap-2">
          {t("confidence", uiLang)}
          <span className={`text-xs px-2 py-0.5 rounded-full font-sans font-medium ${confidenceColors[confidenceLevel]}`}>{confidenceLabels[confidenceLevel]}</span>
        </h2>
        <div className="flex items-baseline gap-4">
          <span className="text-3xl font-bold text-emerald-900 font-mono animate-metric-pulse">
            {confidence.p10}–{confidence.p90}h
          </span>
          <span className="text-sm text-emerald-700">{t("median", uiLang)}: {confidence.p50}h</span>
        </div>
        {avgRate > 0 && (
          <div className="mt-2 pt-2 border-t border-emerald-200">
            <h3 className="text-sm font-semibold text-emerald-800">{t("estimatedCost", uiLang)}</h3>
            <div className="flex items-baseline gap-4 mt-1">
              <span className="text-2xl font-bold text-emerald-900 font-mono">
                {p10Cost.toFixed(0)}–{p90Cost.toFixed(0)} {t("currency", uiLang)}
              </span>
              <span className="text-sm text-emerald-700">{t("median", uiLang)}: {p50Cost.toFixed(0)} {t("currency", uiLang)}</span>
              <span className="text-xs text-emerald-600">({t("rate", uiLang)} {avgRate.toFixed(0)} {t("currency", uiLang)})</span>
            </div>
          </div>
        )}
      </div>

      <div className="space-y-3">
        {hits.map((hit) => {
          const rate = hit.price_mean || 0;
          const p50h = hit.confidence_range.median;
          const p10h = hit.confidence_range.p10;
          const p90h = hit.confidence_range.p90;
          const cost = p50h * rate;

          return (
            <div key={hit.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900 font-mono tracking-tight">{hit.model}</h3>
                  <p className="text-sm text-slate-500">{t("department", uiLang)}: {hit.departments} &middot; {hit.qty_count} {t("records", uiLang)}</p>
                  {hit.compound && (
                    <p className="text-xs text-amber-600 mt-1 flex items-center gap-1">
                      <IconAlertTriangle />
                      {t("compoundNotice", uiLang)} ({hit.compound_max_ops} {t("ops", uiLang)})
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <span className="text-lg font-bold text-slate-900 font-mono">{p50h}h</span>
                  {rate > 0 && <p className="text-sm font-semibold text-slate-700">{cost.toFixed(0)} {t("currency", uiLang)}</p>}
                  <p className="text-xs text-slate-500">{p10h}–{p90h}h</p>
                </div>
              </div>

              <button onClick={() => toggle(hit.id)} aria-expanded={!!expanded[hit.id]} aria-controls={`details-${hit.id}`} className="mt-2 text-sm text-sky-600 hover:text-sky-800 cursor-pointer flex items-center gap-1 font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 rounded">
                {expanded[hit.id] ? <><IconChevronUp />{t("hideDetails", uiLang)}</> : <><IconChevronDown />{t("details", uiLang)}</>}
              </button>

              {expanded[hit.id] && (
                <div id={`details-${hit.id}`} className="mt-3 border-t border-slate-100 pt-3 text-sm text-slate-600 space-y-1">
                  <p>{t("min", uiLang)}: {p10h}h (P10)</p><p>P25: {hit.confidence_range.p25}h</p>
                  <p>{t("median", uiLang)}: {p50h}h (P50)</p><p>P75: {hit.confidence_range.p75}h</p>
                  <p>{t("max", uiLang)}: {p90h}h (P90)</p>
                  {rate > 0 && (<><p>{t("rate", uiLang)}: {rate.toFixed(0)} {t("currency", uiLang)}/h</p><p>{t("cost", uiLang)}: {(p10h * rate).toFixed(0)}–{(p90h * rate).toFixed(0)} {t("currency", uiLang)}</p></>)}
                  {hit.compound && hit.weighted_qty_p50 > 0 && (
                    <p className="text-amber-700 font-medium">{t("unitEstimate", uiLang)}: {hit.weighted_qty_p50.toFixed(1)}–{hit.weighted_qty_p90.toFixed(1)}h ({hit.compound_max_ops} {t("ops", uiLang)}, {Math.round(hit.compound_pct * 100)}% {uiLang === "ar" ? "مركبة" : "compound"})</p>
                  )}
                  <p>{t("department", uiLang)}: {hit.departments}</p>
                  <p>Code: {hit.code} &middot; {t("records", uiLang)}: {hit.qty_count}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {outliers.length > 0 && <OutlierPanel outliers={outliers} />}
    </div>
  );
}
