"use client";

import { Download, FileText } from "lucide-react";
import { useCallback, useState } from "react";
import { downloadConfig } from "@/lib/api";

interface ConfigDownloadProps {
  sessionId: string;
}

export function ConfigDownload({ sessionId }: ConfigDownloadProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const config = await downloadConfig(sessionId);
      const blob = new Blob([config.yaml_content], { type: "text/yaml" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${config.org_name.toLowerCase().replace(/\s+/g, "-")}-pact-config.yaml`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Download failed");
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  return (
    <div
      className="rounded-xl border p-4 mt-4"
      style={{
        borderColor: "var(--care-accent)",
        background: "var(--care-accent-bg)",
      }}
    >
      <div className="flex items-center gap-3 mb-3">
        <FileText size={20} style={{ color: "var(--care-accent)" }} />
        <span className="font-medium text-sm">Your PACT Configuration</span>
      </div>
      <p
        className="text-xs mb-3"
        style={{ color: "var(--care-text-secondary)" }}
      >
        This file contains your organization&apos;s governance configuration.
        Share it with your technical team to import into the PACT platform.
      </p>
      <button
        onClick={handleDownload}
        disabled={loading}
        className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white transition-opacity disabled:opacity-50"
        style={{ background: "var(--care-accent)" }}
      >
        <Download size={16} />
        {loading ? "Preparing..." : "Download PACT Configuration"}
      </button>
      {error && (
        <p className="text-xs mt-2" style={{ color: "var(--care-error)" }}>
          {error}
        </p>
      )}
    </div>
  );
}
