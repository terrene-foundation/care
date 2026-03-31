"""Conversation engine — orchestrates the multi-turn assessment journey."""

from __future__ import annotations

from typing import Any, AsyncIterator

from care.conversation.llm import LLMProvider
from care.conversation.prompts import (
    DIAGNOSIS_SYSTEM,
    EXTRACTION_SYSTEM,
    RECOMMENDATION_SYSTEM,
    SCREENING_HIERARCHICAL,
    SCREENING_NON_HIERARCHICAL,
    STATE_TRANSITION_PROMPTS,
    SYSTEM_PROMPT,
    WELCOME_MESSAGE,
)
from care.conversation.session import ExtractedData, Session, SessionState


class ConversationEngine:
    """Drives the assessment conversation through all phases."""

    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm
        self._sessions: dict[str, Session] = {}

    def create_session(self) -> Session:
        session = Session()
        session.add_message("assistant", WELCOME_MESSAGE)
        self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    async def respond(self, session_id: str, user_input: str) -> AsyncIterator[str]:
        """Process user input and stream the assistant response."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.add_message("user", user_input)

        # Handle state transitions based on current state
        if session.state == SessionState.WELCOME:
            # Screening question — determine org type
            async for token in self._handle_screening(session, user_input):
                yield token
        elif session.state in _ASSESSMENT_STATES:
            # Active assessment — conversation with extraction
            async for token in self._handle_assessment(session, user_input):
                yield token
        elif session.state == SessionState.CONFIRMATION:
            async for token in self._handle_confirmation(session, user_input):
                yield token
        elif session.state == SessionState.DIAGNOSIS:
            async for token in self._handle_diagnosis(session):
                yield token
        elif session.state == SessionState.RECOMMENDATIONS:
            async for token in self._handle_recommendations(session):
                yield token
        elif session.state == SessionState.GENERATION:
            async for token in self._handle_generation(session):
                yield token

    async def _handle_screening(
        self, session: Session, user_input: str
    ) -> AsyncIterator[str]:
        """Use LLM to classify org type from user's natural language response."""
        classification = await self._llm.extract_json(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f'The user was asked: "Is your organization structured with clear '
                        f"departments and reporting lines, or is it more of a flat or "
                        f'matrix structure?"\n\n'
                        f'They responded: "{user_input}"\n\n'
                        f"Classify their organization type.\n"
                        f'Respond with: {{"type": "hierarchical" | "non-hierarchical" | "unclear"}}'
                    ),
                }
            ],
            system="You classify organizational structures. Respond with JSON only.",
        )

        org_type = classification.get("type", "unclear")

        if org_type == "non-hierarchical":
            session.extracted.is_hierarchical = False
            session.extracted.org_type = "non-hierarchical"
            response = SCREENING_NON_HIERARCHICAL
        elif org_type == "hierarchical":
            session.extracted.is_hierarchical = True
            session.extracted.org_type = "hierarchical"
            response = SCREENING_HIERARCHICAL
        else:
            # Unclear — let the LLM have a conversational follow-up
            messages = _session_to_messages(session)
            response_parts: list[str] = []
            async for token in self._llm.stream(messages, system=SYSTEM_PROMPT):
                response_parts.append(token)
                yield token
            response = "".join(response_parts)
            session.add_message("assistant", response)
            return

        session.advance(SessionState.ORG_STRUCTURE)
        session.add_message("assistant", response)
        for token in _chunk_text(response):
            yield token

    async def _handle_assessment(
        self, session: Session, user_input: str
    ) -> AsyncIterator[str]:
        """Handle ongoing assessment conversation."""
        messages = _session_to_messages(session)

        # Add context about current state and what to ask next
        state_guidance = _state_guidance(session.state)
        system = SYSTEM_PROMPT + f"\n\n## Current Focus\n{state_guidance}"

        # Check if we should transition to next state
        should_transition = await self._should_advance(session, user_input)

        if should_transition:
            next_state = _next_state(session.state)
            if next_state:
                # Extract data before transitioning
                await self._extract_data(session)
                session.advance(next_state)

                # If transitioning between major phases, use transition prompt
                transition_key = _transition_key(session.state)
                if transition_key and transition_key in STATE_TRANSITION_PROMPTS:
                    bridge = STATE_TRANSITION_PROMPTS[transition_key]
                    # Let LLM blend the transition with conversation context
                    messages.append(
                        {
                            "role": "system",
                            "content": f"Transition to next area. Use this as guidance but make it "
                            f"conversational: {bridge}",
                        }
                    )

        # Generate response
        response_parts: list[str] = []
        async for token in self._llm.stream(messages, system=system):
            response_parts.append(token)
            yield token

        full_response = "".join(response_parts)
        session.add_message("assistant", full_response)

    async def _should_advance(self, session: Session, user_input: str) -> bool:
        """Ask the LLM whether the current assessment area is sufficiently covered."""
        state_name = session.state.value
        recent_messages = session.messages[-6:]  # Last 3 turns
        context = "\n".join(f"{m.role}: {m.content}" for m in recent_messages)

        result = await self._llm.extract_json(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Current assessment area: {state_name}\n\n"
                        f"Recent conversation:\n{context}\n\n"
                        f"Has the user provided enough information about {state_name} "
                        f"to move to the next area? Consider:\n"
                        f"- Have the key questions been answered (even partially)?\n"
                        f"- Has the user indicated they have nothing more to add?\n"
                        f"- Has the conversation naturally moved to a different topic?\n\n"
                        f'Respond with: {{"should_advance": true/false, "reason": "..."}}'
                    ),
                }
            ],
            system="You are a conversation flow analyzer. Respond with JSON only.",
        )
        return result.get("should_advance", False)

    async def _extract_data(self, session: Session) -> None:
        """Extract structured data from the conversation so far."""
        conversation_text = "\n".join(
            f"{m.role}: {m.content}" for m in session.messages
        )

        current_data = {
            "org_name": session.extracted.org_name,
            "departments": session.extracted.departments,
            "teams": session.extracted.teams,
            "roles": session.extracted.roles,
            "financial_constraints": session.extracted.financial_constraints,
            "operational_constraints": session.extracted.operational_constraints,
            "temporal_constraints": session.extracted.temporal_constraints,
            "data_access_constraints": session.extracted.data_access_constraints,
            "communication_constraints": session.extracted.communication_constraints,
            "bridges": session.extracted.bridges,
            "current_ai_usage": session.extracted.current_ai_usage,
            "target_trust_posture": session.extracted.target_trust_posture,
            "gaps": session.extracted.gaps,
        }

        extracted = await self._llm.extract_json(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Conversation so far:\n{conversation_text}\n\n"
                        f"Currently extracted data:\n{current_data}\n\n"
                        "Update the extracted data with any new information from the "
                        "conversation. Return the full updated JSON. Keep existing data "
                        "unless the conversation explicitly corrects it."
                    ),
                }
            ],
            system=EXTRACTION_SYSTEM,
        )

        # Update session extracted data
        _merge_extracted(session.extracted, extracted)

    async def _handle_confirmation(
        self, session: Session, user_input: str
    ) -> AsyncIterator[str]:
        """Handle the confirmation phase — LLM interprets user's response."""
        intent = await self._llm.extract_json(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"The user was shown a summary of their organizational assessment "
                        f"and asked to confirm it.\n\n"
                        f'They responded: "{user_input}"\n\n'
                        f"What is their intent?\n"
                        f'Respond with: {{"intent": "confirmed" | "needs_changes" | "unclear"}}'
                    ),
                }
            ],
            system="You interpret user confirmation responses. Respond with JSON only.",
        )

        user_intent = intent.get("intent", "unclear")

        if user_intent == "confirmed":
            session.advance(SessionState.DIAGNOSIS)
            async for token in self._handle_diagnosis(session):
                yield token
        elif user_intent == "needs_changes":
            messages = _session_to_messages(session)
            system = (
                SYSTEM_PROMPT
                + "\n\nThe user is correcting something in the assessment summary. "
                "Ask what needs to change. Update your understanding. "
                "Then re-present the corrected summary for confirmation."
            )
            response_parts: list[str] = []
            async for token in self._llm.stream(messages, system=system):
                response_parts.append(token)
                yield token
            session.add_message("assistant", "".join(response_parts))
        else:
            messages = _session_to_messages(session)
            response_parts: list[str] = []
            async for token in self._llm.stream(messages, system=SYSTEM_PROMPT):
                response_parts.append(token)
                yield token
            session.add_message("assistant", "".join(response_parts))

    async def _handle_diagnosis(self, session: Session) -> AsyncIterator[str]:
        """Generate the CARE diagnosis."""
        from care.diagnosis import diagnose

        diagnosis_result = await diagnose(self._llm, session.extracted)
        session.add_message(
            "assistant", diagnosis_result.summary, diagnosis=diagnosis_result.to_dict()
        )
        session.advance(SessionState.RECOMMENDATIONS)

        for token in _chunk_text(diagnosis_result.summary):
            yield token

    async def _handle_recommendations(self, session: Session) -> AsyncIterator[str]:
        """Generate recommendations."""
        from care.diagnosis import recommend

        # Get the diagnosis from the last message metadata
        diagnosis_data = None
        for msg in reversed(session.messages):
            if "diagnosis" in msg.metadata:
                diagnosis_data = msg.metadata["diagnosis"]
                break

        recommendations = await recommend(self._llm, session.extracted, diagnosis_data)
        session.add_message(
            "assistant",
            recommendations.summary,
            recommendations=recommendations.to_dict(),
        )
        session.advance(SessionState.GENERATION)

        for token in _chunk_text(recommendations.summary):
            yield token

    async def _handle_generation(self, session: Session) -> AsyncIterator[str]:
        """Generate the PACT configuration."""
        from care.generator import generate_pact_config

        config = generate_pact_config(session.extracted)
        session.add_message("assistant", config.summary, pact_yaml=config.yaml_content)
        session.advance(SessionState.COMPLETE)

        for token in _chunk_text(config.summary):
            yield token

    async def close(self) -> None:
        await self._llm.close()


# ── State machine helpers ────────────────────────────────────

_ASSESSMENT_STATES = {
    SessionState.ORG_STRUCTURE,
    SessionState.CONSTRAINTS,
    SessionState.DATA_SENSITIVITY,
    SessionState.COMMUNICATION,
    SessionState.BRIDGES,
    SessionState.TRUST_POSTURE,
}

_STATE_ORDER = [
    SessionState.SCREENING,
    SessionState.ORG_STRUCTURE,
    SessionState.CONSTRAINTS,
    SessionState.DATA_SENSITIVITY,
    SessionState.COMMUNICATION,
    SessionState.BRIDGES,
    SessionState.TRUST_POSTURE,
    SessionState.CONFIRMATION,
    SessionState.DIAGNOSIS,
    SessionState.RECOMMENDATIONS,
    SessionState.GENERATION,
    SessionState.COMPLETE,
]


def _next_state(current: SessionState) -> SessionState | None:
    try:
        idx = _STATE_ORDER.index(current)
        if idx + 1 < len(_STATE_ORDER):
            return _STATE_ORDER[idx + 1]
    except ValueError:
        pass
    return None


def _transition_key(state: SessionState) -> str | None:
    mapping = {
        SessionState.CONSTRAINTS: "org_structure_to_constraints",
        SessionState.DATA_SENSITIVITY: "constraints_to_data",
        SessionState.COMMUNICATION: "data_to_communication",
        SessionState.BRIDGES: "communication_to_bridges",
        SessionState.TRUST_POSTURE: "bridges_to_trust",
        SessionState.CONFIRMATION: "trust_to_confirmation",
    }
    return mapping.get(state)


def _state_guidance(state: SessionState) -> str:
    guidance = {
        SessionState.ORG_STRUCTURE: (
            "You are discovering the organization's structure: departments, teams, "
            "reporting lines, key roles. Ask about the top-level structure first, "
            "then drill into each department."
        ),
        SessionState.CONSTRAINTS: (
            "You are discovering financial and operational constraints: "
            "spending limits, approval thresholds, what AI can/cannot do, "
            "which actions need human approval."
        ),
        SessionState.DATA_SENSITIVITY: (
            "You are discovering data sensitivity and access policies: "
            "what information is public/internal/confidential/secret, "
            "who can access what, data classification approach."
        ),
        SessionState.COMMUNICATION: (
            "You are discovering communication boundaries: "
            "who AI can contact, through what channels, "
            "what tone/style, what's off-limits."
        ),
        SessionState.BRIDGES: (
            "You are discovering cross-team coordination: "
            "which teams regularly collaborate, current cross-functional projects, "
            "how different groups coordinate on shared objectives."
        ),
        SessionState.TRUST_POSTURE: (
            "You are discovering AI autonomy preferences: "
            "current AI usage, comfort level with AI independence, "
            "where they want more/less AI autonomy."
        ),
    }
    return guidance.get(state, "")


def _session_to_messages(session: Session) -> list[dict[str, str]]:
    """Convert session messages to LLM message format."""
    return [
        {"role": m.role, "content": m.content}
        for m in session.messages
        if m.role in ("user", "assistant")
    ]


def _chunk_text(text: str, chunk_size: int = 4) -> list[str]:
    """Split text into word-sized chunks for simulated streaming."""
    words = text.split()
    chunks: list[str] = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i : i + chunk_size])
        if i > 0:
            chunk = " " + chunk
        chunks.append(chunk)
    return chunks


def _merge_extracted(target: ExtractedData, source: dict[str, Any]) -> None:
    """Merge LLM-extracted data into the session's extracted data.

    Uses explicit None checks so that empty lists and empty strings are valid updates.
    """
    _FIELDS = [
        ("org_name", "org_name"),
        ("org_type", "org_type"),
        ("departments", "departments"),
        ("teams", "teams"),
        ("roles", "roles"),
        ("financial_constraints", "financial_constraints"),
        ("operational_constraints", "operational_constraints"),
        ("temporal_constraints", "temporal_constraints"),
        ("data_access_constraints", "data_access_constraints"),
        ("communication_constraints", "communication_constraints"),
        ("bridges", "bridges"),
        ("current_ai_usage", "current_ai_usage"),
        ("target_trust_posture", "target_trust_posture"),
        ("gaps", "gaps"),
    ]
    for source_key, attr_name in _FIELDS:
        value = source.get(source_key)
        if value is not None:
            setattr(target, attr_name, value)
