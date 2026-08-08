"""Thin HTTP bridge for the future Next.js MVP (ADR-006 section 2b).

Exposes just enough of the existing core to prove the stack end-to-end:
POST /api/classify runs core.intent_router + core.llm_router (a routing
*decision*, not a real LLM call — that still needs ANTHROPIC_API_KEY and is
out of scope for this endpoint).
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from core.intent_router import classify_intent
from core.llm_router import route_task

app = FastAPI(title="Jarvis OS API", version="0.1.0")


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    task_type: str
    domain: Optional[str]
    urgency: str
    stakeholder: Optional[str]
    autonomous: bool
    primary_model: str
    fallback_chain: list[str]


@app.post("/api/classify", response_model=ClassifyResponse)
def classify(request: ClassifyRequest) -> ClassifyResponse:
    intent = classify_intent(request.text)
    routing = route_task(intent.task_type)
    return ClassifyResponse(
        task_type=intent.task_type,
        domain=intent.domain,
        urgency=intent.urgency,
        stakeholder=intent.stakeholder,
        autonomous=intent.autonomous,
        primary_model=routing.primary_model,
        fallback_chain=routing.fallback_chain,
    )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
