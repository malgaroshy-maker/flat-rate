"use client";

import { useState, useRef, useEffect } from "react";
import { useLanguage } from "@/context/LanguageContext";
import ChatMessage from "./ChatMessage";

const IconSend = () => (<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>);

interface Message { role: "user" | "assistant"; content: string; }

interface Props { messages: Message[]; streamingContent: string; loading: boolean; onSend: (text: string) => void; }

export default function ChatPanel({ messages, streamingContent, loading, onSend }: Props) {
  const { uiLang } = useLanguage();
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streamingContent]);
  useEffect(() => { if (!loading) inputRef.current?.focus(); }, [loading]);

  const handleSubmit = () => { const text = input.trim(); if (!text || loading) return; setInput(""); onSend(text); };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1" role="log" aria-live="polite" aria-label={uiLang === "ar" ? "سجل المحادثة" : "Chat transcript"}>
        {messages.length === 0 && !loading && (
          <div className="flex items-center justify-center h-full text-slate-400 text-sm text-center px-8" role="status">
            {uiLang === "ar"
              ? "مرحباً! أنا مساعد تقدير تكلفة العمل.\nاسألني عن أي عملية صيانة أو تصليح وسأعطيك تقديراً بناءً على البيانات التاريخية."
              : "Hello! I'm your labor cost estimator assistant.\nAsk me about any maintenance job and I'll give you an estimate based on historical data."}
          </div>
        )}
        {messages.map((m, i) => (<ChatMessage key={i} role={m.role} content={m.content} />))}
        {streamingContent && (<ChatMessage role="assistant" content={streamingContent} streaming />)}
        {loading && !streamingContent && (<ChatMessage role="assistant" content="..." streaming />)}
        <div ref={bottomRef} />
      </div>
      <div className="border-t border-slate-200 bg-white px-4 py-3">
        <div className="flex gap-2">
          <input ref={inputRef} type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            placeholder={uiLang === "ar" ? "اكتب استفسارك..." : "Type your query..."}
            aria-label={uiLang === "ar" ? "اكتب استفسارك..." : "Type your query..."}
            disabled={loading}
            className="flex-1 rounded-lg border border-slate-300 px-4 py-2.5 text-sm placeholder-slate-400 focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20 disabled:opacity-50"
            dir={uiLang === "ar" ? "rtl" : "ltr"} />
          <button onClick={handleSubmit} disabled={loading || !input.trim()}
            aria-label={uiLang === "ar" ? "إرسال" : "Send"}
            className="flex items-center gap-1.5 rounded-lg bg-sky-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-sky-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500">
            <IconSend />{uiLang === "ar" ? "إرسال" : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
