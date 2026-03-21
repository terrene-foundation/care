# REST API Reference

The PACT exposes a REST API for dashboard integration and programmatic access. All endpoints require Bearer token authentication unless noted otherwise.

## Authentication

Include the API token in the `Authorization` header:

```
Authorization: Bearer <your-token>
```

Set the token via `CARE_API_TOKEN` environment variable. In dev mode (`CARE_DEV_MODE=true`), an empty token is accepted.

## Base URL

Default: `http://localhost:8000`

Configure via `CARE_API_HOST` and `CARE_API_PORT` environment variables.

---

## Health & Readiness

### `GET /health`

No authentication required. Returns service status and component health.

```json
{
  "status": "healthy",
  "service": "pact",
  "version": "0.1.0",
  "components": {
    "api": "ok",
    "trust_store": "ok",
    "database": "ok"
  }
}
```

### `GET /ready`

No authentication required. Returns readiness status for load balancers.

---

## Teams & Agents

### `GET /api/v1/teams`

List all active team IDs.

### `GET /api/v1/teams/{team_id}/agents`

List all agents in a team with their status, posture, and role.

### `GET /api/v1/agents/{agent_id}/status`

Get detailed agent status including posture, capabilities, and constraint envelope.

### `GET /api/v1/agents/{agent_id}/posture-history`

Get posture change history for an agent. Returns chronological records of posture upgrades/downgrades with reasons and triggers.

---

## Approval Queue

### `GET /api/v1/held-actions`

List all pending approval requests with urgency levels and context.

### `POST /api/v1/agents/{agent_id}/approve/{action_id}`

Approve a held action. Body: `{"notes": "optional approval notes"}`

### `POST /api/v1/agents/{agent_id}/reject/{action_id}`

Reject a held action. Body: `{"reason": "rejection reason"}`

---

## Trust & Verification

### `GET /api/v1/trust-chains`

List all trust chains in the system.

### `GET /api/v1/trust-chains/{agent_id}`

Get the complete trust chain for an agent — from genesis record through delegation chain.

### `GET /api/v1/envelopes/{envelope_id}`

Get constraint envelope details with all five CARE dimensions (financial, operational, temporal, data access, communication).

### `GET /api/v1/verification/stats`

Get verification gradient counts by level: AUTO_APPROVED, FLAGGED, HELD, BLOCKED, and total.

---

## ShadowEnforcer

### `GET /api/v1/shadow/{agent_id}/metrics`

Get shadow evaluation metrics for an agent: total evaluations, pass rate, flag rate, block rate, and dimension breakdown.

### `GET /api/v1/shadow/{agent_id}/report`

Get a full shadow report including upgrade eligibility determination and evidence data.

---

## Cost Tracking

### `GET /api/v1/cost/report`

Get API cost report with daily trends, per-agent breakdown, and budget utilization.

---

## Cross-Functional Bridges

### `POST /api/v1/bridges`

Create a new cross-functional bridge between two teams.

### `GET /api/v1/bridges`

List all bridges with their status and team connections.

### `GET /api/v1/bridges/{bridge_id}`

Get bridge details including constraint intersection and sharing policies.

### `PUT /api/v1/bridges/{bridge_id}/approve`

Approve a pending bridge (source or target team approval).

### `POST /api/v1/bridges/{bridge_id}/suspend`

Suspend an active bridge.

### `POST /api/v1/bridges/{bridge_id}/close`

Close a bridge permanently.

### `GET /api/v1/bridges/team/{team_id}`

List all bridges involving a specific team.

### `GET /api/v1/bridges/{bridge_id}/audit`

Get audit trail for a bridge.

---

## Workspaces

### `GET /api/v1/workspaces`

List all workspaces with their paths and descriptions.

---

## Monitoring

### `GET /metrics`

No authentication required. Returns Prometheus-format metrics for scraping.

---

## WebSocket

### `WS /ws`

Real-time event stream. Authenticate via `Sec-WebSocket-Protocol: bearer.<token>`.

Events include: agent actions, approval requests, posture changes, bridge updates, and system alerts.

---

## Rate Limiting

- GET endpoints: 60 requests/minute (configurable via `CARE_RATE_LIMIT_GET`)
- POST endpoints: 20 requests/minute (configurable via `CARE_RATE_LIMIT_POST`)

Rate limit headers are included in responses: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
