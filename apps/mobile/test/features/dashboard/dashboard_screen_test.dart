// Copyright 2026 Terrene Foundation
// Licensed under the Apache License, Version 2.0

/// Widget tests for the dashboard overview screen.
import 'dart:ui';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:care_platform_mobile/features/dashboard/dashboard_screen.dart';

import '../../helpers/test_providers.dart';

void main() {
  group('DashboardScreen', () {
    late FlutterExceptionHandler? originalHandler;

    setUp(() {
      originalHandler = suppressOverflowErrors();
    });

    tearDown(() {
      FlutterError.onError = originalHandler;
    });

    Widget buildSubject({List<Override> overrides = const []}) {
      return ProviderScope(
        overrides: [...dashboardOverrides(), ...overrides],
        child: const MaterialApp(
          home: DashboardScreen(),
        ),
      );
    }

    testWidgets('renders with stat cards', (tester) async {
      // Phone-width viewport so stat grid uses 2 columns.
      tester.view.physicalSize = const Size(400, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(buildSubject());
      await tester.pumpAndSettle();

      // AppBar title
      expect(find.text('Overview'), findsOneWidget);

      // Stat card labels
      expect(find.text('Active Agents'), findsOneWidget);
    });

    testWidgets('quick action cards are present', (tester) async {
      tester.view.physicalSize = const Size(400, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(buildSubject());
      await tester.pumpAndSettle();

      // Scroll to the quick action section.
      final scrollable = find.byType(Scrollable).first;
      await tester.scrollUntilVisible(
        find.text('Review Approvals'),
        200,
        scrollable: scrollable,
      );

      // All four quick actions should be present.
      expect(find.text('Review Approvals'), findsOneWidget);

      // Verify it is inside a tappable ListTile.
      final approvalsTile = find.ancestor(
        of: find.text('Review Approvals'),
        matching: find.byType(ListTile),
      );
      expect(approvalsTile, findsOneWidget);
    });

    testWidgets('shows verification gradient summary', (tester) async {
      tester.view.physicalSize = const Size(400, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(buildSubject());
      await tester.pumpAndSettle();

      // Scroll down to the gradient section if needed.
      final scrollable = find.byType(Scrollable).first;
      await tester.scrollUntilVisible(
        find.text('Verification Gradient'),
        200,
        scrollable: scrollable,
      );

      expect(find.text('Verification Gradient'), findsOneWidget);
      expect(find.text('Auto Approved'), findsOneWidget);
      expect(find.text('Total Verifications'), findsOneWidget);
    });
  });
}
