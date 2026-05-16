"use client";

import { useState, useCallback, useRef } from "react";
import { useLanguage } from "@/context/LanguageContext";
import { sendChatMessage, fetchSession } from "@/lib/chat_api";
import ChatPanel from "@/components/ChatPanel";
import SessionList from "@/components/SessionList";

interface Message { role: "user" | "assistant"; content: string; }

export default function AssistantPage() {
  const { uiLang } = useLanguage();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingContent, setStreamingContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const handleSend = useCallback((text: string) => {
    setMessages((p) => [...p, { role: "user", content: text }]);
    setLoading(true);
    setStreamingContent("");
    let fullResponse = "";
    const controller = sendChatMessage(text, sessionId, uiLang,
      (token) => { fullResponse += token; setStreamingContent(fullResponse); },
      (sid) => setSessionId(sid),
      () => { setMessages((p) => [...p, { role: "assistant", content: fullResponse }]); setStreamingContent(""); setLoading(false); },
      (err) => { setMessages((p) => [...p, { role: "assistant", content: `${err}` }]); setStreamingContent(""); setLoading(false); }
    );
    abortRef.current = controller;
  }, [sessionId, uiLang]);

  const handleSelectSession = useCallback(async (id: string) => {
    setSessionId(id); setMessages([]);
    try { const s = await fetchSession(id); setMessages(s.messages || []); } catch {}
    setSidebarOpen(false);
  }, []);

  const handleNew = useCallback(() => {
    abortRef.current?.abort();
    setSessionId(null); setMessages([]); setStreamingContent(""); setLoading(false);
    setSidebarOpen(false);
  }, []);

  return (
    <div className="flex h-[calc(100vh-3.5rem)] relative">
      <button aria-label="Toggle sidebar" aria-expanded={sidebarOpen}
        className="lg:hidden fixed top-16 left-3 z-30 rounded-md bg-slate-900 p-2 text-white shadow"
        onClick={() => setSidebarOpen(!sidebarOpen)}>
        <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-20 bg-slate-900/50" onClick={() => setSidebarOpen(false)} />
      )}
      <div className={`${sidebarOpen ? "fixed inset-y-0 left-0 z-20 w-64" : "hidden"} lg:static lg:block lg:w-64 shrink-0`}>
        <SessionList activeId={sessionId} onSelect={handleSelectSession} onNew={handleNew} />
      </div>
      <div className="flex-1 flex flex-col min-w-0">
        <ChatPanel messages={messages} streamingContent={streamingContent} loading={loading} onSend={handleSend} />
      </div>
    </div>
  );
}
