"use client";

import { useState, useEffect, useCallback } from "react";
import { fetchPending, resolvePending, type PendingTerm } from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";
import { t } from "@/lib/i18n";

export default function PendingPanel() {
  const { uiLang } = useLanguage();
  const [items, setItems] = useState<PendingTerm[]>([]);
  const [loading, setLoading] = useState(true);
  const [reloadKey, setReloadKey] = useState(0);
  const [resolving, setResolving] = useState<string | null>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [batchCat, setBatchCat] = useState("");
  const [formArab, setFormArab] = useState("");
  const [formCat, setFormCat] = useState("");
  const [formEng, setFormEng] = useState("");

  useEffect(() => { let c = false; fetchPending().then((d) => { if (!c) { setItems(d.pending.filter((p: PendingTerm) => p.status === "pending")); setLoading(false); } }).catch(() => { if (!c) setLoading(false); }); return () => { c = true; }; }, [reloadKey]);
  const reload = useCallback(() => setReloadKey((k) => k + 1), []);
  const handleResolve = async (id: string) => { if (!formArab || !formCat) return; await resolvePending(id, { arabic_term: formArab, standard_category: formCat, english_term: formEng }); setFormArab(""); setFormCat(""); setFormEng(""); setResolving(null); reload(); };
  const startResolve = (item: PendingTerm) => { setResolving(item.id); setFormArab(item.term_text); setFormCat(""); setFormEng(""); };

  const toggleSelect = (id: string) => {
    setSelected(prev => { const next = new Set(prev); if (next.has(id)) next.delete(id); else next.add(id); return next; });
  };

  const batchResolve = async () => {
    if (!batchCat) return;
    for (const id of selected) {
      const item = items.find(i => i.id === id);
      if (item) await resolvePending(id, { arabic_term: item.term_text, standard_category: batchCat, english_term: "" });
    }
    setSelected(new Set()); setBatchCat(""); reload();
  };

  const selectAll = () => {
    if (selected.size === items.length) setSelected(new Set());
    else setSelected(new Set(items.map(i => i.id)));
  };

  return (
    <div className="space-y-4">
      {items.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 p-3 rounded-xl border border-slate-200 bg-slate-50">
          <button onClick={selectAll} className="text-xs text-sky-600 hover:text-sky-800 cursor-pointer">{selected.size === items.length ? (uiLang === "ar" ? "إلغاء الكل" : "Deselect all") : (uiLang === "ar" ? "تحديد الكل" : "Select all")}</button>
          <span className="text-xs text-slate-400">{selected.size} {uiLang === "ar" ? "محدد" : "selected"}</span>
          <input value={batchCat} onChange={(e) => setBatchCat(e.target.value)} placeholder={uiLang === "ar" ? "التصنيف للجميع" : "Category for all"} aria-label={uiLang === "ar" ? "التصنيف للجميع" : "Category for all"} className="rounded border border-slate-300 px-2 py-1 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500" />
          <button onClick={batchResolve} disabled={!batchCat || selected.size === 0} className="rounded bg-emerald-600 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-40 transition-colors cursor-pointer">{uiLang === "ar" ? "تعيين الكل" : "Resolve all"}</button>
        </div>
      )}
      {loading ? (<div className="py-8 text-center text-slate-400" role="status">{t("loading", uiLang)}</div>) : items.length === 0 ? (<div className="py-8 text-center text-slate-400" role="status">{uiLang === "ar" ? "لا توجد مصطلحات معلقة للمراجعة" : "No pending terms to review"}</div>) : (
        items.map((item) => (
          <div key={item.id} className={`rounded-xl border p-4 shadow-sm transition-colors ${selected.has(item.id) ? "border-sky-400 bg-sky-50" : "border-amber-200 bg-amber-50"}`}>
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-2">
                <input type="checkbox" checked={selected.has(item.id)} onChange={() => toggleSelect(item.id)} aria-label={`Select ${item.term_text}`} className="mt-1" />
                <div><span className="font-semibold text-amber-900" dir="rtl">{item.term_text}</span><p className="text-xs text-amber-600 mt-1">{uiLang === "ar" ? "من استفسار:" : "From query:"} {item.query_text}</p></div>
              </div>
              {resolving !== item.id && (<button onClick={() => startResolve(item)} aria-label={uiLang === "ar" ? `تعيين "${item.term_text}"` : `Resolve "${item.term_text}"`} className="rounded-lg bg-amber-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-700 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500">{uiLang === "ar" ? "تعيين" : "Resolve"}</button>)}
            </div>
            {resolving === item.id && (
              <div className="mt-3 border-t border-amber-200 pt-3 space-y-2">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <input value={formArab} onChange={(e) => setFormArab(e.target.value)} placeholder={uiLang === "ar" ? "المصطلح العربي" : "Arabic term"} aria-label={uiLang === "ar" ? "المصطلح العربي" : "Arabic term"} className="rounded border border-slate-300 px-2 py-1.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500" dir="rtl" />
                  <input value={formCat} onChange={(e) => setFormCat(e.target.value)} placeholder={uiLang === "ar" ? "التصنيف" : "Category"} aria-label={uiLang === "ar" ? "التصنيف" : "Category"} className="rounded border border-slate-300 px-2 py-1.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500" />
                  <input value={formEng} onChange={(e) => setFormEng(e.target.value)} placeholder={uiLang === "ar" ? "الإنجليزي" : "English"} aria-label={uiLang === "ar" ? "الإنجليزي" : "English"} className="rounded border border-slate-300 px-2 py-1.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500" />
                </div>
                <div className="flex gap-2">
                  <button onClick={() => handleResolve(item.id)} aria-label={uiLang === "ar" ? "حفظ التعيين" : "Save resolution"} className="rounded bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500">{uiLang === "ar" ? "حفظ" : "Save"}</button>
                  <button onClick={() => setResolving(null)} aria-label={uiLang === "ar" ? "إلغاء التعيين" : "Cancel resolution"} className="rounded border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500">{uiLang === "ar" ? "إلغاء" : "Cancel"}</button>
                </div>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}
