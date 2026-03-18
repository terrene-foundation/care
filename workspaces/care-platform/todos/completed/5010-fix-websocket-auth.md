# 5010: Fix WebSocket auth to prefer protocol header

**Milestone**: M14 — Frontend Fixes
**Priority**: Medium
**Effort**: Small

## What

Update frontend WebSocket connection code to prefer `Sec-WebSocket-Protocol: bearer.<token>` over query parameter auth. The server logs a warning on query-parameter fallback — eliminating this warning cleans up server logs.

## Where

- `apps/web/components/NotificationListener.tsx` — update WebSocket connection
- `apps/web/components/ActivityFeed.tsx` — update WebSocket connection
- `apps/web/components/DashboardShell.tsx` — update WebSocket connection

## Evidence

- No WebSocket auth warnings in server logs
- WebSocket connections still authenticate successfully
- Real-time features (notifications, activity feed) still work

## Dependencies

- None (independent frontend fix)
