// Copyright 2026 Terrene Foundation
// Licensed under the Apache License, Version 2.0

/// Widget tests for the ShadowEnforcer dashboard screen.
import 'dart:ui';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:care_platform_mobile/features/shadow/shadow_screen.dart';

import '../../helpers/test_providers.dart';

void main() {
  group('ShadowScreen', () {
    late FlutterExceptionHandler? originalHandler;

    setUp(() {
      originalHandler = suppressOverflowErrors();
    });

    tearDown(() {
      FlutterError.onError = originalHandler;
    });

    Widget buildSubject({List<Override> overrides = const []}) {
      return ProviderScope(
        overrides: [...shadowOverrides(), ...overrides],
        child: const MaterialApp(
          home: ShadowScreen(),
        ),
      );
    }

    testWidgets('renders the ShadowEnforcer screen', (tester) async {
      // Use a phone-width viewport (< 600) so the stat grid uses 2 columns
      // with enough height per cell to avoid overflow.
      tester.view.physicalSize = const Size(500, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(buildSubject());
      await tester.pumpAndSettle();

      // AppBar title
      expect(find.text('ShadowEnforcer'), findsOneWidget);
    });

    testWidgets('renders with agent selector', (tester) async {
      // Use a phone-width viewport (< 600) so the stat grid uses 2 columns
      // with enough height per cell to avoid overflow.
      tester.view.physicalSize = const Size(500, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(buildSubject());
      await tester.pumpAndSettle();

      // The agent selector should contain "Select Agent" label
      expect(find.text('Select Agent'), findsOneWidget);

      // The dropdown should be present
      expect(find.byType(DropdownButtonFormField<String>), findsOneWidget);
    });

    testWidgets('shows metrics cards with shadow data', (tester) async {
      // Use a phone-width viewport (< 600) so the stat grid uses 2 columns
      // with enough height per cell to avoid overflow.
      tester.view.physicalSize = const Size(500, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(buildSubject());
      await tester.pumpAndSettle();

      // Metric values from mockShadowData
      expect(find.text('200'), findsOneWidget); // total evaluations
      expect(find.text('80.0%'), findsWidgets); // pass rate (stat card + gauge)
      expect(find.text('4.0%'), findsOneWidget); // block rate
      expect(find.text('160'), findsOneWidget); // auto approved
    });

    testWidgets('shows upgrade eligibility section', (tester) async {
      // Use a phone-width viewport (< 600) so the stat grid uses 2 columns
      // with enough height per cell to avoid overflow.
      tester.view.physicalSize = const Size(500, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(buildSubject());
      await tester.pumpAndSettle();

      // Upgrade eligibility heading
      expect(find.text('Upgrade Eligibility'), findsOneWidget);

      // Recommendation text from mock
      expect(
        find.text(
          'Agent meets all criteria for upgrade to SHARED_PLANNING.',
        ),
        findsOneWidget,
      );
    });

    testWidgets('shows dimension compliance section', (tester) async {
      // Use a phone-width viewport (< 600) so the stat grid uses 2 columns
      // with enough height per cell to avoid overflow.
      tester.view.physicalSize = const Size(500, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(buildSubject());
      await tester.pumpAndSettle();

      expect(find.text('Dimension Compliance'), findsOneWidget);

      // Dimension labels from mockShadowData.dimensionBreakdown
      expect(find.text('Financial'), findsOneWidget);
      expect(find.text('Operational'), findsOneWidget);
      expect(find.text('Temporal'), findsOneWidget);
      expect(find.text('Data Access'), findsOneWidget);
      expect(find.text('Communication'), findsOneWidget);
    });
  });
}
