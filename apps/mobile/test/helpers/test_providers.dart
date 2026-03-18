// Copyright 2026 Terrene Foundation
// Licensed under the Apache License, Version 2.0

/// Shared Riverpod provider overrides for widget tests.
///
/// Provides mock data so widget tests run without hitting a real API.
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:care_platform_mobile/core/api/care_websocket_client.dart';
import 'package:care_platform_mobile/core/models/models.dart';
import 'package:care_platform_mobile/core/providers/auth_provider.dart';
import 'package:care_platform_mobile/core/providers/websocket_provider.dart';
import 'package:care_platform_mobile/features/approvals/providers/approvals_providers.dart';
import 'package:care_platform_mobile/features/dashboard/providers/dashboard_providers.dart';
import 'package:care_platform_mobile/features/shadow/providers/shadow_providers.dart';

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const mockAuthState = AuthState(
  user: AuthUser(name: 'Test Operator', role: UserRole.governanceOfficer),
  token: 'test-token-123',
  isLoaded: true,
);

const mockVerificationStats = VerificationStats(
  autoApproved: 120,
  flagged: 15,
  held: 8,
  blocked: 3,
  total: 146,
);

final mockTrustChains = [
  const TrustChainSummary(
    agentId: 'agent-1',
    name: 'Research Agent',
    teamId: 'dm-team',
    posture: 'supervised',
    status: AgentStatus.active,
  ),
  const TrustChainSummary(
    agentId: 'agent-2',
    name: 'Planning Agent',
    teamId: 'dm-team',
    posture: 'shared_planning',
    status: AgentStatus.active,
  ),
];

final mockHeldActions = <HeldAction>[
  const HeldAction(
    actionId: 'action-1',
    agentId: 'agent-1',
    teamId: 'dm-team',
    action: 'deploy_model',
    reason: 'Exceeds daily spend limit',
    urgency: 'high',
    submittedAt: '2026-03-16T10:00:00Z',
  ),
];

final mockDashboardData = DashboardData(
  stats: mockVerificationStats,
  trustChains: mockTrustChains,
  heldActions: mockHeldActions,
);

const mockShadowData = ShadowData(
  agentId: 'agent-1',
  agentName: 'Research Agent',
  posture: 'supervised',
  totalEvaluations: 200,
  autoApproved: 160,
  flagged: 20,
  held: 12,
  blocked: 8,
  passRate: 80.0,
  blockRate: 4.0,
  upgradeEligible: true,
  recommendation: 'Agent meets all criteria for upgrade to SHARED_PLANNING.',
  dimensionBreakdown: {
    'Financial': 0.95,
    'Operational': 0.92,
    'Temporal': 0.98,
    'Data Access': 0.90,
    'Communication': 0.96,
  },
);

// ---------------------------------------------------------------------------
// Provider overrides
// ---------------------------------------------------------------------------

/// Common overrides for authenticated screens.
List<Override> authenticatedOverrides() {
  return [
    authProvider.overrideWith((_) => _MockAuthNotifier()),
    connectionStateProvider
        .overrideWith((ref) => WebSocketState.connected),
    baseUrlProvider.overrideWith((ref) => 'http://localhost:8000'),
  ];
}

/// Overrides for the dashboard screen tests.
List<Override> dashboardOverrides() {
  return [
    ...authenticatedOverrides(),
    dashboardProvider.overrideWith((ref) async => mockDashboardData),
    platformEventsProvider
        .overrideWith((ref) => const Stream<PlatformEvent>.empty()),
  ];
}

/// Overrides for the approvals screen tests.
List<Override> approvalsOverrides({List<ApprovalItem>? items}) {
  return [
    ...authenticatedOverrides(),
    approvalsProvider.overrideWith((ref) async => items ?? []),
    approvalSummaryProvider.overrideWith((ref) {
      final list = items ?? [];
      final critical = list.where((i) => i.urgency == 'critical').length;
      return (pending: list.length, critical: critical, resolved: 0);
    }),
  ];
}

/// Overrides for the shadow screen tests.
List<Override> shadowOverrides({ShadowData? data}) {
  return [
    ...authenticatedOverrides(),
    shadowAgentListProvider.overrideWith((ref) async => mockTrustChains),
    selectedShadowAgentProvider.overrideWith((ref) => null),
    shadowDataProvider.overrideWith((ref) async => data ?? mockShadowData),
  ];
}

// ---------------------------------------------------------------------------
// Overflow error suppression for test viewports
// ---------------------------------------------------------------------------

/// Suppresses RenderFlex overflow errors that occur because the test viewport
/// is smaller than phone screens. Call in setUp or at the start of a test,
/// and restore in tearDown.
///
/// Returns the original handler so it can be restored.
FlutterExceptionHandler? suppressOverflowErrors() {
  final original = FlutterError.onError;
  FlutterError.onError = (details) {
    final isOverflow =
        details.exceptionAsString().contains('overflowed by');
    if (!isOverflow) {
      // Forward non-overflow errors to the original handler.
      original?.call(details);
    }
  };
  return original;
}

// ---------------------------------------------------------------------------
// Mock notifiers
// ---------------------------------------------------------------------------

/// A mock [AuthNotifier] that skips secure storage entirely and sets state
/// directly. Used in tests that need an authenticated user.
class _MockAuthNotifier extends StateNotifier<AuthState>
    implements AuthNotifier {
  _MockAuthNotifier() : super(mockAuthState);

  @override
  Future<String?> checkAuth() async => null;

  @override
  Future<String?> login(
    String name,
    String token, {
    String baseUrl = defaultBaseUrl,
  }) async =>
      null;

  @override
  Future<void> logout() async {
    state = const AuthState(isLoaded: true);
  }
}
