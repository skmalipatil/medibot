"""medibot — /health router."""

from __future__ import annotations

from fastapi import APIRouter

from backend import __version__
from backend.config import settings
from backend.utils.qdrant_helper import get_client

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    qdrant_ok = False
    try:
        get_client().get_collections()
        qdrant_ok = True
    except Exception:  # noqa: BLE001
        qdrant_ok = False

    return {
        "success": True,
        "data": {
            "status": "ok",
            "version": __version__,
            "env": settings.app_env,
            "qdrant": "up" if qdrant_ok else "down",
        },
    }
