# Flutter App — Master Roadmap

**Created**: 2026-03-16
**Status**: IN PROGRESS
**Scope**: 30 tasks across 5 milestones
**Targets**: iOS, iPadOS, Android, Android tablet, macOS desktop, Windows desktop

---

## M1: Foundation (7 tasks)

| #    | Task                                                         | Priority | Effort |
| ---- | ------------------------------------------------------------ | -------- | ------ |
| F-01 | Flutter project setup (6 targets, pubspec, folder structure) | Critical | Medium |
| F-02 | Dart data models (28 models with Freezed)                    | Critical | Large  |
| F-03 | Dio API client (34 methods)                                  | Critical | Large  |
| F-04 | WebSocket client                                             | High     | Medium |
| F-05 | Auth system (secure storage, login/logout)                   | Critical | Medium |
| F-06 | GoRouter setup (19 routes, auth guard, shell)                | High     | Medium |
| F-07 | Design system (Material 3, CARE colors, dark mode)           | High     | Medium |

## M2: Core Screens (7 tasks)

| #    | Task                                                | Priority | Effort |
| ---- | --------------------------------------------------- | -------- | ------ |
| F-08 | Login screen                                        | Critical | Medium |
| F-09 | Dashboard overview (stat cards, activity, gradient) | Critical | Large  |
| F-10 | Agents list + detail                                | High     | Large  |
| F-11 | Approval queue + approve/reject flow                | Critical | Large  |
| F-12 | ShadowEnforcer dashboard                            | High     | Large  |
| F-13 | DM Team + task submission                           | High     | Medium |
| F-14 | Cost report                                         | Medium   | Medium |

## M3: Secondary Screens (8 tasks)

| #    | Task                                               | Priority | Effort |
| ---- | -------------------------------------------------- | -------- | ------ |
| F-15 | Trust chains                                       | Medium   | Medium |
| F-16 | Constraint envelopes (list + detail)               | Medium   | Medium |
| F-17 | Bridges (list + detail + create)                   | Medium   | Large  |
| F-18 | Workspaces                                         | Medium   | Small  |
| F-19 | Audit trail (filters, pagination, export)          | Medium   | Large  |
| F-20 | Organization structure                             | Medium   | Medium |
| F-21 | Verification stats                                 | Medium   | Small  |
| F-22 | Dashboard shell (responsive: phone/tablet/desktop) | High     | Large  |

## M4: Platform Features (4 tasks)

| #    | Task                                                  | Priority | Effort |
| ---- | ----------------------------------------------------- | -------- | ------ |
| F-23 | Dark mode (system + manual toggle)                    | Medium   | Small  |
| F-24 | Responsive layouts (phone/tablet/desktop breakpoints) | High     | Medium |
| F-25 | Pull-to-refresh + connection status banner            | Medium   | Small  |
| F-26 | Settings screen (server URL, theme, about)            | Low      | Small  |

## M5: Testing (4 tasks)

| #    | Task                                      | Priority | Effort |
| ---- | ----------------------------------------- | -------- | ------ |
| F-27 | Widget tests (all 19 screens)             | High     | Large  |
| F-28 | Integration tests (API client, auth flow) | High     | Medium |
| F-29 | Golden tests (design system components)   | Medium   | Medium |
| F-30 | Red team validation                       | High     | Medium |
