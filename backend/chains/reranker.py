"""
medibot — cross-encoder reranker (Phase 3).

Takes the fused candidates from hybrid_rag.retrieve and reorders them
with a cross-encoder, keeping only the RERANK_TOP_N most relevant chunks
for the LLM context window.

TODO (Phase 3):
  * load a cross-encoder (sentence-transformers CrossEncoder or fastembed
    TextCrossEncoder with RERANK_MODEL)
  * score (query, chunk.text) pairs, sort desc, slice to RERANK_TOP_N
  * make it a no-op passthrough if the model fails to load (log + warn)
"""

from __future__ import annotations

from backend.config import RERANK_MODEL, RERANK_TOP_N
from backend.chains.hybrid_rag import RetrievedChunk


class Reranker:
    def __init__(self, model_name: str | None = None, top_n: int = RERANK_TOP_N) -> None:
        self.model_name = model_name or RERANK_MODEL
        self.top_n = top_n
        # TODO: self._model = CrossEncoder(self.model_name)

    def rerank(self, query: str, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        raise NotImplementedError("Phase 3: cross-encoder reranking")


_reranker: Reranker | None = None


def get_reranker() -> Reranker:
    global _reranker
    if _reranker is None:
        _reranker = Reranker()
    return _reranker
