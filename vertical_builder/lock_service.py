from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from google.cloud import firestore


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _lock_doc_ref(db: firestore.Client, org_id: str, vertical_key: str):
    return (
        db.collection("orgs")
        .document(org_id)
        .collection("verticalBuildLocks")
        .document(vertical_key)
    )


def acquire_lock(
    db: firestore.Client,
    payload: dict[str, Any],
    ttl_seconds: int,
) -> None:
    doc_ref = _lock_doc_ref(db, payload["orgId"], payload["verticalKey"])
    now = _utc_now()
    expires_at = now + timedelta(seconds=ttl_seconds)

    @firestore.transactional
    def _create_lock(transaction: firestore.Transaction) -> None:
        snapshot = doc_ref.get(transaction=transaction)
        if snapshot.exists:
            data = snapshot.to_dict() or {}
            lock_expiry = data.get("expiresAt")
            if lock_expiry is None or lock_expiry > now:
                raise RuntimeError(
                    "Concurrent publish blocked by active lock "
                    f"for org={payload['orgId']} vertical={payload['verticalKey']}"
                )
        transaction.set(
            doc_ref,
            {
                "jobId": payload["jobId"],
                "exportId": payload["exportId"],
                "templateKey": payload["templateKey"],
                "env": payload["env"],
                "acquiredAt": now,
                "expiresAt": expires_at,
            },
        )

    _create_lock(db.transaction())


def release_lock(db: firestore.Client, payload: dict[str, Any]) -> None:
    doc_ref = _lock_doc_ref(db, payload["orgId"], payload["verticalKey"])
    doc_ref.delete()
