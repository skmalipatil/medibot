"""
medibot — /chat router.

Accepts a question, runs it through the RBAC-scoped hybrid RAG chain
(and, later, the SQL chain for structured questions), returns an answer
plus citations.

TODO:
  * route structured questions (billing / appointments) to sql_chain
  * stream tokens (SSE) once hybrid_rag.generate is implemented
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.chains import hybrid_rag
from backend.routers.auth import get_current_principal
from backend.utils.rbac import Principal, RBACError, resolve_target_collections

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    collections: list[str] | None = Field(
        default=None,
        description="Optional subset of collections to search; must be a "
        "subset of the caller's allowed collections.",
    )


class ChatResponse(BaseModel):
    success: bool = True
    data: dict


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    principal: Principal = Depends(get_current_principal),
) -> ChatResponse:
    try:
        targets = resolve_target_collections(principal, body.collections)
    except RBACError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    try:
        result = hybrid_rag.answer(principal, body.message, targets)
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="RAG chain not implemented yet (Phase 2)",
        ) from exc

    return ChatResponse(
        data={
            "answer": result.answer,
            "used_collections": result.used_collections,
            "sources": [
                {"source": c.source, "collection": c.collection, "score": c.score}
                for c in result.sources
            ],
        }
    )
