// Copyright 2026 Terrene Foundation
// Licensed under the Apache License, Version 2.0

/// Widget tests for the approvals queue screen.
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:care_platform_mobile/features/approvals/approvals_screen.dart';
import 'package:care_platform_mobile/features/approvals/providers/approvals_providers.dart';

import '../../helpers/test_providers.dart';

void main() {
  group('ApprovalsScreen', () {
    Widget buildSubject({List<ApprovalItem>? items}) {
      return ProviderScope(
        overrides: approvalsOverrides(items: items),
        child: const MaterialApp(
          home: ApprovalsScreen(),
        ),
      );
    }

    testWidgets('renders the approval queue screen', (tester) async {
      await tester.pumpWidget(buildSubject());
      await tester.pumpAndSettle();

      // AppBar title
      expect(find.text('Approval Queue'), findsOneWidget);
    });

    testWidgets('shows empty state when no held actions', (tester) async {
      await tester.pumpWidget(buildSubject(items: []));
      await tester.pumpAndSettle();

      // The _AllClearCard should show "All caught up"
      expect(find.text('All caught up'), findsOneWidget);
      expect(
        find.text('No actions are awaiting approval right now.'),
        findsOneWidget,
      );
    });

    testWidgets('shows approval cards when items exist', (tester) async {
      final items = mockHeldActions.map((action) {
        return ApprovalItem(heldAction: action, urgency: action.urgency);
      }).toList();

      await tester.pumpWidget(buildSubject(items: items));
      await tester.pumpAndSettle();

      // Should show the action name
      expect(find.text('deploy_model'), findsOneWidget);

      // Should show approve/reject buttons
      expect(find.text('Approve'), findsOneWidget);
      expect(find.text('Reject'), findsOneWidget);

      // Should show the urgency badge
      expect(find.text('HIGH'), findsOneWidget);
    });

    testWidgets('summary bar shows correct counts', (tester) async {
      final items = mockHeldActions.map((action) {
        return ApprovalItem(heldAction: action, urgency: action.urgency);
      }).toList();

      await tester.pumpWidget(buildSubject(items: items));
      await tester.pumpAndSettle();

      // Summary bar should show pending count
      expect(find.text('Pending'), findsOneWidget);
    });
  });
}
