"use client";

import { Mic, MicOff, Send } from "lucide-react";
import { useCallback, useRef, useState } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  voiceSupported?: boolean;
  isListening?: boolean;
  voiceTranscript?: string;
  onVoiceStart?: () => void;
  onVoiceStop?: () => void;
}

export function ChatInput({
  onSend,
  disabled,
  voiceSupported,
  isListening,
  voiceTranscript,
  onVoiceStart,
  onVoiceStop,
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = useCallback(() => {
    const text = input.trim();
    if (!text || disabled) return;
    onSend(text);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [input, disabled, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // Auto-resize
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
  };

  return (
    <div
      className="border-t px-4 py-3"
      style={{
        borderColor: "var(--care-border)",
        background: "var(--care-surface)",
      }}
    >
      {/* Voice transcript preview */}
      {isListening && voiceTranscript && (
        <div
          className="text-xs mb-2 px-3 py-1.5 rounded-lg italic"
          style={{
            background: "var(--care-accent-bg)",
            color: "var(--care-text-secondary)",
          }}
        >
          {voiceTranscript}...
        </div>
      )}

      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={isListening ? "Listening..." : "Type your response..."}
          disabled={disabled || isListening}
          rows={1}
          className="flex-1 resize-none rounded-xl border px-4 py-2.5 text-sm outline-none transition-colors focus:ring-2"
          style={{
            borderColor: "var(--care-border)",
            background: "var(--care-bg)",
            color: "var(--care-text)",
          }}
        />

        {/* Voice button */}
        {voiceSupported && (
          <button
            onClick={isListening ? onVoiceStop : onVoiceStart}
            className={`p-2.5 rounded-xl transition-all ${isListening ? "voice-active" : ""}`}
            style={{
              background: isListening
                ? "var(--care-error)"
                : "var(--care-surface)",
              color: isListening ? "white" : "var(--care-text-secondary)",
              border: isListening ? "none" : "1px solid var(--care-border)",
            }}
            title={isListening ? "Stop listening" : "Start voice input"}
          >
            {isListening ? <MicOff size={18} /> : <Mic size={18} />}
          </button>
        )}

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="p-2.5 rounded-xl transition-all disabled:opacity-30"
          style={{
            background: "var(--care-accent)",
            color: "white",
          }}
          title="Send message"
        >
          <Send size={18} />
        </button>
      </div>

      {/* Privacy note for voice */}
      {voiceSupported && (
        <p
          className="text-[10px] mt-1.5 text-center"
          style={{ color: "var(--care-text-secondary)" }}
        >
          Voice input sends audio to your browser&apos;s speech service for
          processing.{" "}
          <button className="underline" onClick={onVoiceStart}>
            Learn more
          </button>
        </p>
      )}
    </div>
  );
}
