# backend/routers/collections.py
from fastapi import APIRouter
from backend.config import ROLE_ACCESS
from fastapi import HTTPException

router = APIRouter()

@router.get("/collections/{role}")
def get_collections(role: str):
	if role in ROLE_ACCESS:
		collection = ROLE_ACCESS[role]
		return {"role": role, "collections": collection}
	else:
		raise HTTPException(status_code=404, detail="Role not found")
