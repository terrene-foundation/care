# 5057: DM task submission UI

**Milestone**: M25 — DM Dashboard and E2E
**Priority**: Medium
**Effort**: Medium

## What

Form on the DM dashboard page to submit tasks to the DM team. Select a specific agent or use auto-routing. View task result, lifecycle state, and audit trail. Real-time status updates via WebSocket.

## Where

- `apps/web/app/dm/page.tsx` — add task submission form
- `apps/web/components/dm/TaskSubmitForm.tsx` — new component
- `apps/web/components/dm/TaskResult.tsx` — new component

## Evidence

- Can submit a task via the form
- Task routes to correct agent (or shows auto-route selection)
- Task result appears when complete (or shows HELD status with approval link)
- Audit trail for the task is visible

## Dependencies

- 5052 (DM API), 5056 (DM dashboard page)
