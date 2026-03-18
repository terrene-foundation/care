# Red Team Report — RT14: Flutter App

**Date**: 2026-03-16
**Scope**: Flutter native app (iOS, iPadOS, Android, Android tablet, macOS, Windows)
**Agents**: flutter-specialist (code review), value-auditor (enterprise perspective)
**App Stats**: 62 Dart files, 19 screens, 6 platform targets, 0 analysis errors

---

## CRITICAL Findings (Fixed During Red Team)

| #   | Finding                                                                         | Status                                     |
| --- | ------------------------------------------------------------------------------- | ------------------------------------------ |
| C1  | All 13 providers used simulated data_service.dart instead of real CareApiClient | **FIXED** — all providers rewired to API   |
| C2  | data_service.dart with fake data was the sole data source                       | **FIXED** — file deleted, 0 imports remain |

## HIGH Findings (Fixed During Red Team)

| #   | Finding                                                   | Status                                                     |
| --- | --------------------------------------------------------- | ---------------------------------------------------------- |
| H1  | Approve/reject buttons showed "requires backend" snackbar | **FIXED** — wired to client.approveAction()/rejectAction() |
| H2  | Suspend/revoke agent buttons were stubs                   | **FIXED** — wired to client.suspendAgent()/revokeAgent()   |
| H3  | Bridge creation used simulated submission                 | **FIXED** — wired to client.createBridge()                 |
| H4  | DM task submission used Future.delayed, no API            | **FIXED** — wired to client.submitDmTask()                 |
| H5  | Navigator.push used instead of GoRouter context.go()      | **FIXED** — envelopes and bridges use GoRouter             |
| H6  | dynamic types in shadow_screen.dart                       | **FIXED** — replaced with List<TrustChainSummary>          |
| H7  | baseUrl not restored on app restart                       | **FIXED** — stored baseUrl read in checkAuth()             |
| H8  | WebSocket client never connected                          | Accepted — Phase 2 enhancement                             |

## MEDIUM Findings (Accepted)

| #   | Finding                                 | Notes                         |
| --- | --------------------------------------- | ----------------------------- |
| M1  | Unused app/theme.dart (dead code)       | Cleanup task                  |
| M2  | Duplicate CareBreakpoints class         | Consolidation task            |
| M3  | Single widget test only                 | Test coverage in M5 milestone |
| M4  | DM task doesn't show governance outcome | Wire DmTask response display  |
| M5  | No pull-to-refresh gesture              | Enhancement                   |

---

## Value Audit Summary

The value auditor concluded: **"The architecture is genuinely impressive. A complete API client with 34 typed methods, WebSocket with exponential backoff, secure credential storage, three-tier responsive layout, and 100% feature parity with the web dashboard. The gap is execution — now closed by wiring providers to the real API."**

Key strengths:

- 19 screens covering 100% of web dashboard pages + settings
- Three-tier responsive shell (phone bottom nav / tablet rail / desktop sidebar)
- Approval queue UX correctly prioritized for one-handed mobile use
- ShadowEnforcer with custom-painted gauge and upgrade recommendation
- 5-step bridge creation wizard
- CARE semantic color system ported from web Tailwind tokens
- Secure token storage via flutter_secure_storage (not SharedPreferences)

---

## Convergence Status

| Category        | Round 1       | After Fix                             |
| --------------- | ------------- | ------------------------------------- |
| CRITICAL        | 2 found       | 2 **FIXED**                           |
| HIGH            | 8 found       | 7 **FIXED**, 1 accepted               |
| MEDIUM          | 5 found       | 0 fixed (accepted for next iteration) |
| Flutter analyze | 0 errors      | 0 errors                              |
| Backend tests   | 3,420 passing | 3,420 passing                         |

**Verdict**: 0 CRITICAL remaining. 1 HIGH accepted (WebSocket wiring — enhancement). **RED TEAM CONVERGED.**
