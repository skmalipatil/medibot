"""
medibot — Qdrant helper (Phase 1).

Thin wrapper over qdrant-client so ingestion, retrieval and the
/collections router all share one client and one set of conventions:

  * every collection uses a named dense vector "dense" (EMBED_DIM, COSINE)
    and a named sparse vector "sparse"
  * every point payload carries at least: {"collection", "source", "text"}

TODO (Phase 1):
  * implement `ensure_collection`
  * implement `upsert_points`
  * implement `hybrid_search` (dense + sparse + RRF) — or defer to chains/hybrid_rag.py
"""

from __future__ import annotations

from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client import models as qmodels

from backend.config import EMBED_DIM, settings


@lru_cache
def get_client() -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
        timeout=settings.qdrant_timeout,
    )


def ensure_collection(name: str) -> None:
    """Create the collection with dense+sparse vectors if it does not exist."""
    client = get_client()
    if client.collection_exists(name):
        return
    client.create_collection(
        collection_name=name,
        vectors_config={
            "dense": qmodels.VectorParams(
                size=EMBED_DIM, distance=qmodels.Distance.COSINE
            )
        },
        sparse_vectors_config={"sparse": qmodels.SparseVectorParams()},
    )
    # Payload index so RBAC filters on `collection` stay fast.
    client.create_payload_index(
        collection_name=name,
        field_name="collection",
        field_schema=qmodels.PayloadSchemaType.KEYWORD,
    )


def upsert_points(name: str, points: list[qmodels.PointStruct]) -> None:
    raise NotImplementedError("Phase 1: batch upsert")


def list_collections() -> list[str]:
    return [c.name for c in get_client().get_collections().collections]
