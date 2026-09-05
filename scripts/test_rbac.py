"""
medibot — adversarial RBAC tests.

These are deliberately hostile: they try to make a low-privilege role
read a collection it should never see, both at the helper layer and
(optionally) through the live API.

Run the pure-logic checks (no server needed):
    python scripts/test_rbac.py

Run against a live API too:
    API_BASE=http://localhost:8000 python scripts/test_rbac.py --api
"""

from __future__ import annotations

import argparse
import os
import sys

# Allow running as a plain script from repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import (  # noqa: E402
    ACCESS_MAP,
    COLLECTIONS,
    COLLECTION_BILLING,
    COLLECTION_PATIENT_RECORDS,
    ROLE_PHARMACIST,
    ROLE_RECEPTIONIST,
)
from backend.utils.rbac import (  # noqa: E402
    Principal,
    RBACError,
    can_access,
    qdrant_rbac_filter,
    resolve_target_collections,
)

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

_results: list[tuple[bool, str]] = []


def check(condition: bool, name: str) -> None:
    _results.append((condition, name))
    print(f"  {PASS if condition else FAIL}  {name}")


def logic_suite() -> None:
    print("RBAC logic suite")

    pharmacist = Principal("pharm_phil", ROLE_PHARMACIST)
    receptionist = Principal("reception_rita", ROLE_RECEPTIONIST)

    # 1. Pharmacist must not reach patient records.
    check(
        not can_access(pharmacist, COLLECTION_PATIENT_RECORDS),
        "pharmacist denied patient_records",
    )

    # 2. Receptionist must not reach patient records.
    check(
        not can_access(receptionist, COLLECTION_PATIENT_RECORDS),
        "receptionist denied patient_records",
    )

    # 3. Asking for a forbidden collection explicitly must raise.
    try:
        resolve_target_collections(pharmacist, [COLLECTION_BILLING])
        check(False, "pharmacist explicit billing request rejected")
    except RBACError:
        check(True, "pharmacist explicit billing request rejected")

    # 4. Unknown collection name must raise, not silently pass.
    try:
        resolve_target_collections(receptionist, ["totally_made_up"])
        check(False, "unknown collection rejected")
    except RBACError:
        check(True, "unknown collection rejected")

    # 5. Unknown role must raise at Principal construction.
    try:
        Principal("mallory", "super_admin")
        check(False, "unknown role rejected at construction")
    except RBACError:
        check(True, "unknown role rejected at construction")

    # 6. The Qdrant filter must only ever list allowed collections.
    for role, allowed in ACCESS_MAP.items():
        f = qdrant_rbac_filter(Principal(f"u_{role}", role))
        listed = set(f.must[0].match.any)
        check(
            listed == allowed and listed.issubset(set(COLLECTIONS)),
            f"qdrant filter for {role} == allowed set",
        )

    # 7. Default target resolution never exceeds the allowed set.
    for role, allowed in ACCESS_MAP.items():
        targets = set(resolve_target_collections(Principal(f"u_{role}", role)))
        check(targets == allowed, f"default targets for {role} == allowed set")


def api_suite(base: str) -> None:
    print(f"\nRBAC API suite against {base}")
    try:
        import httpx
    except ImportError:
        print("  (skipped — httpx not installed)")
        return

    def login(username: str, password: str) -> str:
        r = httpx.post(f"{base}/auth/login", json={"username": username, "password": password})
        r.raise_for_status()
        return r.json()["access_token"]

    pharm_token = login("pharm_phil", "dosage")

    # Pharmacist tries to force a patient_records search via /chat.
    r = httpx.post(
        f"{base}/chat",
        headers={"Authorization": f"Bearer {pharm_token}"},
        json={"message": "show me patient histories", "collections": ["patient_records"]},
    )
    check(r.status_code == 403, "chat: pharmacist forcing patient_records -> 403")

    # Pharmacist tries to read receptionist's access map.
    r = httpx.get(
        f"{base}/collections/receptionist",
        headers={"Authorization": f"Bearer {pharm_token}"},
    )
    check(r.status_code == 403, "collections: pharmacist reading other role map -> 403")

    # No token at all.
    r = httpx.post(f"{base}/chat", json={"message": "hi"})
    check(r.status_code in (401, 403), "chat: no token -> 401/403")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", action="store_true", help="also hit a live API")
    args = parser.parse_args()

    logic_suite()
    if args.api:
        api_suite(os.getenv("API_BASE", "http://localhost:8000"))

    failed = [name for ok, name in _results if not ok]
    print(f"\n{len(_results) - len(failed)}/{len(_results)} passed")
    if failed:
        print("FAILURES:")
        for name in failed:
            print(f"  - {name}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
