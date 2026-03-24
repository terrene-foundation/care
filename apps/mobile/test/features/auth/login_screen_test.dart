// Copyright 2026 Terrene Foundation
// Licensed under the Apache License, Version 2.0

/// Widget tests for the login screen.
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:care_platform_mobile/core/providers/auth_provider.dart';
import 'package:care_platform_mobile/features/auth/login_screen.dart';

/// A slow auth notifier that simulates a long-running login.
/// The login never completes, keeping the UI in the loading state for testing.
class _SlowAuthNotifier extends StateNotifier<AuthState>
    implements AuthNotifier {
  _SlowAuthNotifier() : super(const AuthState(isLoaded: true));

  final _loginCompleter = Completer<String?>();

  @override
  Future<String?> checkAuth() async => null;

  @override
  Future<String?> login(
    String name,
    String token, {
    String baseUrl = defaultBaseUrl,
  }) async {
    state = const AuthState(isLoading: true, isLoaded: true);
    // Never completes during the test -- holds UI in loading state.
    return _loginCompleter.future;
  }

  @override
  Future<void> logout() async {
    state = const AuthState(isLoaded: true);
  }
}

/// An auth notifier that immediately returns an error.
class _FailingAuthNotifier extends StateNotifier<AuthState>
    implements AuthNotifier {
  _FailingAuthNotifier() : super(const AuthState(isLoaded: true));

  @override
  Future<String?> checkAuth() async => null;

  @override
  Future<String?> login(
    String name,
    String token, {
    String baseUrl = defaultBaseUrl,
  }) async {
    state = const AuthState(isLoading: true, isLoaded: true);
    await Future<void>.delayed(Duration.zero);
    final errorMessage = token.isEmpty
        ? 'API token is required.'
        : 'Unable to connect to the CARE Platform API.';
    state = AuthState(isLoaded: true, error: errorMessage);
    return errorMessage;
  }

  @override
  Future<void> logout() async {
    state = const AuthState(isLoaded: true);
  }
}

void main() {
  group('LoginScreen', () {
    Widget buildSubject({List<Override> overrides = const []}) {
      return ProviderScope(
        overrides: overrides,
        child: const MaterialApp(
          home: LoginScreen(),
        ),
      );
    }

    testWidgets('renders with token field, name field, and server URL field',
        (tester) async {
      await tester.pumpWidget(buildSubject());
      await tester.pumpAndSettle();

      // Brand header
      expect(find.text('CARE Platform'), findsOneWidget);

      // Sign in card
      expect(find.text('Sign in'), findsOneWidget);

      // Fields
      expect(find.text('Operator Name'), findsOneWidget);
      expect(find.text('API Token'), findsOneWidget);
      expect(find.text('Server URL'), findsOneWidget);

      // Hints
      expect(find.text('e.g. Jane Smith'), findsOneWidget);
      expect(find.text('Enter your PACT_API_TOKEN'), findsOneWidget);

      // Submit button (may need scroll to see it)
      await tester.scrollUntilVisible(
        find.text('Sign In'),
        100,
        scrollable: find.byType(Scrollable).first,
      );
      expect(find.text('Sign In'), findsOneWidget);
    });

    testWidgets('submit with empty token shows error', (tester) async {
      await tester.pumpWidget(buildSubject(
        overrides: [
          authProvider.overrideWith((_) => _FailingAuthNotifier()),
        ],
      ));
      await tester.pumpAndSettle();

      // Enter a name but leave token empty.
      await tester.enterText(
        find.widgetWithText(TextField, 'e.g. Jane Smith'),
        'Test User',
      );

      // Scroll to the submit button.
      await tester.scrollUntilVisible(
        find.text('Sign In'),
        100,
        scrollable: find.byType(Scrollable).first,
      );

      // Tap sign in.
      await tester.tap(find.text('Sign In'));
      await tester.pumpAndSettle();

      // The screen should stay on login (not navigate away).
      expect(find.text('Sign in'), findsOneWidget);
    });

    testWidgets('login button shows spinner during loading', (tester) async {
      await tester.pumpWidget(buildSubject(
        overrides: [
          authProvider.overrideWith((_) => _SlowAuthNotifier()),
        ],
      ));
      await tester.pumpAndSettle();

      // Enter credentials.
      await tester.enterText(
        find.widgetWithText(TextField, 'e.g. Jane Smith'),
        'Test User',
      );
      await tester.enterText(
        find.widgetWithText(TextField, 'Enter your PACT_API_TOKEN'),
        'test-token',
      );

      // Scroll to submit button.
      await tester.scrollUntilVisible(
        find.text('Sign In'),
        100,
        scrollable: find.byType(Scrollable).first,
      );

      // Tap sign in -- it starts loading.
      await tester.tap(find.text('Sign In'));

      // Pump a single frame so the loading state renders.
      await tester.pump();

      // During loading the button shows a CircularProgressIndicator.
      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      // The "Sign In" text is replaced by the spinner, so it should not
      // be found.
      expect(find.text('Sign In'), findsNothing);
    });
  });
}
