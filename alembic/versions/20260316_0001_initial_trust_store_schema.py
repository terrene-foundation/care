# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Initial trust store schema — creates all tables matching migrations.py v1.

Creates the 8 trust store tables with indexes, matching the schema defined
in pact.persistence.migrations (Migration v1) and
pact.persistence.postgresql_store.PostgreSQLTrustStore._create_tables.

Tables created:
- envelopes: Constraint envelopes (EATP trust boundaries)
- audit_anchors: Audit anchors (append-only, immutable)
- posture_changes: Trust posture history (append-only, immutable)
- revocations: Trust revocation records
- genesis_records: Genesis records (write-once trust roots)
- delegations: Delegation records (trust chain extensions)
- attestations: Capability attestations
- org_definitions: Organization definitions

Revision ID: 0001
Revises: None
Create Date: 2026-03-16
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -- Constraint envelopes --
    op.create_table(
        "envelopes",
        sa.Column("envelope_id", sa.Text(), primary_key=True),
        sa.Column("agent_id", sa.Text(), nullable=True),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.Text(),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
    )
    op.create_index("idx_envelopes_agent", "envelopes", ["agent_id"])

    # -- Audit anchors (append-only) --
    op.create_table(
        "audit_anchors",
        sa.Column("anchor_id", sa.Text(), primary_key=True),
        sa.Column("agent_id", sa.Text(), nullable=True),
        sa.Column("action", sa.Text(), nullable=True),
        sa.Column("verification_level", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.Text(), nullable=True),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.Text(),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
    )
    op.create_index("idx_anchors_agent", "audit_anchors", ["agent_id"])
    op.create_index("idx_anchors_timestamp", "audit_anchors", ["timestamp"])
    op.create_index("idx_anchors_level", "audit_anchors", ["verification_level"])

    # -- Posture changes (append-only) --
    op.create_table(
        "posture_changes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agent_id", sa.Text(), nullable=False),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.Text(),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
    )
    op.create_index("idx_posture_agent", "posture_changes", ["agent_id"])

    # -- Revocations --
    op.create_table(
        "revocations",
        sa.Column("revocation_id", sa.Text(), primary_key=True),
        sa.Column("agent_id", sa.Text(), nullable=True),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.Text(),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
    )
    op.create_index("idx_revocations_agent", "revocations", ["agent_id"])

    # -- Genesis records --
    op.create_table(
        "genesis_records",
        sa.Column("authority_id", sa.Text(), primary_key=True),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.Text(),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
    )

    # -- Delegation records --
    op.create_table(
        "delegations",
        sa.Column("delegation_id", sa.Text(), primary_key=True),
        sa.Column("delegator_id", sa.Text(), nullable=False),
        sa.Column("delegatee_id", sa.Text(), nullable=False),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.Text(),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
    )
    op.create_index("idx_delegations_delegator", "delegations", ["delegator_id"])
    op.create_index("idx_delegations_delegatee", "delegations", ["delegatee_id"])

    # -- Capability attestations --
    op.create_table(
        "attestations",
        sa.Column("attestation_id", sa.Text(), primary_key=True),
        sa.Column("agent_id", sa.Text(), nullable=False),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.Text(),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
    )
    op.create_index("idx_attestations_agent", "attestations", ["agent_id"])

    # -- Organization definitions --
    op.create_table(
        "org_definitions",
        sa.Column("org_id", sa.Text(), primary_key=True),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.Text(),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
    )


def downgrade() -> None:
    op.drop_table("org_definitions")
    op.drop_index("idx_attestations_agent", table_name="attestations")
    op.drop_table("attestations")
    op.drop_index("idx_delegations_delegatee", table_name="delegations")
    op.drop_index("idx_delegations_delegator", table_name="delegations")
    op.drop_table("delegations")
    op.drop_table("genesis_records")
    op.drop_index("idx_revocations_agent", table_name="revocations")
    op.drop_table("revocations")
    op.drop_index("idx_posture_agent", table_name="posture_changes")
    op.drop_table("posture_changes")
    op.drop_index("idx_anchors_level", table_name="audit_anchors")
    op.drop_index("idx_anchors_timestamp", table_name="audit_anchors")
    op.drop_index("idx_anchors_agent", table_name="audit_anchors")
    op.drop_table("audit_anchors")
    op.drop_index("idx_envelopes_agent", table_name="envelopes")
    op.drop_table("envelopes")
