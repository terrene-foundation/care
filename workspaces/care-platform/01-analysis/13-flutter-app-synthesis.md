# Flutter App Analysis: Synthesis

**Date**: 2026-03-16
**Inputs**: flutter-specialist, uiux-designer, requirements-analyst
**Scope**: Native app for iOS, iPadOS, Android, Android tablet, macOS desktop, Windows desktop

---

## What We're Building

A Flutter native client for the CARE Platform that provides the full governance dashboard across 6 targets. The app gives operators mobile access to agent management, approval queues, ShadowEnforcer metrics, DM team task submission, and cost tracking — all backed by the existing REST API.

## Architecture Decisions

| Decision         | Choice                        | Why                                                                   |
| ---------------- | ----------------------------- | --------------------------------------------------------------------- |
| State management | Riverpod 2.x                  | Type-safe, AsyncValue for loading/error/success, provider families    |
| Navigation       | GoRouter                      | Shell routes, auth guards, deep linking                               |
| HTTP client      | Dio                           | Interceptors for auth, retry, cancellation                            |
| Models           | Freezed + json_serializable   | 28 immutable data classes with JSON round-tripping                    |
| Responsive       | 3-tier (phone/tablet/desktop) | Bottom nav < 600dp, NavigationRail 600-1200dp, full sidebar >= 1200dp |
| Storage          | flutter_secure_storage        | Platform-native encrypted token storage                               |
| Charts           | fl_chart                      | Open source, handles bar + line charts                                |
| Shared code      | 92-95%                        | Only nav shell, storage adapter, and window chrome differ             |

## Screen Inventory (19 screens)

Priority order for implementation:

1. **MVP**: Login, Dashboard, Approvals, Agents (4 screens — enough to clear approval queue from phone)
2. **Monitoring**: ShadowEnforcer, Cost Report, DM Team, Verification (4 screens)
3. **Full parity**: Trust Chains, Envelopes, Bridges, Workspaces, Audit, Org (8+ screens)

## Effort Estimate

30 tasks across 5 milestones. ~30 working days total.

| Milestone             | Focus                                                                  | Tasks  | Effort       |
| --------------------- | ---------------------------------------------------------------------- | ------ | ------------ |
| M1: Foundation        | Project setup, models, API client, auth, theme                         | 7      | 7 days       |
| M2: Core Screens      | Login, dashboard, agents, approvals, shadow, DM, cost                  | 7      | 9 days       |
| M3: Secondary Screens | Trust chains, envelopes, bridges, workspaces, audit, org, verification | 8      | 6 days       |
| M4: Platform Features | Dark mode, responsive, pull-to-refresh, settings                       | 4      | 4 days       |
| M5: Testing           | Widget tests, integration tests, golden tests                          | 4      | 4 days       |
| **Total**             |                                                                        | **30** | **~30 days** |
