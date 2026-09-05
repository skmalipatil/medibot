"""
medibot — /collections/{role} router.

Introspection endpoint: given a role, report which Qdrant collections it
may and may not access. Handy for the frontend and for the adversarial
RBAC tests in scripts/test_rbac.py.

Only an admin (or the role's own holder) may query another role's map.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.config import ROLE_ADMIN, is_valid_role
from backend.routers.auth import get_current_principal
from backend.utils.rbac import Principal, RBACError, describe_access

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("/{role}")
async def collections_for_role(
    role: str,
    principal: Principal = Depends(get_current_principal),
) -> dict:
    if not is_valid_role(role):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown role: {role}"
        )
    if principal.role != ROLE_ADMIN and principal.role != role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You may only view your own role's access map",
        )
    try:
        return {"success": True, "data": describe_access(role)}
    except RBACError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
