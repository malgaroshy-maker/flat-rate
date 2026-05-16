"use client";

import { useEffect, useState, useCallback } from "react";
import { fetchSessions, deleteSession, type ChatSession } from "@/lib/chat_api";
import { useLanguage } from "@/context/LanguageContext";

const IconPlus = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>);
const IconTrash = () => (<svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>);

interface Props { activeId: string | null; onSelect: (id: string) => void; onNew: () => void; }

export default function SessionList({ activeId, onSelect, onNew }: Props) {
  const { uiLang } = useLanguage();
  const [sessions, setSessions] = useState<ChatSession[]>([]);

  useEffect(() => { let c = false; fetchSessions().then(s => { if (!c) setSessions(s); }).catch(() => {}); return () => { c = true; }; }, []);

  const reload = useCallback(async () => { try { setSessions(await fetchSessions()); } catch {} }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => { e.stopPropagation(); await deleteSession(id); await reload(); };

  return (
      <div className="border-r border-slate-200 bg-slate-50 flex flex-col h-full" role="navigation" aria-label={uiLang === "ar" ? "قائمة المحادثات" : "Chat sessions"}>
      <div className="px-4 py-3 border-b border-slate-200">
        <button onClick={onNew} className="w-full rounded-lg bg-sky-600 px-3 py-2 text-xs font-semibold text-white hover:bg-sky-700 transition-colors cursor-pointer flex items-center justify-center gap-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500" aria-label={uiLang === "ar" ? "محادثة جديدة" : "New chat"}>
          <IconPlus />{uiLang === "ar" ? "محادثة جديدة" : "New Chat"}
        </button>
      </div>
      <div className="flex-1 overflow-y-auto" role="listbox" aria-label={uiLang === "ar" ? "المحادثات" : "Sessions"}>
        {sessions.length === 0 && (<div className="px-4 py-8 text-center text-xs text-slate-400" role="status">{uiLang === "ar" ? "لا توجد محادثات" : "No conversations"}</div>)}
        {sessions.map((s) => (
          <button key={s.id} onClick={() => onSelect(s.id)}
            role="option" aria-selected={s.id === activeId}
            className={`w-full text-left px-4 py-3 text-sm border-b border-slate-100 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-sky-500 ${
              s.id === activeId ? "bg-sky-50 text-sky-700 border-l-2 border-l-sky-500" : "text-slate-700 hover:bg-slate-100"}`}>
            <div className="truncate font-medium">{s.title || (uiLang === "ar" ? "محادثة جديدة" : "New chat")}</div>
            <div className="text-xs text-slate-400 mt-0.5 flex items-center gap-2">
              <span>{s.message_count} msgs</span>
              <span onClick={(e) => handleDelete(s.id, e)} className="text-slate-400 hover:text-red-500 transition-colors cursor-pointer p-0.5" role="button" tabIndex={0} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.stopPropagation(); handleDelete(s.id, e as unknown as React.MouseEvent); } }} aria-label={uiLang === "ar" ? "حذف المحادثة" : "Delete session"}><IconTrash /></span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
