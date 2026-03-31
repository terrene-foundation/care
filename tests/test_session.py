"""Tests for session state management."""

from care.conversation.session import (
    ExtractedData,
    Session,
    SessionState,
    PHASE_MAP,
    STATE_PROGRESS,
)


def test_session_creation():
    session = Session()
    assert session.state == SessionState.WELCOME
    assert session.progress == 0
    assert session.phase == "Assess"
    assert len(session.messages) == 0


def test_session_advance():
    session = Session()
    session.advance(SessionState.ORG_STRUCTURE)
    assert session.state == SessionState.ORG_STRUCTURE
    assert session.progress == 15


def test_session_add_message():
    session = Session()
    msg = session.add_message("user", "Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert len(session.messages) == 1


def test_session_to_dict():
    session = Session()
    session.add_message("assistant", "Welcome!")
    session.extracted.org_name = "Acme Corp"
    d = session.to_dict()
    assert d["state"] == "welcome"
    assert d["phase"] == "Assess"
    assert d["message_count"] == 1
    assert d["extracted"]["org_name"] == "Acme Corp"


def test_all_states_have_phase():
    for state in SessionState:
        assert state in PHASE_MAP, f"{state} missing from PHASE_MAP"


def test_all_states_have_progress():
    for state in SessionState:
        assert state in STATE_PROGRESS, f"{state} missing from STATE_PROGRESS"


def test_extracted_data_defaults():
    extracted = ExtractedData()
    assert extracted.org_name is None
    assert extracted.departments == []
    assert extracted.gaps == []
