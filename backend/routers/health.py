from fastapi import APIRouter
from qdrant_client import QdrantClient
import sqlite3
from backend.config import DB_PATH, QDRANT_HOST, QDRANT_PORT

router = APIRouter()

@router.get("/health")
def health():
    # check Qdrant
    try:
        client = QdrantClient(url=f"http://{QDRANT_HOST}:{QDRANT_PORT}")
        client.get_collections()
        qdrant_status = "connected"
    except:
        qdrant_status = "disconnected"

    # check database
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except:
        db_status = "disconnected"

    return {
        "status": "ok",
        "qdrant": qdrant_status,
        "database": db_status
    }