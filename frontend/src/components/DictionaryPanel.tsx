"use client";

import { useState, useCallback, useEffect } from "react";
import { fetchTerms, createTerm, updateTerm, deleteTerm, type DictTerm } from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";
import { t } from "@/lib/i18n";

type SortKey = "arabic" | "category" | "english";
type SortDir = "asc" | "desc";

export default function DictionaryPanel() {
  const { uiLang } = useLanguage();
  const [terms, setTerms] = useState<DictTerm[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [loadKey, setLoadKey] = useState(0);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [formArab, setFormArab] = useState("");
  const [formCat, setFormCat] = useState("");
  const [formEng, setFormEng] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("arabic");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const triggerReload = useCallback(() => setLoadKey((k) => k + 1), []);

  useEffect(() => { let c = false; fetchTerms(search || undefined).then((d) => { if (!c) { setTerms(d.terms); setLoading(false); } }).catch(() => { if (!c) setLoading(false); }); return () => { c = true; }; }, [search, loadKey]);

  const resetForm = () => { setFormArab(""); setFormCat(""); setFormEng(""); setShowAdd(false); setEditingId(null); };
  const handleAdd = async () => { if (!formArab || !formCat) return; await createTerm({ arabic_term: formArab, standard_category: formCat, english_term: formEng }); resetForm(); triggerReload(); };
  const handleEdit = (t: DictTerm) => { setEditingId(t.id); setFormArab(t.arabic_term); setFormCat(t.standard_category); setFormEng(t.english_term); setShowAdd(false); };
  const handleUpdate = async () => { if (!editingId || !formArab || !formCat) return; await updateTerm(editingId, { arabic_term: formArab, standard_category: formCat, english_term: formEng }); resetForm(); triggerReload(); };
  const handleDelete = async (id: string) => { await deleteTerm(id); triggerReload(); };

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) { setSortDir(d => d === "asc" ? "desc" : "asc"); }
    else { setSortKey(key); setSortDir("asc"); }
  };

  const sorted = [...terms].sort((a, b) => {
    const va = keyOf(a, sortKey); const vb = keyOf(b, sortKey);
    return sortDir === "asc" ? va.localeCompare(vb, "ar") : vb.localeCompare(va, "ar");
  });

  const exportCSV = () => {
    const header = "Arabic,Category,English\n";
    const rows = sorted.map(t => `"${t.arabic_term}","${t.standard_category}","${t.english_term}"`).join("\n");
    const blob = new Blob([header + rows], { type: "text/csv" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "dictionary.csv"; a.click();
  };

  const sortIcon = (k: SortKey) => sortKey === k ? (sortDir === "asc" ? " ▲" : " ▼") : "";

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder={uiLang === "ar" ? "بحث في القاموس..." : "Search dictionary..."} aria-label={uiLang === "ar" ? "بحث في القاموس" : "Search dictionary"} className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500" />
        <button onClick={() => { resetForm(); setShowAdd(true); }} aria-label={uiLang === "ar" ? "إضافة مصطلح" : "Add term"} className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-700 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500">{uiLang === "ar" ? "إضافة مصطلح" : "Add Term"}</button>
        <button onClick={exportCSV} aria-label="Export CSV" className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500">CSV</button>
      </div>
      {(showAdd || editingId) && (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 space-y-3 shadow-sm">
          <h3 className="font-semibold text-sm text-slate-700">{editingId ? (uiLang === "ar" ? "تعديل مصطلح" : "Edit Term") : (uiLang === "ar" ? "مصطلح جديد" : "New Term")}</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <input value={formArab} onChange={(e) => setFormArab(e.target.value)} placeholder={uiLang === "ar" ? "المصطلح العربي" : "Arabic term"} aria-label={uiLang === "ar" ? "المصطلح العربي" : "Arabic term"} className="rounded border border-slate-300 px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500" dir="rtl" />
            <input value={formCat} onChange={(e) => setFormCat(e.target.value)} placeholder={uiLang === "ar" ? "التصنيف" : "Category"} aria-label={uiLang === "ar" ? "التصنيف" : "Category"} className="rounded border border-slate-300 px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500" />
            <input value={formEng} onChange={(e) => setFormEng(e.target.value)} placeholder={uiLang === "ar" ? "المقابل الإنجليزي" : "English term"} aria-label={uiLang === "ar" ? "المقابل الإنجليزي" : "English term"} className="rounded border border-slate-300 px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500" />
          </div>
          <div className="flex gap-2">
            <button onClick={editingId ? handleUpdate : handleAdd} aria-label={editingId ? (uiLang === "ar" ? "حفظ التعديلات" : "Save changes") : (uiLang === "ar" ? "إضافة مصطلح" : "Add term")} className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500">{editingId ? (uiLang === "ar" ? "حفظ" : "Save") : (uiLang === "ar" ? "إضافة" : "Add")}</button>
            <button onClick={resetForm} aria-label={uiLang === "ar" ? "إلغاء" : "Cancel"} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500">{uiLang === "ar" ? "إلغاء" : "Cancel"}</button>
          </div>
        </div>
      )}
      {loading ? (<div className="py-8 text-center text-slate-400" role="status">{t("loading", uiLang)}</div>) : terms.length === 0 ? (<div className="py-8 text-center text-slate-400" role="status">{uiLang === "ar" ? "لا توجد مصطلحات" : "No terms found"}</div>) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 shadow-sm">
          <div className="px-4 py-2 text-xs text-slate-500">{terms.length} {uiLang === "ar" ? "مصطلح" : "terms"}</div>
          <table className="w-full text-sm">
            <thead className="bg-slate-50"><tr>
              <th scope="col" className="px-4 py-2 text-left font-semibold text-slate-600 cursor-pointer hover:text-sky-600" onClick={() => toggleSort("arabic")}>{uiLang === "ar" ? "المصطلح العربي" : "Arabic"}{sortIcon("arabic")}</th>
              <th scope="col" className="px-4 py-2 text-left font-semibold text-slate-600 cursor-pointer hover:text-sky-600" onClick={() => toggleSort("category")}>{uiLang === "ar" ? "التصنيف" : "Category"}{sortIcon("category")}</th>
              <th scope="col" className="px-4 py-2 text-left font-semibold text-slate-600 cursor-pointer hover:text-sky-600 hidden sm:table-cell" onClick={() => toggleSort("english")}>{uiLang === "ar" ? "الإنجليزي" : "English"}{sortIcon("english")}</th>
              <th scope="col" className="px-4 py-2 text-right font-semibold text-slate-600">{uiLang === "ar" ? "إجراءات" : "Actions"}</th>
            </tr></thead>
            <tbody className="divide-y divide-slate-100">
              {sorted.map((t) => (<tr key={t.id} className="hover:bg-slate-50"><td className="px-4 py-2" dir="rtl">{t.arabic_term}</td><td className="px-4 py-2 text-slate-600">{t.standard_category}</td><td className="px-4 py-2 text-slate-500 text-xs hidden sm:table-cell">{t.english_term}</td>
                <td className="px-4 py-2 text-right"><button onClick={() => handleEdit(t)} className="mr-2 text-xs text-sky-600 hover:text-sky-800 cursor-pointer">{uiLang === "ar" ? "تعديل" : "Edit"}</button><button onClick={() => handleDelete(t.id)} className="text-xs text-red-500 hover:text-red-700 cursor-pointer">{uiLang === "ar" ? "حذف" : "Del"}</button></td></tr>))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function keyOf(t: DictTerm, k: SortKey): string {
  if (k === "arabic") return t.arabic_term || "";
  if (k === "category") return t.standard_category || "";
  return t.english_term || "";
}
