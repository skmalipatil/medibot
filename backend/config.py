# backend/config.py
# Central configuration — roles, access control, and app constants

import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# ── LLM (Groq free tier) ──────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = "openai/gpt-oss-20b"   # fast, free on Groq

# ── Embeddings (local, free) ──────────────────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM   = 384

# ── Qdrant ────────────────────────────────────────────────────────────────────
QDRANT_HOST       = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT       = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION = "medibot_chunks"

# ── Retrieval ─────────────────────────────────────────────────────────────────
HYBRID_TOP_K = 10   # candidates from hybrid search
RERANK_TOP_K = 5    # chunks passed to LLM after reranking

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", "data/mediassist_data/db/mediassist.db")

# ── Auth ──────────────────────────────────────────────────────────────────────
SECRET_KEY         = os.getenv("SECRET_KEY", "medibot-dev-secret-change-in-prod")
TOKEN_EXPIRE_HOURS = 8

# Demo users: username → (password, role)
DEMO_USERS: dict[str, tuple[str, str]] = {
    "dr.mehta":     ("doctor123",   "doctor"),
    "nurse.priya":  ("nurse123",    "nurse"),
    "billing.ravi": ("billing123",  "billing_executive"),
    "tech.anand":   ("tech123",     "technician"),
    "admin.sys":    ("admin123",    "admin"),
}

# ── RBAC Access Map ───────────────────────────────────────────────────────────
ROLE_ACCESS: dict[str, list[str]] = {
    "doctor":            ["clinical", "nursing", "general"],
    "nurse":             ["nursing", "general"],
    "billing_executive": ["billing", "general"],
    "technician":        ["equipment", "general"],
    "admin":             ["clinical", "nursing", "billing", "equipment", "general"],
}

# Roles that can use SQL RAG
SQL_RAG_ROLES = {"billing_executive", "admin"}

# ── Collection Access (inverse of ROLE_ACCESS) ────────────────────────────────
COLLECTION_ACCESS: dict[str, list[str]] = {
    "general":   ["doctor", "nurse", "billing_executive", "technician", "admin"],
    "clinical":  ["doctor", "admin"],
    "nursing":   ["nurse", "doctor", "admin"],
    "billing":   ["billing_executive", "admin"],
    "equipment": ["technician", "admin"],
}

# ── Data Directories ──────────────────────────────────────────────────────────
# Build absolute path so it works from anywhere
BASE_DIR = Path(__file__).parent.parent  # goes up from backend/ to medibot/
DATA_DIR = BASE_DIR / "data" / "mediassist_data"

COLLECTION_DIRS: dict[str, str] = {
    "general":   str(DATA_DIR / "general"),
    "clinical":  str(DATA_DIR / "clinical"),
    "nursing":   str(DATA_DIR / "nursing"),
    "billing":   str(DATA_DIR / "billing"),
    "equipment": str(DATA_DIR / "equipment"),
}