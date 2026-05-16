/** Chat API client with SSE streaming support. */

const BASE = "http://localhost:8000";

export interface ChatSession {
  id: string;
  title: string;
  lang: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export async function fetchSessions(): Promise<ChatSession[]> {
  const r = await fetch(`${BASE}/api/chat/sessions`);
  if (!r.ok) throw new Error("Failed to fetch sessions");
  const data = await r.json();
  return data.sessions;
}

export async function fetchSession(id: string): Promise<{ messages: ChatMessage[]; title: string; lang: string }> {
  const r = await fetch(`${BASE}/api/chat/sessions/${id}`);
  if (!r.ok) throw new Error("Session not found");
  return r.json();
}

export async function deleteSession(id: string): Promise<void> {
  await fetch(`${BASE}/api/chat/sessions/${id}`, { method: "DELETE" });
}

export function sendChatMessage(
  message: string,
  sessionId: string | null,
  lang: string,
  onToken: (text: string) => void,
  onSessionId: (id: string) => void,
  onDone: () => void,
  onError: (err: string) => void,
): AbortController {
  const params = new URLSearchParams({ message, lang });
  if (sessionId) params.set("session_id", sessionId);

  const controller = new AbortController();
  const url = `${BASE}/api/chat/send?${params.toString()}`;

  fetch(url, {
    method: "POST",
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const reader = res.body?.getReader();
      if (!reader) throw new Error("No stream reader");
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.session_id) onSessionId(data.session_id);
              if (data.text) onToken(data.text);
              if (data.done) onDone();
              if (data.error) onError(data.error);
            } catch { /* ignore parse errors */ }
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== "AbortError") onError(err.message);
    });

  return controller;
}
