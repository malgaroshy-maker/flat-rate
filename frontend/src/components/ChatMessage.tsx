"use client";

interface Props { role: "user" | "assistant"; content: string; streaming?: boolean; }

function renderMarkdown(text: string): string {
  const html = text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^### (.+)$/gm, '<h4 class="font-semibold text-sm mt-2 mb-1">$1</h4>')
    .replace(/^## (.+)$/gm, '<h3 class="font-semibold text-base mt-2 mb-1">$1</h3>')
    .replace(/^# (.+)$/gm, '<h2 class="font-semibold text-lg mt-2 mb-1">$1</h2>')
    .replace(/^\- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li class="ml-4 list-decimal" value="$1">$2</li>')
    .replace(/`([^`]+)`/g, '<code class="bg-slate-200 rounded px-1 text-xs">$1</code>')
    .replace(/\n\n/g, '</p><p class="mb-1">')
    .replace(/\n/g, '<br/>');
  return `<p class="mb-1">${html}</p>`;
}

export default function ChatMessage({ role, content, streaming }: Props) {
  const isUser = role === "user";

  const handleCopy = () => {
    navigator.clipboard.writeText(content).catch(() => {});
  };

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4 group`}>
      <div className="flex flex-col max-w-[80%]">
        <div role="article" aria-label={isUser ? "Your message" : "Assistant message"}
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser ? "bg-sky-600 text-white rounded-br-md" : "bg-slate-100 text-slate-900 rounded-bl-md"
          }`}
        >
          {isUser ? (
            <div className="whitespace-pre-wrap">{content}</div>
          ) : (
            <div className="prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
            />
          )}
          {streaming && <span className="inline-block w-2 h-4 bg-slate-400 animate-pulse ml-1 align-middle rounded-sm" aria-hidden="true" />}
        </div>
        <button onClick={handleCopy}
          className="self-start mt-0.5 text-xs text-slate-400 hover:text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
          aria-label="Copy message"
        >
          Copy
        </button>
      </div>
    </div>
  );
}
