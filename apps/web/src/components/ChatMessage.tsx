"use client";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

export function ChatMessage({ role, content, isStreaming }: ChatMessageProps) {
  const isAssistant = role === "assistant";

  return (
    <div
      className={`flex w-full ${isAssistant ? "justify-start" : "justify-end"} mb-4`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isAssistant ? "rounded-bl-sm" : "rounded-br-sm"
        }`}
        style={{
          background: isAssistant
            ? "var(--care-surface)"
            : "var(--care-accent)",
          color: isAssistant ? "var(--care-text)" : "white",
          border: isAssistant ? "1px solid var(--care-border)" : "none",
        }}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
        {isStreaming && (
          <span className="inline-flex gap-1 ml-1">
            <span className="typing-dot w-1.5 h-1.5 rounded-full bg-current opacity-50" />
            <span className="typing-dot w-1.5 h-1.5 rounded-full bg-current opacity-50" />
            <span className="typing-dot w-1.5 h-1.5 rounded-full bg-current opacity-50" />
          </span>
        )}
      </div>
    </div>
  );
}
