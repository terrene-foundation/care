"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ChatInput } from "@/components/ChatInput";
import { ChatMessage } from "@/components/ChatMessage";
import { ConfigDownload } from "@/components/ConfigDownload";
import { MaturityRadar } from "@/components/MaturityRadar";
import { ProgressBar } from "@/components/ProgressBar";
import { useVoice } from "@/hooks/useVoice";
import {
  createSession,
  getDiagnosis,
  sendMessage,
  type DiagnosisData,
  type OrgUpdate,
} from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState("Assess");
  const [state, setState] = useState("welcome");
  const [orgData, setOrgData] = useState<OrgUpdate | null>(null);
  const [diagnosis, setDiagnosis] = useState<DiagnosisData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Voice input
  const handleVoiceResult = useCallback(
    (text: string) => {
      if (sessionId && !isStreaming) {
        handleSend(text);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [sessionId, isStreaming],
  );

  const voice = useVoice(handleVoiceResult);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  // Initialize session
  useEffect(() => {
    async function init() {
      try {
        const session = await createSession();
        setSessionId(session.session_id);
        setMessages([{ role: "assistant", content: session.welcome_message }]);
        setProgress(session.progress);
      } catch {
        setError(
          "Could not connect to the CARE server. Please check that the API is running.",
        );
      }
    }
    init();
  }, []);

  // Fetch diagnosis when we reach that phase
  useEffect(() => {
    if (state === "recommendations" && sessionId && !diagnosis) {
      getDiagnosis(sessionId)
        .then(setDiagnosis)
        .catch(() => {});
    }
  }, [state, sessionId, diagnosis]);

  const handleSend = useCallback(
    async (text: string) => {
      if (!sessionId || isStreaming) return;

      setMessages((prev) => [...prev, { role: "user", content: text }]);
      setIsStreaming(true);
      setError(null);

      let assistantContent = "";
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      await sendMessage(sessionId, text, {
        onToken: (token) => {
          assistantContent += token;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              role: "assistant",
              content: assistantContent,
            };
            return updated;
          });
        },
        onState: (s) => {
          setState(s.state);
          setPhase(s.phase);
          setProgress(s.progress);
        },
        onOrgUpdate: (data) => {
          setOrgData(data);
        },
        onDone: () => {
          setIsStreaming(false);
        },
        onError: (err) => {
          setError(err);
          setIsStreaming(false);
        },
      });
    },
    [sessionId, isStreaming],
  );

  const isComplete = state === "complete";

  return (
    <div className="flex h-screen">
      {/* Main chat panel */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Header */}
        <header
          className="flex items-center gap-3 px-6 py-4 border-b shrink-0"
          style={{
            borderColor: "var(--care-border)",
            background: "var(--care-surface)",
          }}
        >
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm"
            style={{ background: "var(--care-accent)" }}
          >
            C
          </div>
          <div>
            <h1 className="text-sm font-semibold">CARE Assessment Kit</h1>
            <p
              className="text-xs"
              style={{ color: "var(--care-text-secondary)" }}
            >
              Terrene Foundation
            </p>
          </div>
        </header>

        {/* Progress bar */}
        <ProgressBar progress={progress} phase={phase} />

        {/* Messages */}
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto px-6 py-4 chat-scroll"
        >
          {messages.map((msg, i) => (
            <ChatMessage
              key={i}
              role={msg.role}
              content={msg.content}
              isStreaming={
                isStreaming &&
                i === messages.length - 1 &&
                msg.role === "assistant"
              }
            />
          ))}

          {/* Config download button when complete */}
          {isComplete && sessionId && <ConfigDownload sessionId={sessionId} />}

          {error && (
            <div
              className="rounded-lg px-4 py-3 text-sm my-2"
              style={{
                background: "var(--care-error)",
                color: "white",
                opacity: 0.9,
              }}
            >
              {error}
            </div>
          )}
        </div>

        {/* Input */}
        {!isComplete && (
          <ChatInput
            onSend={handleSend}
            disabled={isStreaming || !sessionId}
            voiceSupported={voice.isSupported}
            isListening={voice.isListening}
            voiceTranscript={voice.transcript}
            onVoiceStart={voice.startListening}
            onVoiceStop={voice.stopListening}
          />
        )}
      </div>

      {/* Side panel — shows org data and diagnosis when available */}
      <aside
        className="hidden lg:flex flex-col w-80 border-l shrink-0 overflow-y-auto"
        style={{
          borderColor: "var(--care-border)",
          background: "var(--care-surface)",
        }}
      >
        <div className="p-4">
          <h2
            className="text-xs font-semibold uppercase tracking-wider mb-4"
            style={{ color: "var(--care-text-secondary)" }}
          >
            Assessment Progress
          </h2>

          {/* Org data summary */}
          {orgData && (
            <div className="space-y-3 mb-6">
              <InfoRow label="Organization" value={orgData.org_name || "—"} />
              <InfoRow
                label="Departments"
                value={orgData.departments.toString()}
              />
              <InfoRow label="Teams" value={orgData.teams.toString()} />
              <InfoRow label="Roles" value={orgData.roles.toString()} />
              <InfoRow label="Bridges" value={orgData.bridges.toString()} />
              {orgData.gaps > 0 && (
                <InfoRow
                  label="Information gaps"
                  value={orgData.gaps.toString()}
                  warn
                />
              )}
            </div>
          )}

          {!orgData && (
            <p
              className="text-xs italic"
              style={{ color: "var(--care-text-secondary)" }}
            >
              Organization details will appear here as the conversation
              progresses.
            </p>
          )}

          {/* Maturity radar */}
          {diagnosis && (
            <div className="mt-6">
              <h2
                className="text-xs font-semibold uppercase tracking-wider mb-3"
                style={{ color: "var(--care-text-secondary)" }}
              >
                CARE Readiness
              </h2>
              <div
                className="text-center mb-2 text-2xl font-bold"
                style={{ color: "var(--care-accent)" }}
              >
                {diagnosis.overall_score.toFixed(1)}/5.0
              </div>
              <MaturityRadar dimensions={diagnosis.dimensions} />
            </div>
          )}
        </div>
      </aside>

      {/* Voice privacy dialog */}
      {voice.showPrivacyNotice && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div
            className="rounded-2xl p-6 max-w-md mx-4"
            style={{ background: "var(--care-surface)" }}
          >
            <h3 className="font-semibold mb-2">Voice Input Privacy Notice</h3>
            <p
              className="text-sm mb-4"
              style={{ color: "var(--care-text-secondary)" }}
            >
              Voice input uses your browser&apos;s speech recognition service,
              which may send audio data to external servers (such as Google) for
              processing.
            </p>
            <p
              className="text-sm mb-4"
              style={{ color: "var(--care-text-secondary)" }}
            >
              If you&apos;re discussing sensitive organizational information,
              you may prefer to use text input instead. You can switch between
              voice and text at any time.
            </p>
            <div className="flex gap-3">
              <button
                onClick={voice.acceptVoice}
                className="flex-1 px-4 py-2 rounded-lg text-sm font-medium text-white"
                style={{ background: "var(--care-accent)" }}
              >
                I understand, enable voice
              </button>
              <button
                onClick={voice.declineVoice}
                className="flex-1 px-4 py-2 rounded-lg text-sm font-medium border"
                style={{
                  borderColor: "var(--care-border)",
                  color: "var(--care-text)",
                }}
              >
                Use text only
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function InfoRow({
  label,
  value,
  warn,
}: {
  label: string;
  value: string;
  warn?: boolean;
}) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-xs" style={{ color: "var(--care-text-secondary)" }}>
        {label}
      </span>
      <span
        className="text-xs font-medium"
        style={{ color: warn ? "var(--care-warn)" : "var(--care-text)" }}
      >
        {value}
      </span>
    </div>
  );
}
