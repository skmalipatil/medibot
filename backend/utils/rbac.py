"""
medibot — RBAC filters & helpers.

All access-control logic lives here and is derived from
`config.ACCESS_MAP`. Routers and chains must call these helpers
instead of re-implementing role checks.

Two layers of defence:
  1. Collection-level  — a role may only query collections in its access set.
  2. Payload-level     — even inside an allowed collection, a Qdrant filter
                         pins results to that role's allowed collections
                         (defence in depth if collections are ever merged).
"""

from __future__ import annotations

from dataclasses import dataclass

from qdrant_client import models as qmodels

from backend.config import (
    ACCESS_MAP,
    COLLECTIONS,
    collections_for_role,
    is_valid_collection,
    is_valid_role,
)


class RBACError(Exception):
    """Raised on any access-control violation. Map to HTTP 403 at the edge."""


@dataclass(frozen=True)
class Principal:
    """The authenticated caller. Never trust a raw dict from a request body."""

    username: str
    role: str

    def __post_init__(self) -> None:
        if not is_valid_role(self.role):
            raise RBACError(f"Unknown role: {self.role!r}")


# ─────────────────────────────────────────────────────────────
# Collection-level checks
# ─────────────────────────────────────────────────────────────
def allowed_collections(principal: Principal) -> set[str]:
    return collections_for_role(principal.role)


def can_access(principal: Principal, collection: str) -> bool:
    if not is_valid_collection(collection):
        return False
    return collection in ACCESS_MAP.get(principal.role, set())


def assert_can_access(principal: Principal, collection: str) -> None:
    """Raise RBACError unless the principal may read `collection`."""
    if not is_valid_collection(collection):
        raise RBACError(f"Unknown collection: {collection!r}")
    if not can_access(principal, collection):
        raise RBACError(
            f"Role {principal.role!r} is not permitted to access "
            f"collection {collection!r}"
        )


def resolve_target_collections(
    principal: Principal, requested: list[str] | None = None
) -> list[str]:
    """
    Work out which collections a query should actually hit.

    * requested is None  -> every collection the role can see
    * requested provided -> intersection with the role's allowed set,
                            raising if the caller asked for something off-limits
    """
    permitted = allowed_collections(principal)
    if not permitted:
        raise RBACError(f"Role {principal.role!r} has no collection access")

    if requested is None:
        return sorted(permitted)

    requested_set = set(requested)
    unknown = requested_set - set(COLLECTIONS)
    if unknown:
        raise RBACError(f"Unknown collection(s): {sorted(unknown)}")

    forbidden = requested_set - permitted
    if forbidden:
        raise RBACError(
            f"Role {principal.role!r} may not access: {sorted(forbidden)}"
        )
    return sorted(requested_set)


# ─────────────────────────────────────────────────────────────
# Payload-level filter (defence in depth)
# ─────────────────────────────────────────────────────────────
def qdrant_rbac_filter(
    principal: Principal, extra: qmodels.Filter | None = None
) -> qmodels.Filter:
    """
    Build a Qdrant `Filter` that only matches points whose payload
    `collection` field is in the principal's allowed set.

    Ingestion (`ingest.py`) must stamp every point payload with a
    `collection` key for this to bite.
    """
    permitted = sorted(allowed_collections(principal))
    if not permitted:
        raise RBACError(f"Role {principal.role!r} has no collection access")

    must: list[qmodels.Condition] = [
        qmodels.FieldCondition(
            key="collection",
            match=qmodels.MatchAny(any=permitted),
        )
    ]
    if extra is not None and extra.must:
        must.extend(extra.must)

    return qmodels.Filter(
        must=must,
        should=extra.should if extra else None,
        must_not=extra.must_not if extra else None,
    )


# ─────────────────────────────────────────────────────────────
# Introspection helper (backs /collections/{role})
# ─────────────────────────────────────────────────────────────
def describe_access(role: str) -> dict[str, object]:
    if not is_valid_role(role):
        raise RBACError(f"Unknown role: {role!r}")
    allowed = sorted(ACCESS_MAP.get(role, set()))
    return {
        "role": role,
        "allowed_collections": allowed,
        "denied_collections": sorted(set(COLLECTIONS) - set(allowed)),
    }
