// Copyright 2026 Terrene Foundation
// Licensed under the Apache License, Version 2.0

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:care_platform_mobile/main.dart';

void main() {
  testWidgets('CARE app renders login screen when unauthenticated',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(child: CareApp()),
    );
    await tester.pumpAndSettle();

    // The app should show the login screen since no credentials are stored.
    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('CARE Platform'), findsOneWidget);
  });
}
