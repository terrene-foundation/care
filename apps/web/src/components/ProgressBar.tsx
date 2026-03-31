"use client";

interface ProgressBarProps {
  progress: number;
  phase: string;
}

const PHASES = ["Assess", "Diagnose", "Recommend", "Generate", "Complete"];

export function ProgressBar({ progress, phase }: ProgressBarProps) {
  return (
    <div
      className="w-full px-6 py-3 border-b"
      style={{ borderColor: "var(--care-border)" }}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex gap-1">
          {PHASES.map((p) => (
            <span
              key={p}
              className="text-xs font-medium px-2 py-0.5 rounded-full transition-colors"
              style={{
                background: p === phase ? "var(--care-accent)" : "transparent",
                color: p === phase ? "white" : "var(--care-text-secondary)",
              }}
            >
              {p}
            </span>
          ))}
        </div>
        <span
          className="text-xs"
          style={{ color: "var(--care-text-secondary)" }}
        >
          {progress}%
        </span>
      </div>
      <div
        className="w-full h-1.5 rounded-full overflow-hidden"
        style={{ background: "var(--care-border)" }}
      >
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{
            width: `${progress}%`,
            background: "var(--care-accent)",
          }}
        />
      </div>
    </div>
  );
}
