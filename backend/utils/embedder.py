# backend/utils/embedder.py
# Load all ML models once — reused across ingest.py and hybrid_rag.py

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import FastEmbedSparse
from sentence_transformers import CrossEncoder
from backend.config import EMBEDDING_MODEL

# ── Dense embeddings (sentence-transformers) ──────────────────────────────────
dense_embeddings = HuggingFaceEmbeddings(
    model_name = EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"}, 
    encode_kwargs={"normalize_embeddings": True}
)

# ── Sparse embeddings (BM25) ──────────────────────────────────────────────────
sparse_embeddings = FastEmbedSparse(
    model_name="Qdrant/bm25", batch_size=32
)

# ── Reranker (cross-encoder) ──────────────────────────────────────────────────
rerank_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")