// Copyright 2026 Terrene Foundation
// Licensed under the Apache License, Version 2.0

/**
 * ShadowEnforcer dashboard page.
 *
 * Shows what AI agents WOULD do vs what they actually do -- the key insight
 * for trust posture upgrade decisions. The ShadowEnforcer runs verification
 * gradient evaluation in parallel with normal operations, collecting metrics
 * that provide empirical evidence for posture upgrades.
 *
 * Page structure:
 *   1. Agent selector dropdown (populated from teams/agents API)
 *   2. Shadow metric cards (total, auto_approved, flagged, held, blocked, rates)
 *   3. Pass rate gauge (circular SVG ring)
 *   4. Verification level distribution (stacked horizontal bar)
 *   5. Dimension trigger breakdown (horizontal bar chart)
 *   6. Upgrade eligibility card with blockers and recommendation
 *
 * Data sources:
 *   GET /api/v1/teams -- list team IDs
 *   GET /api/v1/teams/{team_id}/agents -- list agents per team
 *   GET /api/v1/shadow/{agent_id}/metrics -- ShadowMetrics
 *   GET /api/v1/shadow/{agent_id}/report -- ShadowReport
 */

"use client";

import { useState, useMemo } from "react";
import DashboardShell from "../../components/layout/DashboardShell";
import ErrorAlert from "../../components/ui/ErrorAlert";
import ShadowSkeleton from "./elements/ShadowSkeleton";
import ShadowMetricsCards from "./elements/ShadowMetricsCards";
import PassRateGauge from "./elements/PassRateGauge";
import VerificationDistribution from "./elements/VerificationDistribution";
import DimensionBreakdown from "./elements/DimensionBreakdown";
import UpgradeEligibility from "./elements/UpgradeEligibility";
import { useApi } from "../../lib/use-api";

// ---------------------------------------------------------------------------
// Agent option derived from real API data
// ---------------------------------------------------------------------------

interface AgentOption {
  agent_id: string;
  name: string;
  team_id: string;
  posture: string;
}

// ---------------------------------------------------------------------------
// Agent List Loader (fetches teams then agents per team)
// ---------------------------------------------------------------------------

/**
 * Custom hook that loads all agents across all teams.
 * Fetches the team list first, then fetches agents for each team
 * and flattens the results into a single array.
 */
function useAgentList(): {
  agents: AgentOption[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
} {
  const {
    data: teamsData,
    loading: teamsLoading,
    error: teamsError,
    refetch: teamsRefetch,
  } = useApi((client) => client.listTeams(), []);

  // Build a comma-separated team key so we can fetch agents when teams load
  const teamIds = teamsData?.teams ?? [];
  const teamKey = teamIds.join(",");

  const {
    data: agentsData,
    loading: agentsLoading,
    error: agentsError,
    refetch: agentsRefetch,
  } = useApi(
    async (client) => {
      if (teamIds.length === 0) {
        return { status: "ok" as const, data: { agents: [] }, error: null };
      }

      const allAgents: AgentOption[] = [];
      for (const teamId of teamIds) {
        const response = await client.listAgents(teamId);
        if (response.status === "ok" && response.data) {
          for (const agent of response.data.agents) {
            allAgents.push({
              agent_id: agent.agent_id,
              name: agent.name,
              team_id: teamId,
              posture: agent.posture,
            });
          }
        }
      }

      return {
        status: "ok" as const,
        data: { agents: allAgents },
        error: null,
      };
    },
    [teamKey],
  );

  const agents = agentsData?.agents ?? [];

  return {
    agents,
    loading: teamsLoading || agentsLoading,
    error: teamsError ?? agentsError,
    refetch: () => {
      teamsRefetch();
      agentsRefetch();
    },
  };
}

// ---------------------------------------------------------------------------
// Page Component
// ---------------------------------------------------------------------------

export default function ShadowPage() {
  const [selectedAgentId, setSelectedAgentId] = useState<string>("");

  // Load available agents from teams API
  const {
    agents,
    loading: agentsLoading,
    error: agentsError,
    refetch: agentsRefetch,
  } = useAgentList();

  // Auto-select the first agent once loaded (only if nothing is selected)
  const effectiveAgentId = useMemo(() => {
    if (selectedAgentId && agents.some((a) => a.agent_id === selectedAgentId)) {
      return selectedAgentId;
    }
    return agents.length > 0 ? agents[0].agent_id : "";
  }, [selectedAgentId, agents]);

  // Fetch shadow metrics for the selected agent
  const {
    data: metricsData,
    loading: metricsLoading,
    error: metricsError,
    refetch: metricsRefetch,
  } = useApi(
    (client) => {
      if (!effectiveAgentId) {
        return Promise.resolve({
          status: "ok" as const,
          data: null,
          error: null,
        });
      }
      return client.shadowMetrics(effectiveAgentId);
    },
    [effectiveAgentId],
  );

  // Fetch shadow report for the selected agent
  const {
    data: reportData,
    loading: reportLoading,
    error: reportError,
    refetch: reportRefetch,
  } = useApi(
    (client) => {
      if (!effectiveAgentId) {
        return Promise.resolve({
          status: "ok" as const,
          data: null,
          error: null,
        });
      }
      return client.shadowReport(effectiveAgentId);
    },
    [effectiveAgentId],
  );

  // Derived state
  const loading = agentsLoading || metricsLoading || reportLoading;
  const error = agentsError ?? metricsError ?? reportError;
  const selectedAgent = agents.find((a) => a.agent_id === effectiveAgentId);
  const hasData = metricsData !== null && reportData !== null;

  const handleRefetch = () => {
    agentsRefetch();
    metricsRefetch();
    reportRefetch();
  };

  return (
    <DashboardShell
      activePath="/shadow"
      title="ShadowEnforcer"
      breadcrumbs={[
        { label: "Dashboard", href: "/" },
        { label: "ShadowEnforcer" },
      ]}
      actions={
        <button
          onClick={handleRefetch}
          disabled={loading}
          className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-colors"
        >
          Refresh
        </button>
      }
    >
      <div className="space-y-6">
        {/* Page description */}
        <p className="text-sm text-gray-600">
          The ShadowEnforcer runs trust evaluation in parallel with normal agent
          operations. It records what WOULD happen under the current constraint
          configuration without blocking or modifying any actions. These metrics
          provide empirical evidence for trust posture upgrade decisions.
        </p>

        {/* Error */}
        {error && <ErrorAlert message={error} onRetry={handleRefetch} />}

        {/* Agent selector */}
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-4">
          <label
            htmlFor="agent-selector"
            className="text-sm font-medium text-gray-700"
          >
            Select Agent
          </label>
          {agentsLoading ? (
            <div className="h-10 w-80 animate-pulse rounded-lg bg-gray-200" />
          ) : agents.length === 0 ? (
            <span className="text-sm text-gray-500">
              No agents available. Ensure teams and agents are configured.
            </span>
          ) : (
            <select
              id="agent-selector"
              value={effectiveAgentId}
              onChange={(e) => setSelectedAgentId(e.target.value)}
              className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:w-80"
            >
              {agents.map((agent) => (
                <option key={agent.agent_id} value={agent.agent_id}>
                  {agent.name} ({agent.team_id} /{" "}
                  {agent.posture.replace(/_/g, " ")})
                </option>
              ))}
            </select>
          )}
          {selectedAgent && (
            <span className="text-xs text-gray-400">
              Current posture:{" "}
              <span className="font-medium text-gray-600">
                {selectedAgent.posture.replace(/_/g, " ")}
              </span>
            </span>
          )}
        </div>

        {/* Loading state */}
        {(metricsLoading || reportLoading) && effectiveAgentId && (
          <ShadowSkeleton />
        )}

        {/* No data state */}
        {!loading && effectiveAgentId && !hasData && (
          <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-gray-500">
            No shadow evaluation data available for this agent. The
            ShadowEnforcer may not have recorded any evaluations yet.
          </div>
        )}

        {/* Dashboard content */}
        {!metricsLoading && !reportLoading && hasData && (
          <>
            {/* Metrics cards */}
            <ShadowMetricsCards metrics={metricsData} />

            {/* Pass rate gauge + Verification distribution */}
            <div className="grid gap-6 lg:grid-cols-2">
              <PassRateGauge
                passRate={reportData.pass_rate}
                totalEvaluations={reportData.total_evaluations}
                periodDays={reportData.evaluation_period_days}
              />
              <VerificationDistribution metrics={metricsData} />
            </div>

            {/* Dimension trigger breakdown */}
            <DimensionBreakdown
              dimensionTriggerCounts={metricsData.dimension_trigger_counts}
              totalEvaluations={metricsData.total_evaluations}
            />

            {/* Upgrade eligibility */}
            <UpgradeEligibility
              report={reportData}
              agentId={effectiveAgentId}
              agentName={selectedAgent?.name ?? "Agent"}
              currentPosture={selectedAgent?.posture ?? "pseudo_agent"}
              onPostureUpgraded={handleRefetch}
            />
          </>
        )}
      </div>
    </DashboardShell>
  );
}
