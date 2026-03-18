# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Tests for Alembic database migration infrastructure (Task 5023).

Validates that:
- alembic.ini exists and has valid configuration
- alembic/env.py exists and is importable
- alembic/versions/ directory exists
- Initial migration creates the same tables as the custom migration system
- Alembic script_directory is configured correctly
- The initial migration includes all 8 trust store tables
"""

import configparser
from pathlib import Path

# Repository root — alembic.ini lives here
REPO_ROOT = Path(__file__).resolve().parents[3]


class TestAlembicInfrastructure:
    """Alembic infrastructure files must exist and be correctly configured."""

    def test_alembic_ini_exists(self):
        """alembic.ini must exist at the repository root."""
        ini_path = REPO_ROOT / "alembic.ini"
        assert ini_path.is_file(), f"alembic.ini not found at {ini_path}"

    def test_alembic_ini_has_valid_config(self):
        """alembic.ini must be parseable and contain required sections."""
        ini_path = REPO_ROOT / "alembic.ini"
        config = configparser.ConfigParser()
        config.read(str(ini_path))
        assert "alembic" in config.sections(), "alembic.ini must have an [alembic] section"

    def test_alembic_ini_script_location(self):
        """alembic.ini must point script_location to the alembic/ directory."""
        ini_path = REPO_ROOT / "alembic.ini"
        config = configparser.ConfigParser()
        config.read(str(ini_path))
        script_location = config.get("alembic", "script_location")
        assert script_location == "alembic", (
            f"script_location should be 'alembic', got '{script_location}'"
        )

    def test_alembic_ini_sqlalchemy_url_uses_env(self):
        """alembic.ini must not hardcode a database URL — it should be overridden in env.py."""
        ini_path = REPO_ROOT / "alembic.ini"
        content = ini_path.read_text()
        # The sqlalchemy.url in alembic.ini should be empty or a placeholder
        # because the real URL comes from the DATABASE_URL environment variable
        assert "postgresql://user:pass" not in content, (
            "alembic.ini must not contain hardcoded credentials"
        )
        assert "sqlite:///" not in content or "sqlalchemy.url = sqlite:///" not in content, (
            "alembic.ini should not hardcode a sqlite URL for production use"
        )

    def test_alembic_env_py_exists(self):
        """alembic/env.py must exist."""
        env_py = REPO_ROOT / "alembic" / "env.py"
        assert env_py.is_file(), f"alembic/env.py not found at {env_py}"

    def test_alembic_versions_directory_exists(self):
        """alembic/versions/ directory must exist for migration scripts."""
        versions_dir = REPO_ROOT / "alembic" / "versions"
        assert versions_dir.is_dir(), f"alembic/versions/ not found at {versions_dir}"

    def test_alembic_script_mako_exists(self):
        """alembic/script.py.mako template must exist for generating migrations."""
        mako_path = REPO_ROOT / "alembic" / "script.py.mako"
        assert mako_path.is_file(), f"alembic/script.py.mako not found at {mako_path}"


class TestInitialMigration:
    """The initial Alembic migration must create all trust store tables."""

    # These are the 8 tables created by the custom migration system in migrations.py
    EXPECTED_TABLES = [
        "envelopes",
        "audit_anchors",
        "posture_changes",
        "revocations",
        "genesis_records",
        "delegations",
        "attestations",
        "org_definitions",
    ]

    def test_initial_migration_file_exists(self):
        """At least one migration file must exist in alembic/versions/."""
        versions_dir = REPO_ROOT / "alembic" / "versions"
        migration_files = list(versions_dir.glob("*.py"))
        # Exclude __pycache__ and __init__ files
        migration_files = [f for f in migration_files if not f.name.startswith("__")]
        assert len(migration_files) >= 1, "No migration files found in alembic/versions/"

    def test_initial_migration_contains_all_tables(self):
        """The initial migration must reference all 8 trust store tables."""
        versions_dir = REPO_ROOT / "alembic" / "versions"
        migration_files = [f for f in versions_dir.glob("*.py") if not f.name.startswith("__")]
        assert len(migration_files) >= 1, "No migration files found"

        # Read all migration content
        all_content = ""
        for mf in migration_files:
            all_content += mf.read_text()

        for table in self.EXPECTED_TABLES:
            assert table in all_content, (
                f"Table '{table}' not found in any migration file. "
                f"The initial migration must create all trust store tables."
            )

    def test_initial_migration_has_upgrade_and_downgrade(self):
        """The initial migration must have both upgrade() and downgrade() functions."""
        versions_dir = REPO_ROOT / "alembic" / "versions"
        migration_files = [f for f in versions_dir.glob("*.py") if not f.name.startswith("__")]
        assert len(migration_files) >= 1

        content = migration_files[0].read_text()
        assert "def upgrade()" in content, "Migration must have an upgrade() function"
        assert "def downgrade()" in content, "Migration must have a downgrade() function"

    def test_initial_migration_has_revision_identifiers(self):
        """The initial migration must have revision and down_revision set."""
        versions_dir = REPO_ROOT / "alembic" / "versions"
        migration_files = [f for f in versions_dir.glob("*.py") if not f.name.startswith("__")]
        assert len(migration_files) >= 1

        content = migration_files[0].read_text()
        assert "revision" in content, "Migration must set a revision identifier"
        assert "down_revision" in content, "Migration must set a down_revision"

    def test_initial_migration_creates_indexes(self):
        """The initial migration must create indexes matching the custom migration system."""
        versions_dir = REPO_ROOT / "alembic" / "versions"
        migration_files = [f for f in versions_dir.glob("*.py") if not f.name.startswith("__")]
        assert len(migration_files) >= 1

        all_content = ""
        for mf in migration_files:
            all_content += mf.read_text()

        # Key indexes from the custom migration system
        expected_indexes = [
            "idx_envelopes_agent",
            "idx_anchors_agent",
            "idx_anchors_timestamp",
            "idx_anchors_level",
            "idx_posture_agent",
            "idx_revocations_agent",
            "idx_delegations_delegator",
            "idx_delegations_delegatee",
            "idx_attestations_agent",
        ]
        for idx in expected_indexes:
            assert idx in all_content, (
                f"Index '{idx}' not found in migration files. "
                f"The initial migration must create all indexes from the custom migration system."
            )


class TestAlembicEnvPy:
    """alembic/env.py must be configured to read DATABASE_URL from the environment."""

    def test_env_py_references_database_url(self):
        """env.py must read the database URL from the DATABASE_URL environment variable."""
        env_py = REPO_ROOT / "alembic" / "env.py"
        content = env_py.read_text()
        assert "DATABASE_URL" in content, (
            "alembic/env.py must reference DATABASE_URL environment variable"
        )

    def test_env_py_has_run_migrations_functions(self):
        """env.py must have run_migrations_offline and run_migrations_online."""
        env_py = REPO_ROOT / "alembic" / "env.py"
        content = env_py.read_text()
        assert "run_migrations_offline" in content, "env.py must define run_migrations_offline()"
        assert "run_migrations_online" in content, "env.py must define run_migrations_online()"
