"""FastAPI server — serves the CARE assessment API."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pydantic
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from care.config import load_config
from care.conversation.engine import ConversationEngine
from care.conversation.llm import LLMProvider


engine: ConversationEngine | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global engine
    config = load_config()
    llm = LLMProvider(config.llm)
    engine = ConversationEngine(llm)
    yield
    await engine.close()


app = FastAPI(
    title="CARE Assessment Kit",
    description="AI-guided governance assessment for non-technical leaders",
    version="0.1.0",
    lifespan=lifespan,
)

config = load_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.server.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ── Models ───────────────────────────────────────────────────


class CreateSessionResponse(BaseModel):
    session_id: str
    welcome_message: str
    state: str
    progress: int


class MessageRequest(BaseModel):
    content: str = pydantic.Field(max_length=5000)


class SessionStatusResponse(BaseModel):
    session_id: str
    state: str
    phase: str
    progress: int
    message_count: int


class ConfigDownloadResponse(BaseModel):
    yaml_content: str
    org_name: str


# ── Routes ───────────────────────────────────────────────────


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "care-assessment-kit"}


@app.post("/api/sessions", response_model=CreateSessionResponse)
async def create_session() -> CreateSessionResponse:
    """Start a new assessment conversation."""
    if not engine:
        raise HTTPException(status_code=503, detail="Service not ready")

    session = engine.create_session()
    welcome = session.messages[0].content if session.messages else ""

    return CreateSessionResponse(
        session_id=session.id,
        welcome_message=welcome,
        state=session.state.value,
        progress=session.progress,
    )


@app.get("/api/sessions/{session_id}", response_model=SessionStatusResponse)
async def get_session(session_id: str) -> SessionStatusResponse:
    """Get session status and progress."""
    if not engine:
        raise HTTPException(status_code=503, detail="Service not ready")

    session = engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionStatusResponse(
        session_id=session.id,
        state=session.state.value,
        phase=session.phase,
        progress=session.progress,
        message_count=len(session.messages),
    )


@app.post("/api/sessions/{session_id}/messages")
async def send_message(session_id: str, request: MessageRequest) -> EventSourceResponse:
    """Send a message and receive a streaming response via SSE."""
    if not engine:
        raise HTTPException(status_code=503, detail="Service not ready")

    session = engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_stream() -> AsyncIterator[dict[str, str]]:
        try:
            async for token in engine.respond(session_id, request.content):
                yield {"event": "token", "data": json.dumps({"text": token})}

            # Send session state update after response completes
            updated = engine.get_session(session_id)
            if updated:
                yield {
                    "event": "state",
                    "data": json.dumps(
                        {
                            "state": updated.state.value,
                            "phase": updated.phase,
                            "progress": updated.progress,
                        }
                    ),
                }

                # If there's extracted data for visualization, send it
                if updated.extracted.departments or updated.extracted.teams:
                    yield {
                        "event": "org_update",
                        "data": json.dumps(updated.to_dict()["extracted"]),
                    }

            yield {"event": "done", "data": "{}"}
        except Exception:
            yield {
                "event": "error",
                "data": json.dumps(
                    {
                        "message": "An error occurred processing your request. Please try again."
                    }
                ),
            }

    return EventSourceResponse(event_stream())


@app.get("/api/sessions/{session_id}/config")
async def download_config(session_id: str) -> ConfigDownloadResponse:
    """Download the generated PACT configuration."""
    if not engine:
        raise HTTPException(status_code=503, detail="Service not ready")

    session = engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Find the PACT YAML in message metadata
    for msg in reversed(session.messages):
        if "pact_yaml" in msg.metadata:
            return ConfigDownloadResponse(
                yaml_content=msg.metadata["pact_yaml"],
                org_name=session.extracted.org_name or "organization",
            )

    raise HTTPException(
        status_code=400,
        detail="Assessment not yet complete — no configuration generated",
    )


@app.get("/api/sessions/{session_id}/diagnosis")
async def get_diagnosis(session_id: str) -> dict:
    """Get the diagnosis results."""
    if not engine:
        raise HTTPException(status_code=503, detail="Service not ready")

    session = engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    for msg in reversed(session.messages):
        if "diagnosis" in msg.metadata:
            return msg.metadata["diagnosis"]

    raise HTTPException(status_code=400, detail="Diagnosis not yet available")


@app.get("/api/sessions/{session_id}/recommendations")
async def get_recommendations(session_id: str) -> dict:
    """Get the recommendation results."""
    if not engine:
        raise HTTPException(status_code=503, detail="Service not ready")

    session = engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    for msg in reversed(session.messages):
        if "recommendations" in msg.metadata:
            return msg.metadata["recommendations"]

    raise HTTPException(status_code=400, detail="Recommendations not yet available")
