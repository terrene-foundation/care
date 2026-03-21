# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Smoke tests for pact package."""


def test_package_imports():
    """Verify the pact package is importable."""
    import pact

    assert pact.__version__ == "0.1.0"


def test_submodules_importable():
    """Verify all submodules are importable."""
    import pact.build.config
    import pact.build.workspace
    import pact.trust
    import pact.trust.audit
    import pact.trust.constraint
    import pact.use.execution

    assert pact.trust is not None
    assert pact.trust.constraint is not None
    assert pact.use.execution is not None
    assert pact.trust.audit is not None
    assert pact.build.workspace is not None
    assert pact.build.config is not None
