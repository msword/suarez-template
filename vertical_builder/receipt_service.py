from __future__ import annotations

from datetime import datetime
from typing import Any

from google.cloud import firestore


def _receipt_doc_ref(db: firestore.Client, org_id: str, job_id: str):
    return (
        db.collection("orgs")
        .document(org_id)
        .collection("verticalBuildReceipts")
        .document(job_id)
    )


def write_receipt(
    db: firestore.Client,
    payload: dict[str, Any],
    status: str,
    started_at: datetime,
    finished_at: datetime,
    deployed_at: datetime | None,
    error: str | None,
) -> None:
    duration_ms = int((finished_at - started_at).total_seconds() * 1000)
    doc_ref = _receipt_doc_ref(db, payload["orgId"], payload["jobId"])
    doc_ref.set(
        {
            "jobId": payload["jobId"],
            "exportId": payload["exportId"],
            "verticalKey": payload["verticalKey"],
            "templateKey": payload["templateKey"],
            "status": status,
            "startedAt": started_at,
            "finishedAt": finished_at,
            "deployedAt": deployed_at,
            "error": error,
            "durationMs": duration_ms,
            "result": status,
        }
    )


def write_receipt_status(
    db: firestore.Client,
    payload: dict[str, Any],
    status: str,
    started_at: datetime,
    error: str | None = None,
) -> None:
    doc_ref = _receipt_doc_ref(db, payload["orgId"], payload["jobId"])
    doc_ref.set(
        {
            "jobId": payload["jobId"],
            "exportId": payload["exportId"],
            "verticalKey": payload["verticalKey"],
            "templateKey": payload["templateKey"],
            "status": status,
            "startedAt": started_at,
            "error": error,
        },
        merge=True,
    )
