"""
medibot — FastAPI application entry point (Phase 4 wiring).

Run:
    uvicorn backend.main:app --reload --port 8000
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import __version__
from backend.config import settings
from backend.routers import auth, chat, collections, health
from backend.utils.rbac import RBACError

logging.basicConfig(level=settings.log_level)

app = FastAPI(
    title="medibot",
    version=__version__,
    description="RBAC-scoped hybrid RAG assistant over hospital knowledge bases.",
)

# Learning project — permissive locally; tighten for any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RBACError)
async def _rbac_handler(_request, exc: RBACError):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=403, content={"success": False, "message": str(exc)})


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(collections.router)


@app.get("/")
async def root() -> dict:
    return {"success": True, "data": {"name": "medibot", "version": __version__}}
