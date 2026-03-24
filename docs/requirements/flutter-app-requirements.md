# PACT Flutter App -- Requirements Analysis

## Executive Summary

- **Feature**: Cross-platform Flutter app with full feature parity to the Next.js web dashboard
- **Platforms**: iOS, iPadOS, Android, Android tablet, macOS desktop, Windows desktop (6 targets)
- **Complexity**: High -- 18 screens, 35+ API methods, WebSocket real-time, responsive layouts across phone/tablet/desktop
- **Risk Level**: Medium -- backend API and data models are well-defined; no API changes required
- **Estimated Effort**: 27--35 working days across 5 milestones

---

## Source Inventory

The following existing artifacts define the scope:

| Artifact                          | Location                                                                   | What it defines                                           |
| --------------------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------- |
| REST API (30+ endpoints)          | `/Users/esperie/repos/terrene/care/docs/rest-api.md`                       | All backend endpoints                                     |
| TypeScript data models (28 types) | `/Users/esperie/repos/terrene/care/apps/web/types/pact.ts`                 | Every data shape                                          |
| API client (35 methods)           | `/Users/esperie/repos/terrene/care/apps/web/lib/api.ts`                    | Client method signatures, error classes, WebSocket client |
| Auth context                      | `/Users/esperie/repos/terrene/care/apps/web/lib/auth-context.tsx`          | Auth flow, token storage, user roles                      |
| Notification context              | `/Users/esperie/repos/terrene/care/apps/web/lib/notification-context.tsx`  | Event-to-notification mapping, priority levels            |
| Sidebar navigation (12 items)     | `/Users/esperie/repos/terrene/care/apps/web/components/layout/Sidebar.tsx` | Navigation structure and icons                            |
| 18 page files                     | `/Users/esperie/repos/terrene/care/apps/web/app/**/page.tsx`               | Screen layouts and data flows                             |
| Existing Flutter scaffold         | `/Users/esperie/repos/terrene/care/apps/mobile/`                           | Placeholder project (pubspec + main.dart)                 |

---

## ADR-001: Flutter App Architecture

### Status

Proposed

### Context

The PACT has an existing web dashboard (Next.js, 18 pages) and a complete REST API (30+ endpoints plus WebSocket). A Flutter app is needed to provide the same governance oversight capabilities across iOS, iPadOS, Android, Android tablet, macOS desktop, and Windows desktop. A placeholder Flutter project already exists at `apps/mobile/`.

The app is a dashboard client -- it reads and writes data through the existing API. There is no offline-first requirement. The primary users are governance officers who need to approve/reject held actions, monitor agent postures, and review trust chains on the go.

### Decision

1. **State management**: Riverpod 2.x -- type-safe, testable, supports async providers. Preferred over BLoC (too much boilerplate for a dashboard) and Provider (less testable).

2. **Routing**: GoRouter -- declarative, supports deep linking (needed for push notification navigation later), redirect guards for auth.

3. **HTTP client**: Dio -- interceptors for auth token injection, timeout handling, retry logic, request/response logging in debug mode. Mirrors the TypeScript CareApiClient pattern.

4. **WebSocket**: web_socket_channel -- cross-platform, works on all 6 targets. Reconnection logic mirrors the TypeScript CareWebSocketClient.

5. **Secure storage**: flutter_secure_storage -- Keychain on iOS/macOS, EncryptedSharedPreferences on Android, Windows Credential Locker on Windows.

6. **Design system**: Material 3 with custom ColorScheme and TextTheme. Dark mode via ThemeMode toggle. Adaptive layouts using LayoutBuilder breakpoints (compact < 600dp, medium 600--840dp, expanded > 840dp).

7. **Project structure**: Feature-first with shared core layer.

### Consequences

#### Positive

- Riverpod + GoRouter is the most common modern Flutter architecture -- easy to hire for
- Dio interceptors give a clean equivalent to the TypeScript request() helper
- Material 3 adaptive widgets handle phone/tablet/desktop differences automatically

#### Negative

- Riverpod has a learning curve for developers used to setState or BLoC
- Six platform targets increase testing surface area

---

## Complete Task Breakdown

### Milestone 1: Foundation (Days 1--6)

Everything needed before any screen can be built. All subsequent milestones depend on this.

---

#### F-01: Flutter project setup (6 platform targets)

**Effort**: Medium (1.5 days)
**Dependencies**: None (starting point)

**What to do**:

- Rebuild the existing `apps/mobile/` scaffold with `flutter create` for all 6 targets (ios, android, macos, windows, plus existing web stub is out of scope)
- Update `pubspec.yaml` with all dependencies:
  - `flutter_riverpod` (^2.5.0)
  - `go_router` (^14.0.0)
  - `dio` (^5.4.0)
  - `web_socket_channel` (^3.0.0)
  - `flutter_secure_storage` (^9.2.0)
  - `json_annotation` (^4.9.0)
  - `freezed_annotation` (^2.4.0)
  - `intl` (^0.19.0)
  - `fl_chart` (^0.68.0) -- for verification gradient bars, cost charts, pass rate gauges
- Dev dependencies: `build_runner`, `json_serializable`, `freezed`, `flutter_lints`, `mocktail`
- Configure analysis_options.yaml with strict rules
- Set up directory structure:
  ```
  lib/
    app.dart                    # MaterialApp.router root
    main.dart                   # Entry point
    core/
      api/                      # Dio client, interceptors, error types
      models/                   # Dart data classes (freezed)
      providers/                # Riverpod providers
      router/                   # GoRouter configuration
      theme/                    # ColorScheme, TextTheme, dark mode
      websocket/                # WebSocket client
    features/
      auth/                     # Login screen, auth provider
      dashboard/                # Overview screen
      agents/                   # List + detail
      approvals/                # Queue + approve/reject
      shadow/                   # ShadowEnforcer dashboard
      dm/                       # DM team + task submission
      cost/                     # Cost report
      trust_chains/             # List + detail
      envelopes/                # List + detail
      bridges/                  # List + detail + create
      workspaces/               # List
      audit/                    # Audit trail
      org/                      # Organization structure
      verification/             # Verification stats
      settings/                 # Theme toggle, server URL, logout
    shared/
      widgets/                  # Reusable UI components
      extensions/               # Dart extensions
  ```
- Platform-specific setup: iOS Info.plist (NSAppTransportSecurity for dev), Android network_security_config.xml, macOS entitlements for network access, Windows runner configuration
- Verify `flutter run` works on at least one target

**Acceptance criteria**: `flutter analyze` passes with zero warnings. `flutter run` launches on all 6 targets showing a placeholder screen.

---

#### F-02: Dart data models (28 types, matching TypeScript)

**Effort**: Medium (1 day)
**Dependencies**: F-01

**What to do**:
Port every type from `apps/web/types/pact.ts` to Dart using `freezed` + `json_serializable`. The complete type inventory:

**Enums** (8):
| TypeScript | Dart enum |
|---|---|
| `VerificationLevel` | `VerificationLevel { autoApproved, flagged, held, blocked }` |
| `TrustPosture` | `TrustPosture { pseudoAgent, supervised, sharedPlanning, continuousInsight, delegated }` |
| `AgentStatus` | `AgentStatus { active, suspended, revoked, inactive }` |
| `WorkspaceState` | `WorkspaceState { provisioning, active, archived, decommissioned }` |
| `WorkspacePhase` | `WorkspacePhase { analyze, plan, implement, validate, codify }` |
| `BridgeType` | `BridgeType { standing, scoped, adHoc }` |
| `BridgeStatus` | `BridgeStatus { pending, negotiating, active, suspended, expired, closed, revoked }` |
| `DmTaskStatus` | `DmTaskStatus { pending, routing, executing, complete, held, failed }` |

**Data classes** (20):
| TypeScript interface | Dart class | Fields |
|---|---|---|
| `ApiResponse<T>` | `ApiResponse<T>` | status, data, error |
| `TrustChainSummary` | `TrustChainSummary` | agent_id, name, team_id, posture, status |
| `TrustChainDetail` | `TrustChainDetail` | + role, capabilities |
| `FinancialConstraint` | `FinancialConstraint` | max_spend_usd, api_cost_budget_usd, requires_approval_above_usd |
| `OperationalConstraint` | `OperationalConstraint` | allowed_actions, blocked_actions, max_actions_per_day |
| `TemporalConstraint` | `TemporalConstraint` | active_hours_start/end, timezone, blackout_periods |
| `DataAccessConstraint` | `DataAccessConstraint` | read_paths, write_paths, blocked_data_types |
| `CommunicationConstraint` | `CommunicationConstraint` | internal_only, allowed_channels, external_requires_approval |
| `ConstraintEnvelope` | `ConstraintEnvelope` | envelope_id, description, financial, operational, temporal, data_access, communication |
| `Workspace` | `Workspace` | id, path, description, state, phase, team_id |
| `Bridge` | `Bridge` | bridge_id, bridge_type, source_team_id, target_team_id, purpose, status, created_at |
| `BridgeDetail` | `BridgeDetail` | + all detail fields (permissions, payloads, approval state, replacement chain) |
| `BridgePermissions` | `BridgePermissions` | read_paths, write_paths, message_types, requires_attribution |
| `CreateBridgeRequest` | `CreateBridgeRequest` | bridge_type, source/target_team_id, purpose, permissions, valid_days, request_payload, created_by |
| `BridgeAuditEntry` | `BridgeAuditEntry` | agent_id, path, access_type, timestamp |
| `BridgeAuditResponse` | `BridgeAuditResponse` | bridge_id, entries, total, limit, offset |
| `VerificationStats` | `VerificationStats` | AUTO_APPROVED, FLAGGED, HELD, BLOCKED, total |
| `EnvelopeSummary` | `EnvelopeSummary` | envelope_id, description, agent_id, team_id |
| `AuditAnchor` | `AuditAnchor` | anchor_id, agent_id, agent_name, team_id, action, verification_level, timestamp, details |
| `PostureChange` | `PostureChange` | from_posture, to_posture, reason, changed_at, changed_by |
| `AgentDetail` | `AgentDetail` | agent_id, name, role, team_id, posture, status, capabilities, envelope_id, created_at, last_active_at, posture_history |
| `ShadowMetrics` | `ShadowMetrics` | agent_id, total_evaluations, auto_approved_count, flagged_count, held_count, blocked_count, dimension_trigger_counts, window_start/end, previous_pass_rate |
| `ShadowReport` | `ShadowReport` | agent_id, evaluation_period_days, total_evaluations, pass_rate, block_rate, hold_rate, flag_rate, dimension_breakdown, upgrade_eligible, upgrade_blockers, recommendation |
| `DmAgentSummary` | `DmAgentSummary` | agent_id, name, role, posture, status, actions_today, approval_rate |
| `DmStatus` | `DmStatus` | team_id, agents, total_actions_today, overall_approval_rate, active_agent_count, pending_task_count |
| `DmTask` | `DmTask` | task_id, description, target_agent, status, result, created_at, completed_at |
| `PlatformEvent` | `PlatformEvent` | event_id, event_type, data, source_agent_id, source_team_id, timestamp |
| `EventType` | `EventType` enum | audit_anchor, held_action, posture_change, bridge_status, verification_result, workspace_transition |

**JSON key mapping**: Use `@JsonKey(name: 'snake_case')` annotations. The API returns snake_case; Dart conventions use camelCase.

**Acceptance criteria**: `build_runner` generates serialization code. Every model can round-trip through `toJson()` / `fromJson()` using sample API response data.

---

#### F-03: Dart API client (35 methods, matching TypeScript)

**Effort**: Large (1.5 days)
**Dependencies**: F-02

**What to do**:
Build `CareApiClient` in Dart using Dio, mirroring every method in `apps/web/lib/api.ts`. The client must handle:

**Configuration**:

- `baseUrl` (from environment/settings)
- `token` (from secure storage, injected via interceptor)
- `timeoutMs` (default 10000)

**Error types** (mirror TypeScript):

- `ApiError` (statusCode, responseBody) -- for HTTP 4xx/5xx
- `NetworkError` (cause) -- for connection failures, timeouts

**Dio interceptor**:

- Auth interceptor: injects `Authorization: Bearer <token>` on every request
- Error interceptor: converts Dio errors to `ApiError` / `NetworkError`
- Logging interceptor (debug only)

**Methods (35 total)**:

| #   | TypeScript method                 | Dart method                                                                                   | HTTP | Path                                          |
| --- | --------------------------------- | --------------------------------------------------------------------------------------------- | ---- | --------------------------------------------- |
| 1   | `health()`                        | `health()`                                                                                    | GET  | `/health`                                     |
| 2   | `listTeams()`                     | `listTeams()`                                                                                 | GET  | `/api/v1/teams`                               |
| 3   | `listAgents(teamId)`              | `listAgents(String teamId)`                                                                   | GET  | `/api/v1/teams/{teamId}/agents`               |
| 4   | `agentStatus(agentId)`            | `agentStatus(String agentId)`                                                                 | GET  | `/api/v1/agents/{agentId}/status`             |
| 5   | `approveAction(...)`              | `approveAction(String agentId, String actionId, String approverId, {String? reason})`         | POST | `/api/v1/agents/{agentId}/approve/{actionId}` |
| 6   | `rejectAction(...)`               | `rejectAction(String agentId, String actionId, String approverId, {String? reason})`          | POST | `/api/v1/agents/{agentId}/reject/{actionId}`  |
| 7   | `heldActions()`                   | `heldActions()`                                                                               | GET  | `/api/v1/held-actions`                        |
| 8   | `costReport(params?)`             | `costReport({String? teamId, String? agentId, int? days})`                                    | GET  | `/api/v1/cost/report`                         |
| 9   | `listTrustChains()`               | `listTrustChains()`                                                                           | GET  | `/api/v1/trust-chains`                        |
| 10  | `getTrustChainDetail(agentId)`    | `getTrustChainDetail(String agentId)`                                                         | GET  | `/api/v1/trust-chains/{agentId}`              |
| 11  | `listEnvelopes()`                 | `listEnvelopes()`                                                                             | GET  | `/api/v1/envelopes`                           |
| 12  | `getEnvelope(envelopeId)`         | `getEnvelope(String envelopeId)`                                                              | GET  | `/api/v1/envelopes/{envelopeId}`              |
| 13  | `listAuditAnchors(params?)`       | `listAuditAnchors({String? agentId, String? level, String? startDate, String? endDate})`      | GET  | `/api/v1/audit`                               |
| 14  | `getTeamAudit(teamId)`            | `getTeamAudit(String teamId)`                                                                 | GET  | `/api/v1/audit/team/{teamId}`                 |
| 15  | `getAgentDetail(agentId)`         | `getAgentDetail(String agentId)`                                                              | GET  | `/api/v1/agents/{agentId}`                    |
| 16  | `suspendAgent(...)`               | `suspendAgent(String agentId, String reason, String suspendedBy)`                             | POST | `/api/v1/agents/{agentId}/suspend`            |
| 17  | `revokeAgent(...)`                | `revokeAgent(String agentId, String reason, String revokedBy)`                                | POST | `/api/v1/agents/{agentId}/revoke`             |
| 18  | `changePosture(...)`              | `changePosture(String agentId, String newPosture, String reason, String changedBy)`           | PUT  | `/api/v1/agents/{agentId}/posture`            |
| 19  | `listWorkspaces()`                | `listWorkspaces()`                                                                            | GET  | `/api/v1/workspaces`                          |
| 20  | `listBridges()`                   | `listBridges()`                                                                               | GET  | `/api/v1/bridges`                             |
| 21  | `getBridge(bridgeId)`             | `getBridge(String bridgeId)`                                                                  | GET  | `/api/v1/bridges/{bridgeId}`                  |
| 22  | `createBridge(data)`              | `createBridge(CreateBridgeRequest data)`                                                      | POST | `/api/v1/bridges`                             |
| 23  | `approveBridge(...)`              | `approveBridge(String bridgeId, String side, String approverId)`                              | PUT  | `/api/v1/bridges/{bridgeId}/approve`          |
| 24  | `suspendBridge(...)`              | `suspendBridge(String bridgeId, String reason)`                                               | POST | `/api/v1/bridges/{bridgeId}/suspend`          |
| 25  | `closeBridge(...)`                | `closeBridge(String bridgeId, String reason)`                                                 | POST | `/api/v1/bridges/{bridgeId}/close`            |
| 26  | `listBridgesByTeam(teamId)`       | `listBridgesByTeam(String teamId)`                                                            | GET  | `/api/v1/bridges/team/{teamId}`               |
| 27  | `bridgeAudit(...)`                | `bridgeAudit(String bridgeId, {String? startDate, String? endDate, int? limit, int? offset})` | GET  | `/api/v1/bridges/{bridgeId}/audit`            |
| 28  | `verificationStats()`             | `verificationStats()`                                                                         | GET  | `/api/v1/verification/stats`                  |
| 29  | `shadowMetrics(agentId)`          | `shadowMetrics(String agentId)`                                                               | GET  | `/api/v1/shadow/{agentId}/metrics`            |
| 30  | `shadowReport(agentId)`           | `shadowReport(String agentId)`                                                                | GET  | `/api/v1/shadow/{agentId}/report`             |
| 31  | `getDmStatus()`                   | `getDmStatus()`                                                                               | GET  | `/api/v1/dm/status`                           |
| 32  | `submitDmTask(...)`               | `submitDmTask(String description, {String? targetAgent})`                                     | POST | `/api/v1/dm/tasks`                            |
| 33  | `getDmTaskStatus(taskId)`         | `getDmTaskStatus(String taskId)`                                                              | GET  | `/api/v1/dm/tasks/{taskId}`                   |
| 34  | `getAgentPostureHistory(agentId)` | `getAgentPostureHistory(String agentId)`                                                      | GET  | `/api/v1/agents/{agentId}/posture-history`    |
| 35  | (not in TS)                       | `listEnvelopesSummary()`                                                                      | GET  | `/api/v1/envelopes`                           |

**Riverpod provider**: Expose `apiClientProvider` as a `Provider<CareApiClient>` that reads token from auth state.

**Acceptance criteria**: Every method returns the correct typed `ApiResponse<T>`. Unit tests verify serialization for at least one representative request/response per domain (agents, bridges, shadow, DM).

---

#### F-04: WebSocket client (real-time events)

**Effort**: Medium (0.5 day)
**Dependencies**: F-02

**What to do**:
Port `CareWebSocketClient` from TypeScript to Dart using `web_socket_channel`. Must include:

- Automatic reconnection with exponential backoff (matches TS: initial 1s, max 30s, 10 attempts, jitter)
- Auth via `Sec-WebSocket-Protocol: bearer.<token>` (matches TS implementation)
- Parse incoming JSON into `PlatformEvent` objects
- Stream-based API: `Stream<PlatformEvent> get events`
- Connection state stream: `Stream<WebSocketState> get stateChanges`
- `connect()`, `disconnect()` methods
- Event-to-notification conversion (port `eventToNotification()` from notification-context.tsx)

**Riverpod providers**:

- `webSocketProvider` -- manages lifecycle
- `platformEventsProvider` -- exposes event stream
- `notificationsProvider` -- converts events to notifications, stores in FIFO list (max 50), tracks unread count, pending approval count

**Acceptance criteria**: WebSocket connects, receives events, auto-reconnects after disconnection. Notification provider correctly maps all 6 event types to notification priorities.

---

#### F-05: Auth system (token storage, login/logout)

**Effort**: Medium (1 day)
**Dependencies**: F-03

**What to do**:
Port the auth flow from `auth-context.tsx`. The Flutter implementation needs:

**Secure storage**:

- Store token in `flutter_secure_storage` (Keychain/EncryptedSharedPrefs/Credential Locker)
- Store user name and role alongside token
- Storage keys: `PACT_API_TOKEN`, `PACT_USER_NAME`, `PACT_USER_ROLE`

**Auth state (Riverpod)**:

- `authProvider` -- `AsyncNotifier<AuthState>` that:
  - On init: reads from secure storage, hydrates state
  - `login(name, token, {remember})`: validates token via health check (same as TS), stores if valid
  - `logout()`: clears storage, resets state, navigates to login

**AuthState model**:

```dart
@freezed
class AuthState {
  const factory AuthState.unauthenticated() = _Unauthenticated;
  const factory AuthState.authenticated({
    required String name,
    required UserRole role,
    required String token,
  }) = _Authenticated;
  const factory AuthState.loading() = _Loading;
}
```

**User roles** (matching TS): `governance_officer`, `admin`, `auditor`, `operator`
**Default role**: `governance_officer` (same as web)

**GoRouter guard**: Redirect to `/login` when unauthenticated. Redirect to `/` when authenticated and on `/login`.

**Acceptance criteria**: User can log in with name + token. Token persists across app restarts. Logout clears all stored data. Invalid tokens show a clear error message.

---

#### F-06: Navigation and routing

**Effort**: Medium (0.5 day)
**Dependencies**: F-05

**What to do**:
Configure GoRouter with all 18 routes matching the web dashboard navigation:

| Route             | Screen                  | Sidebar label |
| ----------------- | ----------------------- | ------------- |
| `/login`          | LoginScreen             | (no sidebar)  |
| `/`               | DashboardOverviewScreen | Overview      |
| `/trust-chains`   | TrustChainsScreen       | Trust Chains  |
| `/envelopes`      | EnvelopesListScreen     | Envelopes     |
| `/envelopes/:id`  | EnvelopeDetailScreen    | (child)       |
| `/workspaces`     | WorkspacesScreen        | Workspaces    |
| `/agents`         | AgentsListScreen        | Agents        |
| `/agents/:id`     | AgentDetailScreen       | (child)       |
| `/dm`             | DmTeamScreen            | DM Team       |
| `/bridges`        | BridgesListScreen       | Bridges       |
| `/bridges/create` | BridgeCreateScreen      | (child)       |
| `/bridges/:id`    | BridgeDetailScreen      | (child)       |
| `/verification`   | VerificationScreen      | Verification  |
| `/shadow`         | ShadowScreen            | Shadow        |
| `/audit`          | AuditTrailScreen        | Audit Trail   |
| `/approvals`      | ApprovalsScreen         | Approvals     |
| `/cost-report`    | CostReportScreen        | Cost Report   |
| `/org`            | OrgStructureScreen      | Org Structure |

**Shell route**: Wrap all authenticated routes in a `ShellRoute` that provides the adaptive scaffold (sidebar on desktop/tablet, bottom navigation on phone).

**Adaptive navigation**:

- Phone (< 600dp): BottomNavigationBar with 5 primary items + "More" drawer
- Tablet (600--840dp): NavigationRail (collapsed sidebar)
- Desktop (> 840dp): Full sidebar (matches web `Sidebar.tsx` with 12 items)

**Acceptance criteria**: All 18 routes resolve. Auth redirect works. Deep links work on all platforms. Back navigation is correct.

---

#### F-07: Design system (theme, colors, typography)

**Effort**: Medium (1 day)
**Dependencies**: F-01

**What to do**:
Build the Material 3 theme matching the web dashboard CSS variables:

**Color tokens** (from web CSS):
| Token | Light | Dark | Usage |
|---|---|---|---|
| care-primary | Blue 600 (#2563EB) | Blue 400 | Primary actions, links |
| care-primary-dark | Blue 700 | Blue 300 | Hover states |
| care-primary-light | Blue 50 | Blue 900/20 | Backgrounds |
| care-muted | Gray 500 | Gray 400 | Secondary text |
| care-border | Gray 200 | Gray 700 | Borders |

**Verification gradient colors** (canonical CARE terminology):
| Level | Color | Light bg | Dark text |
|---|---|---|---|
| AUTO_APPROVED | Green 500 | Green 50 | Green 700 |
| FLAGGED | Yellow 500 | Yellow 50 | Yellow 700 |
| HELD | Orange 500 | Orange 50 | Orange 700 |
| BLOCKED | Red 500 | Red 50 | Red 700 |

**Trust posture colors**:
| Posture | Badge color |
|---|---|
| PSEUDO_AGENT | Gray 100/700 |
| SUPERVISED | Blue 100/700 |
| SHARED_PLANNING | Indigo 100/700 |
| CONTINUOUS_INSIGHT | Purple 100/700 |
| DELEGATED | Green 100/700 |

**Urgency colors**:
| Level | Color |
|---|---|
| critical | Red 600 |
| high | Orange 500 |
| medium | Yellow 500 |
| low | Gray 400 |

**Typography**: System font stack (San Francisco on Apple, Roboto on Android, Segoe UI on Windows). Use Material 3 text theme with sensible scale.

**Shared widgets**:

- `CareCard` -- rounded border, shadow, matches web `.card` class
- `StatCard` -- metric card with icon, value, label, sub-content (matches OverviewPage)
- `PostureBadge` -- colored chip for trust posture
- `StatusDot` -- green/yellow/gray dot for agent status
- `VerificationBadge` -- colored badge for verification level
- `UrgencyBadge` -- colored badge for action urgency
- `ErrorAlert` -- error display with retry button
- `LoadingSkeleton` -- shimmer loading placeholders
- `EmptyState` -- centered message with icon for no-data states
- `GaugeBar` -- horizontal progress bar with label (budget gauge, pass rate)
- `BridgeStatusBadge` -- colored badge for bridge lifecycle

**Dark mode**: Full ThemeData.dark() with all color tokens mapped. Toggle via `ThemeMode` stored in local preferences (not secure storage).

**Acceptance criteria**: Light and dark themes render correctly. All badge/status widgets show correct colors. Typography is consistent across platforms.

---

### Milestone 2: Core Screens (Days 7--15)

The screens that provide the most value to governance officers. These are the ones they will use daily.

---

#### C-01: Login screen

**Effort**: Small (0.5 day)
**Dependencies**: F-05, F-07

**What to do**:
Port `apps/web/app/login/page.tsx`. The screen must include:

- PACT branding (blue icon, title, tagline)
- Operator name text field (with validation)
- API token text field (obscured, with validation)
- "Remember me" checkbox (default on)
- Sign In button with loading spinner
- Error display for invalid token / connection failure
- Auto-redirect to dashboard if already authenticated

**Platform considerations**: On desktop, center the login card. On phones, full-width with padding.

**Acceptance criteria**: Login works against a running PACT backend. Invalid token shows an error. Credentials persist when "remember me" is checked.

---

#### C-02: Dashboard overview

**Effort**: Large (1.5 days)
**Dependencies**: F-03, F-04, F-07

**What to do**:
Port `apps/web/app/page.tsx`. Three-row layout:

**Row 1 -- Stat cards** (4 cards in a grid):

1. Active Agents (count, trend indicator, link to /agents)
2. Pending Approvals (count, critical/standard breakdown, link to /approvals)
3. Verification Rate (percentage auto-approved, link to /verification)
4. API Spend Today (dollar amount, budget gauge bar, link to /cost-report)

**Row 2 -- Two columns**:

- Left (60%): Activity Feed -- real-time events from WebSocket, scrollable list, each entry shows event type icon + description + timestamp. Port the `ActivityFeed` component.
- Right (40%): Verification Gradient -- four horizontal bars (AUTO_APPROVED, FLAGGED, HELD, BLOCKED) with counts, percentages, and mini sparkline trend indicators

**Row 3 -- Quick Actions** (4 action cards):

1. Review Approvals (with pending count badge)
2. View Audit Trail
3. Cost Report
4. Agent Overview

**Data sources**: `verificationStats()`, `heldActions()`, `listTrustChains()`, `costReport({days: 1})`, WebSocket events

**Adaptive layout**:

- Phone: single column, stat cards 2x2
- Tablet: two columns, stat cards 2x2
- Desktop: full layout as described

**Pull-to-refresh**: RefreshIndicator wrapping the scrollable content. Refreshes all 4 API calls.

**Acceptance criteria**: All stat cards show real data. Activity feed updates in real-time. Tapping any card navigates to the correct screen.

---

#### C-03: Agents list + detail

**Effort**: Large (1.5 days)
**Dependencies**: F-03, F-07

**What to do**:

**List screen** (`/agents`):

- Load all teams via `listTeams()`, then agents per team via `listAgents(teamId)`
- Display as grouped list (group by team) or flat list with team filter dropdown
- Each agent row: name, role, posture badge, status dot
- Tapping navigates to agent detail
- Pull-to-refresh

**Detail screen** (`/agents/:id`):

- Load via `getAgentDetail(agentId)`
- Header: agent name, role, team, status dot
- Posture section: current posture badge, posture history timeline (chronological list of `PostureChange` entries)
- Capabilities section: chip list of capability strings
- Constraint envelope link: if `envelope_id` is set, link to `/envelopes/{envelope_id}`
- Actions section (buttons):
  - Change Posture: dialog with posture dropdown, reason field, confirmation
  - Suspend Agent: dialog with reason field, confirmation
  - Revoke Agent: dialog with reason field, confirmation (with "irreversible" warning)
- Timestamps: created_at, last_active_at (formatted relative)

**Data sources**: `listTeams()`, `listAgents()`, `getAgentDetail()`, `changePosture()`, `suspendAgent()`, `revokeAgent()`

**Acceptance criteria**: Agent list loads and groups by team. Detail screen shows all fields. Posture change, suspend, and revoke actions work and refresh the screen.

---

#### C-04: Approval queue + approve/reject flow

**Effort**: Large (1.5 days)
**Dependencies**: F-03, F-04, F-07

**What to do**:
Port `apps/web/app/approvals/page.tsx` and the `ApprovalCard` component.

**List view**:

- Load via `heldActions()`
- Sort by urgency (critical first), then submission time (oldest first)
- Summary bar: pending count, critical count, resolved-this-session count
- Each card shows: action description, agent ID, team ID, urgency badge, submission timestamp, reason
- Empty state: "All caught up" message with green check icon

**Approve/reject flow**:

- Each card has Approve (green) and Reject (red) buttons
- Tapping either opens a bottom sheet (phone) or dialog (tablet/desktop) with:
  - Optional reason/notes text field
  - Confirm button
  - Loading state during API call
- On success: card transitions to resolved state (muted, strikethrough, with "Approved" or "Rejected" badge)
- On error: shows inline error on the card

**Real-time updates**: When a `held_action` event arrives via WebSocket, add the new item to the list with a highlight animation.

**Data sources**: `heldActions()`, `approveAction()`, `rejectAction()`, WebSocket `held_action` events

**Acceptance criteria**: Approval queue displays all held actions sorted correctly. Approve and reject work. Resolved items are visually distinct. New items appear in real-time.

---

#### C-05: ShadowEnforcer dashboard

**Effort**: Large (1.5 days)
**Dependencies**: F-03, F-07

**What to do**:
Port `apps/web/app/shadow/page.tsx` and its child components.

**Agent selector**: Dropdown populated from teams/agents API (same multi-team loading pattern as web). Auto-selects first agent.

**Metrics cards** (6 cards):

- Total evaluations
- Auto-approved count
- Flagged count
- Held count
- Blocked count
- Previous pass rate

**Pass rate gauge**: Circular SVG/CustomPaint ring showing pass rate percentage. Center text shows the percentage. Below shows total evaluations and period days.

**Verification distribution**: Stacked horizontal bar showing the ratio of auto_approved : flagged : held : blocked using verification gradient colors.

**Dimension breakdown**: Horizontal bar chart showing trigger counts per constraint dimension (Financial, Operational, Temporal, Data Access, Communication). Each bar shows count and percentage of total.

**Upgrade eligibility card**:

- Green banner if `upgrade_eligible` is true
- Red/amber banner with blocker list if not eligible
- Recommendation text from the report

**Data sources**: `listTeams()`, `listAgents()`, `shadowMetrics()`, `shadowReport()`

**Acceptance criteria**: Agent selector works. All metrics display correctly. Gauge renders. Upgrade eligibility correctly shows eligible/blocked states.

---

#### C-06: DM team + task submission

**Effort**: Large (1.5 days)
**Dependencies**: F-03, F-07

**What to do**:
Port `apps/web/app/dm/page.tsx` and child components.

**Team summary** (stat cards):

- Active agents count
- Total actions today
- Overall approval rate (percentage)
- Pending task count

**Agent cards grid**: Each card shows agent name, role, posture badge, status dot, actions today, approval rate percentage.

**Task submission form**:

- Description text field (multiline)
- Target agent dropdown (optional -- "Auto-route" is default, then list of team agents)
- Submit button with loading state
- After submission: show task status card with task_id, status badge, polling for completion
- Status polling: call `getDmTaskStatus(taskId)` every 2 seconds until status is `complete` or `failed`
- Result display: show the task result when complete

**Fallback behavior** (matching web): If `/api/v1/dm/status` returns 404, fall back to loading agents from `/api/v1/teams/dm-team/agents` and construct a synthetic DmStatus.

**Data sources**: `getDmStatus()`, `listAgents('dm-team')` (fallback), `submitDmTask()`, `getDmTaskStatus()`

**Acceptance criteria**: DM status loads (either from dedicated endpoint or fallback). Task submission works. Polling shows live status updates.

---

#### C-07: Cost report

**Effort**: Medium (1 day)
**Dependencies**: F-03, F-07

**What to do**:
Port `apps/web/app/cost-report/page.tsx`.

**Summary section**:

- Total cost (large text)
- Period (days)
- Total API calls
- Alerts triggered

**By-agent breakdown**: Horizontal bar chart or list showing cost per agent.

**By-model breakdown**: Horizontal bar chart or list showing cost per model.

**Daily trend**: Line chart or bar chart showing cost per day (using `fl_chart`). The `by_day` field provides date-keyed cost data.

**Filters** (matching API params):

- Team filter dropdown
- Agent filter dropdown
- Days selector (7, 14, 30)

**Data sources**: `costReport({teamId, agentId, days})`

**Acceptance criteria**: Cost data displays. Charts render. Filters trigger API re-fetch with updated parameters.

---

### Milestone 3: Secondary Screens (Days 16--22)

Important but less frequently used screens. These complete feature parity with the web dashboard.

---

#### S-01: Trust chains

**Effort**: Medium (1 day)
**Dependencies**: F-03, F-07

**What to do**:
Port `apps/web/app/trust-chains/page.tsx`.

**List view**: Table/list of all trust chains from `listTrustChains()`. Columns: agent name, team, posture badge, status badge. Tapping navigates to trust chain detail.

**Detail view** (inline expansion or separate screen): Load `getTrustChainDetail(agentId)`. Show agent_id, name, role, team_id, posture, status, capabilities list.

**Data sources**: `listTrustChains()`, `getTrustChainDetail()`

---

#### S-02: Constraint envelopes

**Effort**: Medium (1 day)
**Dependencies**: F-03, F-07

**What to do**:
Port `apps/web/app/envelopes/page.tsx` and `apps/web/app/envelopes/[id]/page.tsx`.

**List view**: Load `listEnvelopes()`. Show envelope_id, description, agent_id, team_id. Tapping navigates to detail.

**Detail view**: Load `getEnvelope(envelopeId)`. Display all five CARE constraint dimensions in expandable sections:

1. **Financial**: max_spend_usd, api_cost_budget_usd, requires_approval_above_usd
2. **Operational**: allowed_actions (chip list), blocked_actions (chip list), max_actions_per_day
3. **Temporal**: active hours (formatted time range), timezone, blackout periods
4. **Data Access**: read_paths, write_paths, blocked_data_types
5. **Communication**: internal_only toggle, allowed_channels, external_requires_approval

**Data sources**: `listEnvelopes()`, `getEnvelope()`

---

#### S-03: Bridges list + detail + create

**Effort**: Large (1.5 days)
**Dependencies**: F-03, F-07

**What to do**:
Port `apps/web/app/bridges/page.tsx`, `apps/web/app/bridges/[id]/page.tsx`, `apps/web/app/bridges/create/page.tsx`.

**List view**: Load `listBridges()`. Columns: bridge_id, type badge, source team, target team, purpose (truncated), status badge, created_at. Filter by team. Link to create.

**Detail view**: Load `getBridge(bridgeId)`. Show all fields from BridgeDetail. Action buttons:

- Approve (if pending, show source/target side selector)
- Suspend (if active)
- Close (if active/suspended)
- Audit trail: load `bridgeAudit(bridgeId)` in a collapsible section

**Create screen**: Form with fields matching `CreateBridgeRequest`:

- Bridge type selector (Standing, Scoped, Ad-Hoc)
- Source team dropdown
- Target team dropdown
- Purpose text field
- Permissions (optional expandable section): read paths, write paths, message types
- Valid days (optional number input)
- Submit button

**Data sources**: `listBridges()`, `getBridge()`, `createBridge()`, `approveBridge()`, `suspendBridge()`, `closeBridge()`, `bridgeAudit()`

---

#### S-04: Workspaces

**Effort**: Small (0.5 day)
**Dependencies**: F-03, F-07

**What to do**:
Port `apps/web/app/workspaces/page.tsx`.

**List view**: Load `listWorkspaces()`. Each item shows: id, path, description, state badge (provisioning/active/archived/decommissioned), phase badge (analyze/plan/implement/validate/codify), team_id.

**Data sources**: `listWorkspaces()`

---

#### S-05: Audit trail

**Effort**: Medium (1 day)
**Dependencies**: F-03, F-07

**What to do**:
Port `apps/web/app/audit/page.tsx`.

**List view**: Load `listAuditAnchors()`. Each entry shows: anchor_id, agent_name, team_id, action, verification_level badge, timestamp, details (expandable).

**Filters**:

- Agent filter (text input or dropdown)
- Verification level filter (multi-select: AUTO_APPROVED, FLAGGED, HELD, BLOCKED)
- Date range picker (start_date, end_date)

**Team audit**: Ability to filter by team via `getTeamAudit(teamId)`.

**Data sources**: `listAuditAnchors()`, `getTeamAudit()`

---

#### S-06: Org structure

**Effort**: Medium (0.5 day)
**Dependencies**: F-03, F-07

**What to do**:
Port `apps/web/app/org/page.tsx`.

**Summary cards**: Teams count, total agents count, operational status.

**Team cards**: Each team shown as a card containing a grid of agent sub-cards. Each agent sub-card shows name, role, posture badge, status dot. Tapping an agent navigates to `/agents/{agent_id}`.

**Data sources**: `listTeams()`, `listAgents()` per team

---

#### S-07: Verification stats

**Effort**: Small (0.5 day)
**Dependencies**: F-03, F-07

**What to do**:
Port `apps/web/app/verification/page.tsx`.

Full-page view of verification gradient stats:

- Four large stat cards (one per level): AUTO_APPROVED, FLAGGED, HELD, BLOCKED with counts and percentages
- Horizontal stacked bar showing distribution
- Total verifications count

**Data sources**: `verificationStats()`

---

### Milestone 4: Platform Features (Days 23--27)

Cross-cutting features that make the app production-quality.

---

#### P-01: Dark mode

**Effort**: Small (0.5 day)
**Dependencies**: F-07

**What to do**:

- ThemeMode toggle in settings screen (Light / Dark / System)
- Store preference in SharedPreferences (not secure storage)
- All screens must already use theme tokens from F-07, so switching should "just work"
- Verify all custom colors (verification gradient, posture badges, urgency) have dark variants

**Acceptance criteria**: Toggle works. All screens render correctly in both modes. System default follows OS setting.

---

#### P-02: Responsive layouts (phone/tablet/desktop)

**Effort**: Large (2 days)
**Dependencies**: All screens

**What to do**:
This is a pass over all screens to verify and polish adaptive behavior:

**Breakpoints**:

- Compact (< 600dp): phone layout
- Medium (600--840dp): tablet layout
- Expanded (> 840dp): desktop layout

**Navigation adaptation** (from F-06):

- Phone: BottomNavigationBar (5 items: Overview, Agents, Approvals, DM, More)
- Tablet: NavigationRail (12 items, icon + label on hover)
- Desktop: Full sidebar (12 items, collapsible)

**Screen-specific adaptations**:
| Screen | Phone | Tablet | Desktop |
|---|---|---|---|
| Dashboard | 1-col, stat cards 2x2 | 2-col | 3-row layout |
| Agents list | Single column | 2-column grid | 3-column grid |
| Agent detail | Scrollable single column | Two-pane (list + detail) | Two-pane |
| Approvals | Card list | 2-column grid | 3-column grid |
| Shadow | Scrollable single column | Two-column charts | Full layout |
| Bridges list | Card list | Table | Table |
| Bridge detail | Scrollable | Two-pane | Two-pane |

**iPad multitasking**: Support split view and slide over on iPadOS.

**Acceptance criteria**: Every screen renders correctly at 360dp (small phone), 768dp (tablet), 1200dp (desktop). No overflow. No truncation of critical data.

---

#### P-03: Pull-to-refresh on all list screens

**Effort**: Small (0.5 day)
**Dependencies**: All list screens

**What to do**:
Wrap every scrollable list screen with `RefreshIndicator`. On refresh, re-fetch the relevant API data. Screens: Dashboard, Agents, Approvals, Trust Chains, Envelopes, Bridges, Workspaces, Audit, Org, Verification, Shadow, DM, Cost Report.

**Acceptance criteria**: Pull-to-refresh works on all list screens. Loading indicator shows. Data refreshes.

---

#### P-04: Connection status indicator

**Effort**: Small (0.5 day)
**Dependencies**: F-04

**What to do**:
Port the web `Header` connection status indicator. Show a colored dot + label:

- Green "Connected" when WebSocket is connected
- Yellow "Connecting..." when connecting/reconnecting
- Red "Disconnected" when disconnected

Display in the app bar (top right on tablet/desktop, in the app bar subtitle on phone).

**Acceptance criteria**: Status updates in real-time as WebSocket connects/disconnects.

---

#### P-05: Settings screen

**Effort**: Small (0.5 day)
**Dependencies**: F-05, P-01

**What to do**:

- Server URL configuration (for connecting to different PACT instances)
- Theme toggle (Light / Dark / System)
- Current user display (name, role)
- Logout button
- App version display
- "About" section: PACT v0.1.0, Terrene Foundation

**Acceptance criteria**: All settings work. Logout clears credentials and returns to login.

---

### Milestone 5: Testing (Days 28--32)

---

#### T-01: Widget tests for all screens

**Effort**: Large (2 days)
**Dependencies**: All screens complete

**What to do**:
Write widget tests for each screen using `mocktail` to mock the API client. At minimum, one test per screen covering:

1. **Loading state**: verify shimmer/skeleton appears
2. **Data state**: verify correct rendering with mock data
3. **Error state**: verify error alert appears with retry button
4. **Empty state**: verify empty state message (where applicable)
5. **User interaction**: verify navigation, button taps, form submission

**Screen test inventory** (18 screens):
| Screen | Key interactions to test |
|---|---|
| Login | Submit form, validation errors, loading state, redirect |
| Dashboard | Stat cards render, activity feed, quick actions navigate |
| Agents list | Group by team, tap navigates to detail |
| Agent detail | Posture history renders, actions work (change posture, suspend, revoke) |
| Approvals | Sort by urgency, approve/reject flow, empty state |
| Shadow | Agent selector, metrics cards, upgrade eligibility |
| DM Team | Team summary, agent cards, task submission + polling |
| Cost Report | Summary renders, filter changes trigger re-fetch |
| Trust Chains | List renders, detail expansion |
| Envelopes list | List renders, tap navigates |
| Envelope detail | Five dimensions render correctly |
| Bridges list | List renders, status badges |
| Bridge detail | Actions work (approve, suspend, close), audit trail |
| Bridge create | Form validation, submission |
| Workspaces | List renders with state/phase badges |
| Audit Trail | Filters work, entries render |
| Org Structure | Team cards, agent sub-cards |
| Verification | Gradient bars, totals |

**Acceptance criteria**: All widget tests pass. Coverage target: every screen has at least loading + data + error tests.

---

#### T-02: Integration tests for API client

**Effort**: Medium (1 day)
**Dependencies**: F-03

**What to do**:
Test every `CareApiClient` method against either a live backend or a mock HTTP server (using `dio_test` or `http_mock_adapter`).

**Test categories**:

1. **Successful responses**: Verify correct deserialization for every method
2. **Error responses**: Verify 401 maps to ApiError, 404 maps correctly, 500 maps correctly
3. **Network errors**: Verify timeout maps to NetworkError
4. **Auth interceptor**: Verify token is injected, verify unauthenticated requests are rejected
5. **Query parameter encoding**: Verify filters (costReport, listAuditAnchors, bridgeAudit) encode correctly

**Acceptance criteria**: All 35 methods have at least one success and one error test case.

---

#### T-03: Golden tests for design system

**Effort**: Medium (1 day)
**Dependencies**: F-07

**What to do**:
Golden (snapshot) tests for shared widgets to catch visual regressions:

**Widgets to snapshot** (both light and dark mode):

- PostureBadge (all 5 postures)
- VerificationBadge (all 4 levels)
- UrgencyBadge (all 4 levels)
- StatusDot (all 4 statuses)
- BridgeStatusBadge (all 7 statuses)
- StatCard (with and without sub-content)
- CareCard
- GaugeBar (0%, 50%, 100%)
- ErrorAlert
- EmptyState

**Acceptance criteria**: Golden files generated. CI compares against golden files on PR.

---

## Dependency Graph

```
F-01 (Project setup)
  |
  +-- F-02 (Data models) --------+-- F-03 (API client) ----+-- F-05 (Auth) ---- F-06 (Router)
  |                              |                         |
  +-- F-07 (Design system)       +-- F-04 (WebSocket)      +-- T-02 (API tests)
  |                              |
  |                              +-- C-02 (Dashboard)
  |                              +-- C-03 (Agents)
  |                              +-- C-04 (Approvals)
  |                              +-- C-05 (Shadow)
  |                              +-- C-06 (DM Team)
  |                              +-- C-07 (Cost)
  |                              +-- S-01..S-07 (Secondary screens)
  |
  +-- T-03 (Golden tests)

C-01 (Login) depends on F-05 + F-07
P-01 (Dark mode) depends on F-07
P-02 (Responsive) depends on all screens
P-03 (Pull-to-refresh) depends on all list screens
P-04 (Connection status) depends on F-04
P-05 (Settings) depends on F-05 + P-01
T-01 (Widget tests) depends on all screens
```

---

## Full Task Summary Table

| ID                       | Task                              | Effort | Days     | Dependencies     | Milestone     |
| ------------------------ | --------------------------------- | ------ | -------- | ---------------- | ------------- |
| F-01                     | Flutter project setup (6 targets) | M      | 1.5      | --               | 1: Foundation |
| F-02                     | Dart data models (28 types)       | M      | 1.0      | F-01             | 1: Foundation |
| F-03                     | Dart API client (35 methods)      | L      | 1.5      | F-02             | 1: Foundation |
| F-04                     | WebSocket client                  | M      | 0.5      | F-02             | 1: Foundation |
| F-05                     | Auth system                       | M      | 1.0      | F-03             | 1: Foundation |
| F-06                     | Navigation and routing            | M      | 0.5      | F-05             | 1: Foundation |
| F-07                     | Design system                     | M      | 1.0      | F-01             | 1: Foundation |
| **Milestone 1 subtotal** |                                   |        | **7.0**  |                  |               |
| C-01                     | Login screen                      | S      | 0.5      | F-05, F-07       | 2: Core       |
| C-02                     | Dashboard overview                | L      | 1.5      | F-03, F-04, F-07 | 2: Core       |
| C-03                     | Agents list + detail              | L      | 1.5      | F-03, F-07       | 2: Core       |
| C-04                     | Approval queue + flow             | L      | 1.5      | F-03, F-04, F-07 | 2: Core       |
| C-05                     | ShadowEnforcer dashboard          | L      | 1.5      | F-03, F-07       | 2: Core       |
| C-06                     | DM team + task submission         | L      | 1.5      | F-03, F-07       | 2: Core       |
| C-07                     | Cost report                       | M      | 1.0      | F-03, F-07       | 2: Core       |
| **Milestone 2 subtotal** |                                   |        | **9.0**  |                  |               |
| S-01                     | Trust chains                      | M      | 1.0      | F-03, F-07       | 3: Secondary  |
| S-02                     | Constraint envelopes              | M      | 1.0      | F-03, F-07       | 3: Secondary  |
| S-03                     | Bridges list + detail + create    | L      | 1.5      | F-03, F-07       | 3: Secondary  |
| S-04                     | Workspaces                        | S      | 0.5      | F-03, F-07       | 3: Secondary  |
| S-05                     | Audit trail                       | M      | 1.0      | F-03, F-07       | 3: Secondary  |
| S-06                     | Org structure                     | M      | 0.5      | F-03, F-07       | 3: Secondary  |
| S-07                     | Verification stats                | S      | 0.5      | F-03, F-07       | 3: Secondary  |
| **Milestone 3 subtotal** |                                   |        | **6.0**  |                  |               |
| P-01                     | Dark mode                         | S      | 0.5      | F-07             | 4: Platform   |
| P-02                     | Responsive layouts                | L      | 2.0      | All screens      | 4: Platform   |
| P-03                     | Pull-to-refresh                   | S      | 0.5      | All list screens | 4: Platform   |
| P-04                     | Connection status indicator       | S      | 0.5      | F-04             | 4: Platform   |
| P-05                     | Settings screen                   | S      | 0.5      | F-05, P-01       | 4: Platform   |
| **Milestone 4 subtotal** |                                   |        | **4.0**  |                  |               |
| T-01                     | Widget tests (18 screens)         | L      | 2.0      | All screens      | 5: Testing    |
| T-02                     | Integration tests (API client)    | M      | 1.0      | F-03             | 5: Testing    |
| T-03                     | Golden tests (design system)      | M      | 1.0      | F-07             | 5: Testing    |
| **Milestone 5 subtotal** |                                   |        | **4.0**  |                  |               |
| **TOTAL**                |                                   |        | **30.0** |                  |               |

---

## Risk Assessment

### High Probability, High Impact (Critical)

1. **Platform-specific storage failures**
   - Risk: `flutter_secure_storage` behaves differently on each platform (Keychain vs EncryptedSharedPreferences vs Credential Locker)
   - Mitigation: Test login/logout/persistence on all 6 targets during F-05
   - Prevention: Wrap storage in an abstraction with platform-specific fallbacks

2. **WebSocket reconnection on mobile**
   - Risk: iOS background app suspension kills WebSocket. Android Doze mode limits network access
   - Mitigation: Reconnect on app resume (WidgetsBindingObserver.didChangeAppLifecycleState)
   - Prevention: Do not rely on WebSocket for critical state -- always have pull-to-refresh as fallback

### Medium Probability, Medium Impact (Monitor)

3. **Responsive layout edge cases**
   - Risk: Specific screen sizes (especially iPad split-view at 1/3 width) may cause overflow
   - Mitigation: Test at all critical breakpoints (320, 375, 414, 768, 1024, 1366, 1440)
   - Prevention: Use LayoutBuilder consistently, never hardcode widths

4. **Desktop-specific issues (macOS/Windows)**
   - Risk: Scrollbar behavior, window resizing, keyboard shortcuts differ from mobile
   - Mitigation: Test on actual macOS and Windows machines
   - Prevention: Use platform-adaptive widgets from Material 3

5. **API rate limiting on mobile**
   - Risk: Dashboard overview makes 4 concurrent API calls. Quick navigation could trigger rate limits
   - Mitigation: Implement request coalescing -- if a request is in-flight, return the pending future
   - Prevention: Cache responses in Riverpod providers with TTL

### Low Probability, High Impact (Accept)

6. **Flutter SDK version compatibility**
   - Risk: Dart 3.x / Flutter 3.x breaking changes
   - Mitigation: Pin SDK version in pubspec.yaml with upper bound
   - Prevention: Stay on stable channel, update deliberately

---

## Notes on Feature Parity

The following web dashboard pages map 1:1 to Flutter screens:

| Web page          | Flutter screen          | Notes                              |
| ----------------- | ----------------------- | ---------------------------------- |
| `/login`          | LoginScreen             | Identical flow                     |
| `/`               | DashboardOverviewScreen | Identical layout (adapted)         |
| `/trust-chains`   | TrustChainsScreen       | Identical                          |
| `/envelopes`      | EnvelopesListScreen     | Identical                          |
| `/envelopes/[id]` | EnvelopeDetailScreen    | Identical                          |
| `/workspaces`     | WorkspacesScreen        | Identical                          |
| `/agents`         | AgentsListScreen        | Identical                          |
| `/agents/[id]`    | AgentDetailScreen       | Identical                          |
| `/dm`             | DmTeamScreen            | Identical (including 404 fallback) |
| `/bridges`        | BridgesListScreen       | Identical                          |
| `/bridges/create` | BridgeCreateScreen      | Identical                          |
| `/bridges/[id]`   | BridgeDetailScreen      | Identical                          |
| `/verification`   | VerificationScreen      | Identical                          |
| `/shadow`         | ShadowScreen            | Identical                          |
| `/audit`          | AuditTrailScreen        | Identical                          |
| `/approvals`      | ApprovalsScreen         | Identical                          |
| `/cost-report`    | CostReportScreen        | Identical                          |
| `/org`            | OrgStructureScreen      | Identical                          |

**Added in Flutter (not in web)**:

- Settings screen (server URL, theme toggle, logout) -- needed because mobile apps need explicit settings management
- Adaptive navigation (BottomNav on phone, Rail on tablet, Sidebar on desktop) -- the web uses a single responsive sidebar

**Not ported from web (not needed in Flutter)**:

- `DashboardShell` component -- replaced by Flutter's adaptive scaffold
- CSS design tokens -- replaced by Material 3 theme
- Next.js routing -- replaced by GoRouter
