# 5025: Add Prometheus metrics endpoint

**Milestone**: M18 — Production Hardening
**Priority**: Medium
**Effort**: Medium

## What

Add `/metrics` endpoint exposing Prometheus-format metrics: request counts, latencies, approval queue depth, trust chain stats, active agents, error rates.

## Where

- `src/pact/api/server.py` — add `/metrics` endpoint
- `src/pact/observability/` — add metrics collection module

## Evidence

- `GET /metrics` returns Prometheus text format
- Metrics include request_count, request_latency_seconds, approval_queue_depth, active_agents
- Prometheus can scrape the endpoint

## Dependencies

- None (can start independently)
