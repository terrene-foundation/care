// Copyright 2026 Terrene Foundation
// Licensed under the Apache License, Version 2.0

/// F-08: Login screen for the CARE Platform mobile app.
///
/// Collects operator name and API token. Validates against the backend
/// health check endpoint before storing credentials. Redirects to the
/// dashboard on success.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/colors.dart';
import '../../core/providers/auth_provider.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _nameController = TextEditingController();
  final _tokenController = TextEditingController();
  final _serverController =
      TextEditingController(text: 'http://localhost:8000');
  bool _remember = true;
  bool _obscureToken = true;

  @override
  void dispose() {
    _nameController.dispose();
    _tokenController.dispose();
    _serverController.dispose();
    super.dispose();
  }

  String? _error;
  bool _isLoading = false;

  Future<void> _handleLogin() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    final baseUrl = _serverController.text.trim();
    final result = await ref.read(authProvider.notifier).login(
          _nameController.text.trim(),
          _tokenController.text.trim(),
          baseUrl: baseUrl,
        );
    if (mounted) {
      if (result == null) {
        // Login succeeded -- update the baseUrl provider so the API client
        // points at the server the user specified.
        ref.read(baseUrlProvider.notifier).state = baseUrl;
      }
      setState(() {
        _isLoading = false;
        _error = result;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Watch auth state so GoRouter redirect triggers on login success.
    ref.watch(authProvider);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(CareSpacing.xl),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 400),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Brand
                  _BrandHeader(),
                  const SizedBox(height: 32),

                  // Login card
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(CareSpacing.xl),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Sign in',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Enter your operator credentials to access the dashboard.',
                            style: TextStyle(
                              fontSize: 13,
                              color: CareColors.muted,
                            ),
                          ),
                          const SizedBox(height: 24),

                          // Error
                          if (_error != null) ...[
                            _ErrorBanner(message: _error!),
                            const SizedBox(height: 16),
                          ],

                          // Operator name
                          const Text(
                            'Operator Name',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _nameController,
                            enabled: !_isLoading,
                            textInputAction: TextInputAction.next,
                            decoration: const InputDecoration(
                              hintText: 'e.g. Jane Smith',
                            ),
                          ),
                          const SizedBox(height: 16),

                          // API Token
                          const Text(
                            'API Token',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _tokenController,
                            enabled: !_isLoading,
                            obscureText: _obscureToken,
                            textInputAction: TextInputAction.next,
                            style: const TextStyle(fontFamily: 'monospace'),
                            decoration: InputDecoration(
                              hintText: 'Enter your PACT_API_TOKEN',
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscureToken
                                      ? Icons.visibility_off_outlined
                                      : Icons.visibility_outlined,
                                  size: 20,
                                ),
                                onPressed: () {
                                  setState(() {
                                    _obscureToken = !_obscureToken;
                                  });
                                },
                              ),
                            ),
                          ),
                          Text(
                            'The bearer token configured in your CARE Platform backend.',
                            style: TextStyle(
                              fontSize: 11,
                              color: CareColors.muted,
                            ),
                          ),
                          const SizedBox(height: 16),

                          // Server URL
                          const Text(
                            'Server URL',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _serverController,
                            enabled: !_isLoading,
                            textInputAction: TextInputAction.done,
                            keyboardType: TextInputType.url,
                            style: const TextStyle(fontFamily: 'monospace'),
                            decoration: const InputDecoration(
                              hintText: 'http://localhost:8000',
                            ),
                            onSubmitted: (_) => _handleLogin(),
                          ),
                          const SizedBox(height: 16),

                          // Remember me
                          Row(
                            children: [
                              SizedBox(
                                width: 20,
                                height: 20,
                                child: Checkbox(
                                  value: _remember,
                                  onChanged: _isLoading
                                      ? null
                                      : (v) {
                                          setState(() {
                                            _remember = v ?? true;
                                          });
                                        },
                                ),
                              ),
                              const SizedBox(width: 8),
                              const Text(
                                'Remember me',
                                style: TextStyle(fontSize: 13),
                              ),
                            ],
                          ),
                          const SizedBox(height: 24),

                          // Submit
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              onPressed: _isLoading ? null : _handleLogin,
                              child: _isLoading
                                  ? const SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        color: Colors.white,
                                      ),
                                    )
                                  : const Text('Sign In'),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Footer
                  const SizedBox(height: 24),
                  Text(
                    'CARE Platform v0.1.0 -- Terrene Foundation',
                    style: TextStyle(
                      fontSize: 11,
                      color: CareColors.muted,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Sub-widgets
// ---------------------------------------------------------------------------

class _BrandHeader extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            color: CareColors.primary,
            borderRadius: BorderRadius.circular(14),
            boxShadow: CareElevation.md,
          ),
          alignment: Alignment.center,
          child: const Text(
            'C',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        const SizedBox(height: 16),
        const Text(
          'CARE Platform',
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Governed operational model for AI agent orchestration',
          style: TextStyle(
            fontSize: 13,
            color: CareColors.muted,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}

class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFFFEE2E2),
        borderRadius: BorderRadius.circular(CareRadius.base),
        border: Border.all(color: const Color(0xFFFECACA)),
      ),
      child: Text(
        message,
        style: const TextStyle(
          fontSize: 13,
          color: Color(0xFFB91C1C),
        ),
      ),
    );
  }
}
