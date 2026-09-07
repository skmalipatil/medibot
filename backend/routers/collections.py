# backend/routers/collections.py
from fastapi import APIRouter, Depends
from backend.config import ROLE_ACCESS
from fastapi import HTTPException
from backend.utils.auth import get_current_user

router = APIRouter()

@router.get("/collections/{role}")
def get_collections(role: str, current_user: dict = Depends(get_current_user)):
    # only allow user to see their own collections
    # unless they are admin
    if current_user["role"] != "admin" and current_user["role"] != role:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if role not in ROLE_ACCESS:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return {
        "role": role,
        "collections": ROLE_ACCESS[role]
    }