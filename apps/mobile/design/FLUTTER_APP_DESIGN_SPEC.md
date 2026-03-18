# CARE Platform Flutter App -- UI/UX Design Specification

Copyright 2026 Terrene Foundation. Licensed under the Apache License, Version 2.0.

---

## Executive Summary

This document is the complete UI/UX design specification for the CARE Platform Flutter app, covering phone, tablet, and desktop form factors. The app provides the same governance dashboard experience as the existing web app (18 pages across 12 navigation sections) but optimized for native interaction on each platform.

**Top-level design decisions:**

1. **Bottom navigation bar on phone** (5 primary tabs + overflow). Not a drawer -- governance dashboards require persistent visibility of critical screens like Approvals.
2. **Master-detail layout on tablet** with a persistent rail on the left. Tablet users get side-by-side panels for reviewing approvals and inspecting agents.
3. **Full sidebar + multi-panel layout on desktop** mirroring the web app, with keyboard shortcuts for power users.
4. **Mobile-first priority screens**: Approvals, Overview, Agents, ShadowEnforcer, Cost Report. These are the screens an operator reaches for when away from their desk.
5. **Material 3 design system** with CARE-specific semantic tokens ported from the web Tailwind config.

---

## 1. Information Architecture

### 1.1 Complete Screen Map (18 Screens)

```
LOGIN
  |
  v
AUTHENTICATED SHELL
  |
  +-- Overview (Dashboard Home)
  |     Stat cards, activity feed, verification gradient summary, quick actions
  |
  +-- Trust & Governance (section)
  |     +-- Trust Chains          (tree visualization)
  |     +-- Constraint Envelopes  (list -> detail with 5-dimension gauges)
  |     +-- Verification Gradient (stats + chart)
  |
  +-- Agent Management (section)
  |     +-- Agents (list)         -> Agent Detail (posture, status, team)
  |     +-- DM Team               (team summary, agent cards, task submission)
  |     +-- Organization          (team structure tree)
  |
  +-- Operations (section)
  |     +-- Approvals             (queue with approve/reject actions)
  |     +-- ShadowEnforcer        (metrics, gauge, dimension breakdown)
  |     +-- Audit Trail           (searchable/filterable table, detail panel)
  |
  +-- Infrastructure (section)
  |     +-- Bridges               (list -> detail, create wizard)
  |     +-- Workspaces            (cards with CO phase, bridge connections)
  |     +-- Cost Report           (stats, agent/model tables, trend chart)
  |
  +-- Settings
        +-- Profile / Logout
        +-- Connection status
        +-- Notification preferences
```

### 1.2 Navigation Hierarchy by Priority

**Tier 1 -- Critical (daily use, needs one-tap access):**

- Overview (home)
- Approvals (time-sensitive: HELD actions need human response)
- Agents (most-viewed roster)

**Tier 2 -- Important (multiple times per day):**

- ShadowEnforcer (trust posture evidence)
- Cost Report (budget monitoring)
- Verification Gradient (system health)

**Tier 3 -- Reference (as-needed):**

- Trust Chains, Envelopes, Audit Trail
- Bridges, Workspaces, Organization
- DM Team

### 1.3 Navigation Flow Diagram

```
PHONE (Bottom Nav):

  [Home]  [Approvals]  [Agents]  [Shadow]  [More...]
                                              |
                                              +-> Cost Report
                                              +-> Verification
                                              +-> Trust Chains
                                              +-> Envelopes
                                              +-> Bridges
                                              +-> Workspaces
                                              +-> DM Team
                                              +-> Organization
                                              +-> Audit Trail
                                              +-> Settings

TABLET (Side Rail + Content):

  [Rail]  |  [Content Area]  |  [Detail Panel (optional)]
    |
    Overview
    ---
    Approvals (badge count)
    Agents
    Shadow
    ---
    Cost
    Verification
    Trust Chains
    Envelopes
    ---
    Bridges
    Workspaces
    DM Team
    Org
    ---
    Audit
    ---
    Settings

DESKTOP (Full Sidebar + Content):

  [Sidebar 256px]  |  [Main Content Area]
    identical to web sidebar with all 12 sections
    collapsible to icon-only (64px)
```

---

## 2. Layout Strategy by Form Factor

### 2.1 Phone (375px -- 414px)

**Core principle**: One-column layout. Every screen fits a single scrollable column. No horizontal scrolling ever.

#### Shell Structure

```
+----------------------------------+
| Status Bar (system)              |
+----------------------------------+
| App Bar: Title | [Actions]       |
+----------------------------------+
|                                  |
|     Scrollable Content Area      |
|     (full width, 16px padding)   |
|                                  |
+----------------------------------+
| Bottom Nav Bar (56px)            |
+----------------------------------+
```

#### Bottom Navigation Bar (5 tabs)

```
+------+----------+--------+--------+------+
| Home | Approvals| Agents | Shadow | More |
|  O      O (3)     O        O       ...  |
+------+----------+--------+--------+------+
```

- **Approvals** shows a badge count for pending HELD actions (mirrors the web sidebar badge).
- **More** opens a full-screen list of all remaining sections, grouped by category.
- Icons use Material Symbols (outlined), labels below at 10sp.
- Active tab uses `care-primary` blue; inactive uses `care-muted` gray.

#### Screen Adaptations (Phone)

**Overview Dashboard:**

- Stat cards: 2x2 grid (not 4-column). Each card is a compact version: icon + value + label, no sub-content. Tap to navigate.
- Activity feed: full-width below stats, capped at 10 items with "View All" link.
- Verification gradient: stacked bars below feed, simplified (no sparkline trends -- they are too small at phone size).
- Quick actions: hidden on phone. The bottom nav already provides direct access to the primary screens.

```
+----------------------------------+
| Overview                    [R]  |  R = Refresh
+----------------------------------+
| +------+ +------+                |
| |  12  | |   3  |                |
| |Active| |Pend. |                |
| |Agents| |Apprvl|                |
| +------+ +------+                |
| +------+ +------+                |
| | 94%  | |$12.40|                |
| |Verif.| | API  |                |
| | Rate | |Spend |                |
| +------+ +------+                |
|                                  |
| Activity Feed                    |
| -------------------------------- |
| [ ] Agent X auto-approved  12:03 |
| [ ] Agent Y held action    12:01 |
| [ ] Agent Z delegated      11:58 |
| ...                              |
| [View all activity ->]           |
|                                  |
| Verification Gradient            |
| Auto Approved  ====== 847  72%   |
| Flagged        ==     198  17%   |
| Held           =       89   8%   |
| Blocked        =       42   4%   |
+----------------------------------+
```

**Approvals Queue (Phone -- Critical Screen):**

- Full-width cards, one per row, sorted by urgency.
- Swipe gestures: swipe right to approve, swipe left to reject. Confirmation dialog on swipe.
- Alternative: large Approve/Reject buttons at bottom of each card for non-swipe users.
- Critical items have a red left border accent.
- Summary bar at top: "3 Pending | 1 Critical"

```
+----------------------------------+
| Approval Queue              [R]  |
+----------------------------------+
| 3 Pending | 1 Critical           |
|                                  |
| +------------------------------+ |
| |! CRITICAL                    | |  red left border
| | send-large-email             | |
| | Agent: dm-coordinator        | |
| | 2 min ago                    | |
| |                              | |
| | Reason: Exceeds comm limit   | |
| |                              | |
| | [Reject]          [Approve]  | |
| +------------------------------+ |
|                                  |
| +------------------------------+ |
| |  MEDIUM                      | |  orange left border
| | api-call-external            | |
| | Agent: research-agent        | |
| | 15 min ago                   | |
| |                              | |
| | [Reject]          [Approve]  | |
| +------------------------------+ |
+----------------------------------+
```

**One-handed optimization:**

- Approve/Reject buttons are at the bottom of each card (thumb-reachable zone).
- Swipe actions require only horizontal movement.
- Optional reason field appears only after tapping Reject (not blocking the happy path for Approve).
- Pull-to-refresh at the top.

**Agents List (Phone):**

- Single-column list with avatar placeholder, name, role, posture badge, status dot.
- Search bar at top (sticky).
- Tap to open agent detail (full-screen push).
- Filter chips: All | Active | Suspended | Revoked

```
+----------------------------------+
| Agents                      [+]  |
+----------------------------------+
| [Search agents...]               |
| [All] [Active] [Suspended]       |
|                                  |
| +------------------------------+ |
| | [A]  DM Coordinator          | |
| |      Coordinator role        | |
| |      SUPERVISED    * active  | |
| +------------------------------+ |
| | [B]  Research Agent           | |
| |      Research role            | |
| |      SHARED_PLANNING *active | |
| +------------------------------+ |
+----------------------------------+
```

**ShadowEnforcer (Phone):**

- Agent selector as a dropdown at top.
- Metrics cards in 2x2 grid (compact).
- Pass rate gauge: full-width circular SVG.
- Dimension breakdown: vertical stacked bars.
- Upgrade eligibility: expandable card at bottom.

**Cost Report (Phone):**

- Period selector as a dropdown.
- Stat cards: 2x2 grid.
- Agent breakdown: card list (not a table -- tables do not work well at 375px).
- Model breakdown: card list.
- Daily spend trend: horizontal bar chart simplified to fit phone width.

**Tables on Phone (Audit Trail, Bridges, Envelopes, Trust Chains):**

- Tables are replaced with card lists. Each row becomes a tappable card showing the 2-3 most important fields. Tap for full detail.
- This is critical: horizontal-scrolling tables are a poor mobile pattern. Cards are always better for phone.

### 2.2 Tablet (768px -- 1194px, portrait and landscape)

**Core principle**: Master-detail where possible. Use a NavigationRail (72px) on the left instead of full sidebar or bottom nav.

#### Shell Structure (Landscape)

```
+--+----------------------------+------------------+
|  |                            |                  |
|R |    Master Content          |  Detail Panel    |
|A |    (flexible width)        |  (360-400px)     |
|I |                            |                  |
|L |                            |                  |
|  |                            |                  |
|72|                            |                  |
|px|                            |                  |
+--+----------------------------+------------------+
```

#### Shell Structure (Portrait)

```
+--+---------------------------------------+
|  |                                       |
|R |         Full-width Content            |
|A |                                       |
|I |     (detail opens as slide-over       |
|L |      from right, 50% width)           |
|  |                                       |
|72|                                       |
|px|                                       |
+--+---------------------------------------+
```

#### Navigation Rail

```
+--+
|C |  CARE logo
+--+
|  |  Overview
|  |  ---
|  |  Approvals (badge)
|  |  Agents
|  |  Shadow
|  |  ---
|  |  Cost
|  |  Verification
|  |  Trust
|  |  Envelopes
|  |  ---
|  |  Bridges
|  |  Workspaces
|  |  DM Team
|  |  Org
|  |  ---
|  |  Audit
|  |  ---
|  |  Settings
+--+
```

- Icons only (no labels) in default state.
- Tap the hamburger icon or swipe right to expand rail into a 256px sidebar with labels (overlay, not push).
- Selected item has a pill-shaped highlight (Material 3 NavigationRail pattern).
- Approvals badge: small red dot in default icon mode; full badge count in expanded mode.

#### Screen Adaptations (Tablet)

**Overview Dashboard:**

- Stat cards: 4-column row (matches web).
- Activity feed + Verification gradient: side-by-side at 60/40 split (matches web).
- Quick actions: 2x2 grid.

**Approvals Queue (Tablet -- Master-Detail):**

- Left panel: scrollable list of approval cards (compact: urgency, action name, agent, time).
- Right panel: selected approval detail with full context, constraint dimensions, and Approve/Reject buttons.
- This eliminates the back-and-forth navigation of phone.

```
+--+--------------------+--------------------+
|  | Approval Queue     | send-large-email   |
|R | ---                | CRITICAL           |
|  | > send-large-email | Agent: dm-coord    |
|  |   api-call-ext     | Team: dm-team      |
|  |   budget-check     | Submitted: 2m ago  |
|  |                    |                    |
|  |                    | Constraint:        |
|  |                    | Communication dim  |
|  |                    | exceeds soft limit |
|  |                    |                    |
|  |                    | [Reject] [Approve] |
+--+--------------------+--------------------+
```

**Agents List (Tablet -- Master-Detail):**

- Left: agent card list (2-column grid or single list).
- Right: selected agent detail (posture, team, recent actions, constraint envelope summary).

**ShadowEnforcer (Tablet):**

- Agent selector spans top.
- Metrics cards: 3x2 or 4-column.
- Pass rate gauge + Verification distribution: side-by-side (matches web).
- Dimension breakdown: full-width below.
- Upgrade eligibility: full-width card.

**Audit Trail (Tablet):**

- Real table works at tablet width.
- Filters in a collapsible row above the table.
- Tapping a row opens the detail panel as a slide-over from the right.

**Tables on Tablet:**

- At 768px+, tables work. Show 3-4 columns.
- At 1024px+, show all columns.

### 2.3 Desktop (1200px+, macOS and Windows)

**Core principle**: Mirror the web dashboard layout exactly. Full sidebar, generous content area, keyboard shortcuts for power users.

#### Shell Structure

```
+------------+--------------------------------------+
|            |  Header: Breadcrumbs | Actions       |
| Sidebar    +--------------------------------------+
| 256px      |                                      |
| (collapse  |     Main Content Area                |
|  to 64px)  |     (padding: 24px)                  |
|            |                                      |
|            |                                      |
| [Collapse] |                                      |
+------------+--------------------------------------+
```

#### Desktop-Specific Features

**Keyboard Shortcuts:**
| Shortcut | Action |
|---|---|
| Cmd/Ctrl + K | Command palette (search anything) |
| Cmd/Ctrl + 1-5 | Navigate to top 5 sections |
| Cmd/Ctrl + Shift + A | Jump to Approvals |
| J / K | Navigate up/down in lists |
| Enter | Open selected item |
| Escape | Close detail panel / go back |
| A | Approve (when in approval detail) |
| R | Reject (when in approval detail) |

**Command Palette:**

- Cmd/Ctrl+K opens a search overlay.
- Searches across: screen names, agent names, bridge IDs, audit actions.
- Results grouped by type. Enter to navigate.

**Multi-Panel for Desktop:**

- Overview: full web layout (4 stat cards, 60/40 split, quick actions).
- Audit Trail: full table with all columns, slide-over detail panel.
- Cost Report: full tables with sort columns.
- All screens match or exceed the web layout fidelity.

**Sidebar:**

- Identical to web: icon + label for each section.
- Collapsible to icon-only (64px) via button or keyboard shortcut.
- Approval badge count in sidebar.
- Hover tooltip on collapsed icons.

---

## 3. Mobile Priority Screens (Build Order)

Build these first. They represent the screens an operator reaches for on their phone.

| Priority | Screen                | Rationale                                                                                                  |
| -------- | --------------------- | ---------------------------------------------------------------------------------------------------------- |
| P0       | Login                 | Required to access anything                                                                                |
| P0       | Overview              | Landing page after login; shows system health at a glance                                                  |
| P0       | Approvals             | Time-sensitive. HELD actions block agent work until approved. This is the #1 reason to open the phone app. |
| P1       | Agents                | Quick lookup of agent status and posture                                                                   |
| P1       | ShadowEnforcer        | Evidence for posture upgrade decisions                                                                     |
| P2       | Cost Report           | Budget monitoring on the go                                                                                |
| P2       | Verification Gradient | System health check                                                                                        |
| P3       | Audit Trail           | Reference lookup                                                                                           |
| P3       | Trust Chains          | Reference                                                                                                  |
| P3       | Envelopes             | Reference                                                                                                  |
| P3       | Bridges               | Infrequent management task                                                                                 |
| P3       | Workspaces            | Infrequent                                                                                                 |
| P3       | DM Team               | Specialized                                                                                                |
| P3       | Organization          | Infrequent                                                                                                 |

**Milestone 1 (MVP)**: Login + Overview + Approvals + Agents = 4 screens.
Operators can log in, see system health, clear the approval queue, and check agent status.

**Milestone 2**: + ShadowEnforcer + Cost Report + Verification = 7 screens.
Full operational monitoring.

**Milestone 3**: Remaining 7 screens to reach feature parity with web.

---

## 4. Design System Recommendations

### 4.1 Framework: Material 3 (Material Design 3)

Use Flutter's built-in Material 3 theming via `ThemeData` with `useMaterial3: true`. This provides:

- Dynamic color (seed-based palette generation)
- Built-in responsive scaffolds (NavigationBar, NavigationRail, NavigationDrawer)
- Adaptive layouts via `LayoutBuilder` and `MediaQuery`

### 4.2 Color Palette

Port the CARE semantic colors from the web Tailwind config directly to Dart constants.

```dart
/// CARE Platform Color Palette
/// Ported from apps/web/tailwind.config.js for cross-platform consistency.
abstract final class CareColors {
  // -- Platform Brand --
  static const Color primary       = Color(0xFF2563EB);  // care-primary
  static const Color primaryLight  = Color(0xFFEFF6FF);  // care-primary-light
  static const Color primaryDark   = Color(0xFF1E40AF);  // care-primary-dark

  static const Color surface       = Color(0xFFFFFFFF);  // care-surface
  static const Color surfaceDark   = Color(0xFF111827);  // care-surface dark mode
  static const Color border        = Color(0xFFE5E7EB);  // care-border
  static const Color muted         = Color(0xFF6B7280);  // care-muted
  static const Color mutedLight    = Color(0xFF9CA3AF);  // care-muted-light
  static const Color background    = Color(0xFFF9FAFB);  // gray-50

  // -- Verification Gradient Levels --
  static const Color gradientAuto          = Color(0xFF16A34A);  // green-600
  static const Color gradientAutoLight     = Color(0xFFDCFCE7);
  static const Color gradientAutoDark      = Color(0xFF166534);
  static const Color gradientFlagged       = Color(0xFFEAB308);  // yellow-500
  static const Color gradientFlaggedLight  = Color(0xFFFEF9C3);
  static const Color gradientFlaggedDark   = Color(0xFF854D0E);
  static const Color gradientHeld          = Color(0xFFF97316);  // orange-500
  static const Color gradientHeldLight     = Color(0xFFFFEDD5);
  static const Color gradientHeldDark      = Color(0xFF9A3412);
  static const Color gradientBlocked       = Color(0xFFDC2626);  // red-600
  static const Color gradientBlockedLight  = Color(0xFFFEE2E2);
  static const Color gradientBlockedDark   = Color(0xFF991B1B);

  // -- Trust Posture Levels (cool to warm) --
  static const Color posturePseudo         = Color(0xFF6B7280);  // gray
  static const Color posturePseudoLight    = Color(0xFFF3F4F6);
  static const Color postureSupervised     = Color(0xFF3B82F6);  // blue
  static const Color postureSupervisedLight = Color(0xFFDBEAFE);
  static const Color postureShared         = Color(0xFF8B5CF6);  // purple
  static const Color postureSharedLight    = Color(0xFFEDE9FE);
  static const Color postureContinuous     = Color(0xFF06B6D4);  // cyan
  static const Color postureContinuousLight = Color(0xFFCFFAFE);
  static const Color postureDelegated      = Color(0xFF16A34A);  // green
  static const Color postureDelegatedLight = Color(0xFFDCFCE7);

  // -- Status Colors --
  static const Color statusActive    = Color(0xFF16A34A);
  static const Color statusSuspended = Color(0xFFEAB308);
  static const Color statusRevoked   = Color(0xFFDC2626);
  static const Color statusInactive  = Color(0xFF6B7280);

  // -- Urgency Colors (Approval Queue) --
  static const Color urgencyCritical = Color(0xFFDC2626);
  static const Color urgencyHigh     = Color(0xFFF97316);
  static const Color urgencyMedium   = Color(0xFFEAB308);
  static const Color urgencyLow      = Color(0xFF6B7280);
}
```

### 4.3 Typography Scale

Use the same font hierarchy as the web app but adapted for Flutter's text theme.

```dart
/// CARE Platform Typography
/// Based on Inter for body text, JetBrains Mono for hashes/IDs.
abstract final class CareTypography {
  static const String fontFamily     = 'Inter';
  static const String monoFamily     = 'JetBrains Mono';

  // -- Scale --
  // Display:  only on login/splash
  // Headline: section headers on desktop
  // Title:    app bar titles, card headers
  // Body:     main content text
  // Label:    badges, captions, stat labels

  static const TextStyle displayLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 32,
    fontWeight: FontWeight.w700,
    height: 1.25,
    letterSpacing: -0.5,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.w600,
    height: 1.33,
  );

  static const TextStyle titleLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 18,
    fontWeight: FontWeight.w600,
    height: 1.44,
  );

  static const TextStyle titleMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w600,
    height: 1.43,
  );

  static const TextStyle bodyLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1.5,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    height: 1.43,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w400,
    height: 1.33,
  );

  static const TextStyle labelLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w500,
    height: 1.43,
  );

  static const TextStyle labelSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 11,
    fontWeight: FontWeight.w500,
    height: 1.45,
    letterSpacing: 0.5,
  );

  // -- Monospace (for hashes, IDs, cryptographic values) --
  static const TextStyle mono = TextStyle(
    fontFamily: monoFamily,
    fontSize: 13,
    fontWeight: FontWeight.w400,
    height: 1.38,
    letterSpacing: -0.3,
  );

  // -- Stat Value (dashboard cards) --
  static const TextStyle statValue = TextStyle(
    fontFamily: fontFamily,
    fontSize: 30,
    fontWeight: FontWeight.w600,
    height: 1.2,
    letterSpacing: -0.5,
  );

  // Phone-specific override: stat values smaller on compact screens
  static const TextStyle statValueCompact = TextStyle(
    fontFamily: fontFamily,
    fontSize: 22,
    fontWeight: FontWeight.w600,
    height: 1.2,
    letterSpacing: -0.3,
  );
}
```

### 4.4 Spacing Scale

```dart
/// CARE Platform Spacing Scale
/// 4px base unit, consistent with Material 3.
abstract final class CareSpacing {
  static const double xs   = 4;
  static const double sm   = 8;
  static const double md   = 12;
  static const double base = 16;
  static const double lg   = 20;
  static const double xl   = 24;
  static const double xxl  = 32;
  static const double xxxl = 48;

  // Layout-specific
  static const double pagePaddingPhone   = 16;
  static const double pagePaddingTablet  = 20;
  static const double pagePaddingDesktop = 24;
  static const double cardPadding        = 16;  // phone
  static const double cardPaddingLarge   = 24;  // tablet/desktop
  static const double sectionGap         = 24;
  static const double cardGap            = 16;

  // Component-specific
  static const double sidebarWidth          = 256;
  static const double sidebarCollapsedWidth = 64;
  static const double navigationRailWidth   = 72;
  static const double bottomNavHeight       = 56;  // phone bottom nav
  static const double appBarHeight          = 56;
  static const double detailPanelWidth      = 400; // tablet detail panel
}
```

### 4.5 Elevation / Shadow System

```dart
/// CARE Platform Elevation
/// Minimal shadows. Enterprise dashboards should feel solid, not floaty.
abstract final class CareElevation {
  // Level 0: flat (most content)
  // border-only separation, no shadow
  static const List<BoxShadow> none = [];

  // Level 1: subtle lift (cards)
  static const List<BoxShadow> sm = [
    BoxShadow(
      color: Color(0x0A000000),  // 4% opacity
      blurRadius: 6,
      offset: Offset(0, 1),
    ),
  ];

  // Level 2: interactive hover state
  static const List<BoxShadow> md = [
    BoxShadow(
      color: Color(0x0F000000),  // 6% opacity
      blurRadius: 10,
      offset: Offset(0, 4),
    ),
  ];

  // Level 3: overlays (modals, slide-overs, command palette)
  static const List<BoxShadow> lg = [
    BoxShadow(
      color: Color(0x1A000000),  // 10% opacity
      blurRadius: 25,
      offset: Offset(0, 10),
    ),
  ];
}
```

### 4.6 Border Radius Scale

```dart
abstract final class CareRadius {
  static const double sm   = 6;   // badges, chips
  static const double base = 8;   // buttons, inputs
  static const double md   = 10;  // cards
  static const double lg   = 12;  // modals, panels
  static const double xl   = 16;  // login card
  static const double full = 999; // pills, avatars
}
```

### 4.7 Animation Timing

```dart
/// CARE Platform Motion
/// Purposeful, minimal animations. No gratuitous bounce or elastic.
abstract final class CareMotion {
  // Durations
  static const Duration fast   = Duration(milliseconds: 100);  // hover, press
  static const Duration normal = Duration(milliseconds: 200);  // page transitions
  static const Duration slow   = Duration(milliseconds: 300);  // panel slide

  // Curves
  static const Curve standard   = Curves.easeOutCubic;    // most transitions
  static const Curve decelerate = Curves.easeOut;          // incoming content
  static const Curve accelerate = Curves.easeIn;           // exiting content
  // No Curves.elasticOut, no Curves.bounceOut. Ever.
}
```

---

## 5. Responsive Breakpoint Strategy

### 5.1 Breakpoint Definitions

```dart
abstract final class CareBreakpoints {
  static const double phone       = 0;     // 0 - 599
  static const double tablet      = 600;   // 600 - 1199
  static const double desktop     = 1200;  // 1200+

  static bool isPhone(BuildContext context) =>
    MediaQuery.sizeOf(context).width < tablet;

  static bool isTablet(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    return w >= tablet && w < desktop;
  }

  static bool isDesktop(BuildContext context) =>
    MediaQuery.sizeOf(context).width >= desktop;
}
```

### 5.2 Adaptive Shell Widget

The app shell switches navigation pattern based on breakpoint:

```
Phone (<600px):
  Scaffold + BottomNavigationBar (5 tabs)

Tablet (600px - 1199px):
  Scaffold + NavigationRail (left, 72px)
  + optional detail panel (right, 400px)

Desktop (1200px+):
  Scaffold + full Sidebar (left, 256px collapsible to 64px)
  Header with breadcrumbs + actions
```

### 5.3 Grid System

| Breakpoint | Grid Columns | Gutter | Margin |
| ---------- | ------------ | ------ | ------ |
| Phone      | 4            | 16px   | 16px   |
| Tablet     | 8            | 20px   | 20px   |
| Desktop    | 12           | 24px   | 24px   |

**Stat cards:**

- Phone: 2 columns (span 2 each)
- Tablet: 4 columns (span 2 each)
- Desktop: 4 columns (span 3 each)

**Agent cards:**

- Phone: 1 column
- Tablet: 2 columns
- Desktop: 3 columns

**Approval cards:**

- Phone: 1 column (full-width)
- Tablet: master-detail (list + detail panel)
- Desktop: 3 columns or master-detail

---

## 6. Component Specifications

### 6.1 CARE-Specific Components to Build

These are domain-specific components not available in standard Material 3:

| Component                 | Description                                     | Used On                |
| ------------------------- | ----------------------------------------------- | ---------------------- |
| `VerificationGradientBar` | Horizontal bar with level color + percentage    | Overview, Verification |
| `PostureBadge`            | Colored pill showing trust posture name         | Agents, Org, DM Team   |
| `StatusBadge`             | Colored pill for active/suspended/revoked       | Agents, Bridges        |
| `UrgencyBadge`            | Colored pill for critical/high/medium/low       | Approvals              |
| `StatCard`                | Icon + value + label + optional sub-content     | Overview, Cost, DM     |
| `GaugeRing`               | Circular SVG progress ring                      | Shadow pass rate       |
| `DimensionGauge`          | Horizontal bar for constraint dimension usage   | Envelopes, Shadow      |
| `ApprovalCard`            | Action card with approve/reject buttons + swipe | Approvals              |
| `ActivityFeedItem`        | Timestamped event row with icon                 | Overview               |
| `TrustChainTree`          | Tree visualization of genesis -> delegation     | Trust Chains           |
| `SpendChart`              | Bar chart for daily cost trend                  | Cost Report            |
| `AnchorDetailPanel`       | Slide-over panel for audit anchor detail        | Audit Trail            |

### 6.2 Component States (Every Component)

Every interactive component must define these states:

- **Default**: normal appearance
- **Loading**: skeleton shimmer (use `CareSkeletonLoader`)
- **Empty**: descriptive message + optional action ("No agents found. Teams may not have been provisioned yet.")
- **Error**: red alert with retry button
- **Disabled**: 50% opacity, no interaction

### 6.3 Stat Card Specification

```
+-------------------------------+
|  [Icon 40x40]     [Chevron]  |
|                               |
|  24 (or $12.40)              |   statValue / statValueCompact
|  Active Agents               |   bodySmall, muted
|  +2 this week | of 30       |   labelSmall, green/muted
+-------------------------------+

Phone: 2-up grid, compact (no sub-content, smaller value)
Tablet/Desktop: 4-up grid, full version with sub-content
```

### 6.4 Approval Card Specification

```
Phone (full-width, swipeable):
+-------------------------------+
| ! CRITICAL        2 min ago   |   urgency badge + timestamp
| send-large-email              |   titleMedium
| Agent: dm-coordinator         |   bodySmall, muted
| Team: dm-team                 |   bodySmall, muted
|                               |
| Reason: Exceeds communication |   bodySmall, italic
| dimension soft limit          |
|                               |
| [Reject]          [Approve]   |   secondary + primary buttons
+-------------------------------+
  <- Swipe left = Reject
  Swipe right = Approve ->

  Left border color = urgency color
  Critical = red, High = orange, Medium = yellow, Low = gray

Tablet (compact, in master list):
+-------------------------------+
| ! send-large-email    2m ago  |
|   dm-coordinator   CRITICAL   |
+-------------------------------+
  Selected row has primaryLight background
```

---

## 7. Accessibility Requirements

### 7.1 WCAG 2.1 AA Compliance (Mandatory)

| Requirement            | Implementation                                                                                                                                                                     |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Color contrast**     | All text meets 4.5:1 ratio (regular) or 3:1 (large text 18sp+). All badge text/background combos verified.                                                                         |
| **Touch targets**      | Minimum 48x48dp for all interactive elements. Approval buttons 56dp height on phone.                                                                                               |
| **Font scaling**       | App must remain usable at 200% system font scale. Layouts use `MediaQuery.textScaleFactor` and avoid fixed-height containers for text.                                             |
| **Screen reader**      | All icons have `semanticLabel`. All badges have aria-equivalent descriptions. Activity feed items are announced with full context.                                                 |
| **Focus order**        | Tab order follows visual reading order. Skip-to-content available on desktop.                                                                                                      |
| **Motion**             | Respect `MediaQuery.disableAnimations` (AccessibilityFeatures). When enabled, all transitions are instant.                                                                         |
| **Color independence** | No information conveyed by color alone. Every status uses color + text label. Every urgency uses color + text badge. Verification gradient bars have level names alongside colors. |

### 7.2 Semantic Labels for Screen Readers

```dart
// Stat card
Semantics(
  label: '12 Active Agents, up 2 this week out of 30 total',
  child: StatCard(...),
)

// Approval card
Semantics(
  label: 'Critical approval: send-large-email by dm-coordinator, submitted 2 minutes ago. Exceeds communication dimension soft limit.',
  child: ApprovalCard(...),
)

// Verification gradient bar
Semantics(
  label: 'Auto Approved: 847 actions, 72% of total verifications',
  child: VerificationGradientBar(...),
)

// Posture badge
Semantics(
  label: 'Trust posture: Supervised',
  child: PostureBadge(posture: TrustPosture.supervised),
)
```

### 7.3 Keyboard Navigation (Desktop)

- All interactive elements reachable via Tab.
- Enter/Space to activate buttons and links.
- Arrow keys to navigate within lists and tables.
- Escape to close modals, slide-overs, and the command palette.
- Focus ring: 2px solid blue-600, 2px offset (matching web `focus-visible` style).

### 7.4 Dark Mode

Material 3 `ColorScheme.fromSeed` generates a dark scheme automatically. Override with CARE-specific tokens:

```dart
// Dark mode overrides
static const Color surfaceDark     = Color(0xFF111827);  // gray-900
static const Color borderDark      = Color(0xFF374151);  // gray-700
static const Color backgroundDark  = Color(0xFF0F172A);  // slate-900
```

The verification gradient colors, posture colors, and urgency colors remain unchanged in dark mode (they are already saturated enough for dark backgrounds). Badge backgrounds should switch to 20% opacity versions.

---

## 8. Real-Time Features

### 8.1 WebSocket Integration

The web app uses WebSocket for real-time activity feed updates and approval notifications. The Flutter app must do the same:

- Connect on login, reconnect on failure (exponential backoff).
- Show connection status indicator in app bar (green dot = connected, yellow = reconnecting, red = disconnected).
- Push new approval items to the top of the queue with a subtle slide-in animation.
- Badge count on Approvals tab updates in real-time.

### 8.2 Push Notifications (Phone/Tablet)

- HELD actions with `critical` urgency trigger a system push notification.
- Tapping the notification opens the Approvals screen with the relevant item pre-selected.
- Non-critical HELD actions update the badge count silently.
- Budget alerts trigger a notification if spend exceeds 80% of daily limit.

### 8.3 Pull-to-Refresh

Available on all scrollable screens on phone and tablet. Uses `RefreshIndicator` widget.

---

## 9. Platform-Specific Considerations

### 9.1 iOS / iPhone

- Respect safe areas (notch, Dynamic Island, home indicator).
- Use `CupertinoScrollbar` for scrollable areas (matches system behavior).
- Haptic feedback on swipe-to-approve/reject (light impact).
- Support Face ID / Touch ID for login token storage (via `local_auth` package).

### 9.2 Android

- Support edge-to-edge display (transparent status bar, gesture navigation).
- Material You dynamic color support (optional: user can use CARE brand colors or system dynamic colors).
- Support fingerprint/face for login token storage.

### 9.3 macOS

- Native window controls (traffic light buttons).
- Menu bar integration (File, Edit, View, Navigate).
- Cmd+, for Settings.
- Respect system accent color or use CARE brand.

### 9.4 Windows

- Title bar with CARE branding.
- Support Windows Hello for biometric login.
- Keyboard shortcuts use Ctrl instead of Cmd.

---

## 10. Screen-by-Screen Wireframe Summaries

### 10.1 Login

All form factors: centered card with CARE logo, operator name field, API token field, remember-me toggle, sign-in button. Footer: "CARE Platform v0.1.0 -- Terrene Foundation".

Phone: card is full-width minus 32px margin. Tablet/Desktop: card is 400px max-width, centered.

### 10.2 Overview

| Element               | Phone                           | Tablet           | Desktop                     |
| --------------------- | ------------------------------- | ---------------- | --------------------------- |
| Stat cards            | 2x2 grid, compact               | 4-column row     | 4-column row                |
| Activity feed         | Full-width, 10 items            | 60% left column  | 60% left column (3/5 grid)  |
| Verification gradient | Full-width below feed           | 40% right column | 40% right column (2/5 grid) |
| Quick actions         | Hidden (bottom nav covers this) | 2x2 grid         | 4-column row                |

### 10.3 Approvals

| Element     | Phone                    | Tablet                              | Desktop                          |
| ----------- | ------------------------ | ----------------------------------- | -------------------------------- |
| Layout      | Single column, card list | Master-detail (list + detail panel) | 3-col card grid or master-detail |
| Interaction | Swipe + buttons          | Tap list item, review in panel      | Click, review in place or panel  |
| Summary bar | Compact: counts only     | Full bar with badge counts          | Full bar with badge counts       |

### 10.4 Agents

| Element      | Phone              | Tablet                      | Desktop                         |
| ------------ | ------------------ | --------------------------- | ------------------------------- |
| Layout       | Single column list | 2-col grid or master-detail | 3-col card grid                 |
| Search       | Sticky search bar  | Sticky search + filter row  | Sticky search + filter row      |
| Agent detail | Full-screen push   | Right detail panel          | Right detail panel or full page |

### 10.5 ShadowEnforcer

| Element                  | Phone               | Tablet                   | Desktop                  |
| ------------------------ | ------------------- | ------------------------ | ------------------------ |
| Agent selector           | Full-width dropdown | Dropdown + posture label | Dropdown + posture label |
| Metric cards             | 2x2 grid            | 3x2 or 4-col             | 6-col row                |
| Pass rate + distribution | Stacked             | Side-by-side             | Side-by-side             |
| Dimension breakdown      | Vertical list       | Full-width chart         | Full-width chart         |
| Upgrade eligibility      | Expandable card     | Full card                | Full card                |

### 10.6 Cost Report

| Element         | Phone                | Tablet                     | Desktop                            |
| --------------- | -------------------- | -------------------------- | ---------------------------------- |
| Period selector | Dropdown at top      | Dropdown in header actions | Dropdown in header actions         |
| Stat cards      | 2x2 grid             | 4-col row                  | 4-col row                          |
| Agent breakdown | Card list (no table) | Table (4 columns)          | Table (4 columns + sort)           |
| Model breakdown | Card list            | Table                      | Table                              |
| Daily trend     | Simplified bar chart | Full bar chart             | Full bar chart with hover tooltips |

### 10.7 Audit Trail

| Element      | Phone                    | Tablet                 | Desktop                  |
| ------------ | ------------------------ | ---------------------- | ------------------------ |
| Filters      | Collapsible filter sheet | Collapsible filter row | Inline filter row        |
| Data display | Card list (2-3 fields)   | Table (4-5 columns)    | Full table (all columns) |
| Detail       | Full-screen push         | Right slide-over panel | Right slide-over panel   |
| Pagination   | Load-more button         | Standard pagination    | Standard pagination      |
| Export       | Share sheet              | CSV/JSON buttons       | CSV/JSON buttons         |

### 10.8 Trust Chains

| Element       | Phone                      | Tablet                    | Desktop                    |
| ------------- | -------------------------- | ------------------------- | -------------------------- |
| Visualization | Vertical tree (scrollable) | Horizontal tree           | Horizontal tree (zoomable) |
| Interaction   | Tap node for detail        | Tap node, detail in panel | Tap node, detail in panel  |

### 10.9 Envelopes

| Element | Phone                                    | Tablet                   | Desktop                 |
| ------- | ---------------------------------------- | ------------------------ | ----------------------- |
| List    | Card list                                | Table                    | Table with sort/filter  |
| Detail  | Full-screen push with 5 dimension gauges | Detail panel with gauges | Detail page with gauges |

### 10.10 Bridges

| Element | Phone                             | Tablet                     | Desktop                    |
| ------- | --------------------------------- | -------------------------- | -------------------------- |
| List    | Card list (purpose, type, status) | Table                      | Full table                 |
| Create  | Multi-step wizard (full-screen)   | Multi-step wizard (dialog) | Multi-step wizard (dialog) |
| Detail  | Full-screen push                  | Detail panel               | Detail page                |

### 10.11 Workspaces

| Element            | Phone                         | Tablet              | Desktop             |
| ------------------ | ----------------------------- | ------------------- | ------------------- |
| Cards              | Single column                 | 2-col grid          | 3-col grid          |
| Bridge connections | Hidden (link to Bridges page) | Diagram below cards | Diagram below cards |

### 10.12 DM Team

| Element         | Phone           | Tablet                | Desktop               |
| --------------- | --------------- | --------------------- | --------------------- |
| Summary stats   | 2x2 grid        | 4-col row             | 4-col row             |
| Agent cards     | Single column   | 2-col grid            | 3-col grid            |
| Task submission | Full-width form | Form card (50% width) | Form card (50% width) |

### 10.13 Organization

| Element    | Phone                                | Tablet                    | Desktop                   |
| ---------- | ------------------------------------ | ------------------------- | ------------------------- |
| Summary    | 3-up stat row                        | 3-up stat row             | 3-up stat row             |
| Team cards | Single column, agents as nested list | 2-col, agent cards inside | 3-col, agent cards inside |

---

## 11. Data Architecture Notes

### 11.1 API Client

The Flutter app should use the same REST API as the web app. Port the API client interface from `apps/web/lib/api.ts`:

- `GET /api/v1/stats/verification` -- verification gradient stats
- `GET /api/v1/held-actions` -- pending approvals
- `POST /api/v1/teams/{team_id}/agents/{agent_id}/approve` -- approve action
- `POST /api/v1/teams/{team_id}/agents/{agent_id}/reject` -- reject action
- `GET /api/v1/trust-chains` -- trust chains
- `GET /api/v1/teams` -- team list
- `GET /api/v1/teams/{team_id}/agents` -- agents per team
- `GET /api/v1/shadow/{agent_id}/metrics` -- shadow metrics
- `GET /api/v1/shadow/{agent_id}/report` -- shadow report
- `GET /api/v1/cost/report?days=N` -- cost report
- `GET /api/v1/bridges` -- bridge list
- `GET /api/v1/workspaces` -- workspace list
- `GET /api/v1/audit/anchors` -- audit anchors
- `GET /api/v1/envelopes` -- envelope list
- `GET /api/v1/dm/status` -- DM team status
- `POST /api/v1/dm/tasks` -- submit task

### 11.2 State Management

Recommend **Riverpod** for state management:

- `AsyncNotifierProvider` for each API endpoint.
- Automatic caching and deduplication.
- Real-time WebSocket updates push into the same providers.
- Pull-to-refresh triggers `ref.invalidate()`.

### 11.3 Offline Support

For phone use, provide minimal offline support:

- Cache the last-fetched state for all screens.
- Show cached data with a "Last updated: 5 min ago" banner when offline.
- Approval actions queue locally and sync when reconnected.

---

## 12. AI-Generated Design Detection Check

Running the mandatory AI slop check against this specification:

| Fingerprint                     | Present? | Notes                                                                   |
| ------------------------------- | -------- | ----------------------------------------------------------------------- |
| Inter used by default           | Yes (1)  | Intentional: Inter is the web app's font. Consistency across platforms. |
| `font-weight: 600` everywhere   | No       | Scale uses 400, 500, 600, 700 appropriately.                            |
| Purple-to-blue gradients        | No       | No gradients in the design.                                             |
| Neon accents on dark            | No       | Dark mode uses muted token overrides.                                   |
| Cards-in-cards nesting          | No       | Flat card hierarchy.                                                    |
| Perfectly uniform spacing       | No       | Spacing varies by context (xs through xxxl).                            |
| Glassmorphism                   | No       |                                                                         |
| Uniform rounded-2xl             | No       | Radius scale from 6 to 16.                                              |
| shadow-lg on every card         | No       | Most cards use `sm` shadow or border-only.                              |
| Gratuitous gradient text        | No       |                                                                         |
| bounce/elastic easing           | No       | Explicitly prohibited in CareMotion.                                    |
| transition-all 300ms everywhere | No       | Durations vary: 100ms, 200ms, 300ms by purpose.                         |

**Verdict: PASS (1 fingerprint)** -- Inter is a deliberate consistency choice, not a default.

---

## Summary of Key Decisions

1. **Phone nav: bottom tabs** (Home, Approvals, Agents, Shadow, More) -- not a drawer. Governance users need persistent visibility of Approvals badge.

2. **Tablet nav: NavigationRail** (72px, icon-only, expandable) -- balances screen real estate with section count.

3. **Desktop nav: full sidebar** (256px, collapsible to 64px) -- mirrors the web app exactly.

4. **Tables become card lists on phone** -- no horizontal scrolling tables. Cards show 2-3 key fields with tap-to-detail.

5. **Master-detail on tablet** for Approvals, Agents, Audit Trail -- eliminates back-and-forth navigation.

6. **Swipe-to-approve/reject on phone** -- optimized for one-handed use of the most time-sensitive screen.

7. **Material 3 with CARE semantic tokens** -- not a custom design system from scratch. Use Flutter's built-in adaptive components, override with CARE colors and typography.

8. **Build order**: Login, Overview, Approvals, Agents first (MVP). Then Shadow, Cost, Verification. Then the remaining 7 screens.

9. **Accessibility is not optional**: 48dp touch targets, 4.5:1 contrast, semantic labels on everything, respect reduced-motion, font scaling to 200%.

10. **Real-time via WebSocket + push notifications**: critical HELD actions get system notifications; badge counts update live.
