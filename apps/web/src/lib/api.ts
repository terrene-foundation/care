/** Typed API client for the CARE backend. */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface SessionInfo {
  session_id: string;
  welcome_message: string;
  state: string;
  progress: number;
}

export interface SessionStatus {
  session_id: string;
  state: string;
  phase: string;
  progress: number;
  message_count: number;
}

export interface OrgUpdate {
  org_name: string | null;
  departments: number;
  teams: number;
  roles: number;
  bridges: number;
  gaps: number;
}

export interface PactConfig {
  yaml_content: string;
  org_name: string;
}

export interface DiagnosisData {
  overall_score: number;
  overall_readiness: string;
  dimensions: {
    name: string;
    score: number;
    description: string;
    gaps: string[];
  }[];
  risks: {
    description: string;
    likelihood: string;
    impact: string;
    dimension: string;
  }[];
  gaps: { description: string; severity: string }[];
}

export interface RecommendationData {
  recommendations: {
    action: string;
    why: string;
    priority: string;
    phase: number;
    phase_name: string;
    dimension: string;
  }[];
}

export async function createSession(): Promise<SessionInfo> {
  const res = await fetch(`${API_BASE}/api/sessions`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to create session");
  return res.json();
}

export async function getSession(id: string): Promise<SessionStatus> {
  const res = await fetch(`${API_BASE}/api/sessions/${id}`);
  if (!res.ok) throw new Error("Failed to get session");
  return res.json();
}

export interface StreamCallbacks {
  onToken: (text: string) => void;
  onState: (state: { state: string; phase: string; progress: number }) => void;
  onOrgUpdate: (data: OrgUpdate) => void;
  onDone: () => void;
  onError: (error: string) => void;
}

export async function sendMessage(
  sessionId: string,
  content: string,
  callbacks: StreamCallbacks,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });

  if (!res.ok) {
    callbacks.onError("Failed to send message");
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        const eventType = line.slice(7).trim();
        // Next line should be data
        continue;
      }
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        try {
          const parsed = JSON.parse(data);
          // Determine event type from the data structure
          if ("text" in parsed) {
            callbacks.onToken(parsed.text);
          } else if ("state" in parsed && "phase" in parsed) {
            callbacks.onState(parsed);
          } else if ("departments" in parsed) {
            callbacks.onOrgUpdate(parsed);
          } else if ("message" in parsed) {
            callbacks.onError(parsed.message);
          }
        } catch {
          // Non-JSON data line, skip
        }
      }
    }
  }

  callbacks.onDone();
}

export async function downloadConfig(sessionId: string): Promise<PactConfig> {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/config`);
  if (!res.ok) throw new Error("Configuration not yet available");
  return res.json();
}

export async function getDiagnosis(sessionId: string): Promise<DiagnosisData> {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/diagnosis`);
  if (!res.ok) throw new Error("Diagnosis not yet available");
  return res.json();
}

export async function getRecommendations(
  sessionId: string,
): Promise<RecommendationData> {
  const res = await fetch(
    `${API_BASE}/api/sessions/${sessionId}/recommendations`,
  );
  if (!res.ok) throw new Error("Recommendations not yet available");
  return res.json();
}
