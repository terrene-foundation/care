"""Session state management for multi-turn assessment conversations."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SessionState(str, Enum):
    """Assessment conversation phases."""

    WELCOME = "welcome"
    SCREENING = "screening"
    ORG_STRUCTURE = "org_structure"
    CONSTRAINTS = "constraints"
    DATA_SENSITIVITY = "data_sensitivity"
    COMMUNICATION = "communication"
    BRIDGES = "bridges"
    TRUST_POSTURE = "trust_posture"
    CONFIRMATION = "confirmation"
    DIAGNOSIS = "diagnosis"
    RECOMMENDATIONS = "recommendations"
    GENERATION = "generation"
    COMPLETE = "complete"
    ABANDONED = "abandoned"


# Assessment phases group states for progress tracking
PHASE_MAP: dict[SessionState, str] = {
    SessionState.WELCOME: "Assess",
    SessionState.SCREENING: "Assess",
    SessionState.ORG_STRUCTURE: "Assess",
    SessionState.CONSTRAINTS: "Assess",
    SessionState.DATA_SENSITIVITY: "Assess",
    SessionState.COMMUNICATION: "Assess",
    SessionState.BRIDGES: "Assess",
    SessionState.TRUST_POSTURE: "Assess",
    SessionState.CONFIRMATION: "Assess",
    SessionState.DIAGNOSIS: "Diagnose",
    SessionState.RECOMMENDATIONS: "Recommend",
    SessionState.GENERATION: "Generate",
    SessionState.COMPLETE: "Complete",
    SessionState.ABANDONED: "Abandoned",
}

# Progress percentage per state (for progress bar)
STATE_PROGRESS: dict[SessionState, int] = {
    SessionState.WELCOME: 0,
    SessionState.SCREENING: 5,
    SessionState.ORG_STRUCTURE: 15,
    SessionState.CONSTRAINTS: 30,
    SessionState.DATA_SENSITIVITY: 45,
    SessionState.COMMUNICATION: 55,
    SessionState.BRIDGES: 65,
    SessionState.TRUST_POSTURE: 75,
    SessionState.CONFIRMATION: 80,
    SessionState.DIAGNOSIS: 85,
    SessionState.RECOMMENDATIONS: 90,
    SessionState.GENERATION: 95,
    SessionState.COMPLETE: 100,
    SessionState.ABANDONED: 0,
}


@dataclass
class Message:
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedData:
    """Structured data extracted from conversation so far."""

    org_name: str | None = None
    org_type: str | None = None  # hierarchical, matrix, flat, project-based
    is_hierarchical: bool | None = None

    departments: list[dict[str, Any]] = field(default_factory=list)
    teams: list[dict[str, Any]] = field(default_factory=list)
    roles: list[dict[str, Any]] = field(default_factory=list)

    # Constraint envelopes (per-role or per-team)
    financial_constraints: list[dict[str, Any]] = field(default_factory=list)
    operational_constraints: list[dict[str, Any]] = field(default_factory=list)
    temporal_constraints: list[dict[str, Any]] = field(default_factory=list)
    data_access_constraints: list[dict[str, Any]] = field(default_factory=list)
    communication_constraints: list[dict[str, Any]] = field(default_factory=list)

    # Bridges
    bridges: list[dict[str, Any]] = field(default_factory=list)

    # Trust posture
    current_ai_usage: str | None = None
    target_trust_posture: str | None = None  # pseudo, supervised, shared_planning, etc.

    # Gaps (questions the user couldn't answer)
    gaps: list[dict[str, str]] = field(default_factory=list)


@dataclass
class Session:
    """A single assessment conversation session."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    state: SessionState = SessionState.WELCOME
    messages: list[Message] = field(default_factory=list)
    extracted: ExtractedData = field(default_factory=ExtractedData)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def phase(self) -> str:
        return PHASE_MAP.get(self.state, "Unknown")

    @property
    def progress(self) -> int:
        return STATE_PROGRESS.get(self.state, 0)

    def add_message(self, role: str, content: str, **metadata: Any) -> Message:
        msg = Message(role=role, content=content, metadata=metadata)
        self.messages.append(msg)
        self.updated_at = datetime.now(timezone.utc)
        return msg

    def advance(self, new_state: SessionState) -> None:
        self.state = new_state
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "state": self.state.value,
            "phase": self.phase,
            "progress": self.progress,
            "message_count": len(self.messages),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "extracted": {
                "org_name": self.extracted.org_name,
                "departments": len(self.extracted.departments),
                "teams": len(self.extracted.teams),
                "roles": len(self.extracted.roles),
                "bridges": len(self.extracted.bridges),
                "gaps": len(self.extracted.gaps),
            },
        }
