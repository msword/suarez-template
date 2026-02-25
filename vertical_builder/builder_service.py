from __future__ import annotations

import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.cloud import firestore
from google.cloud import storage

from vertical_builder.bucket_service import (
    assemble_workspace,
    download_snapshot,
    load_manifest,
    validate_snapshot_layout,
    validate_manifest,
)
from vertical_builder.config import RuntimeConfig
from vertical_builder.deploy_service import deploy_hosting, run_hugo_minify
from vertical_builder.lock_service import acquire_lock, release_lock
from vertical_builder.receipt_service import write_receipt, write_receipt_status


LOGGER = logging.getLogger("vertical_builder")
WORKSPACE_ROOT = Path(
    os.environ.get(
        "VERTICAL_WORKSPACE_ROOT",
        str(Path(__file__).resolve().parent / "workspaces"),
    )
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_build_target(
    build_target: Any,
    runtime: RuntimeConfig,
) -> tuple[str, str]:
    if not isinstance(build_target, dict):
        raise ValueError("buildTarget must be an object")
    hosting_project = build_target.get("hostingProject")
    site = build_target.get("site")
    if not hosting_project:
        raise ValueError("buildTarget must include hostingProject")

    if not site:
        raise ValueError("buildTarget must include site")
    if hosting_project != runtime.firebase_project and site != "local":
        raise ValueError(
            "buildTarget.hostingProject must match runtime FIREBASE_PROJECT"
        )
    return hosting_project, site


def _snapshot_uri(payload: dict[str, Any], runtime: RuntimeConfig) -> str:
    return (
        f"gs://{runtime.export_bucket}/orgs/{payload['orgId']}/verticals/"
        f"{payload['verticalKey']}/exports/{payload['exportId']}"
    )


def _prepare_run_dirs(payload: dict[str, Any]) -> tuple[Path, Path, Path]:
    run_root = WORKSPACE_ROOT / payload["jobId"]
    snapshot_root = run_root / "snapshot"
    workspace = run_root / "workspace"
    shutil.rmtree(run_root, ignore_errors=True)
    snapshot_root.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(parents=True, exist_ok=True)
    return run_root, snapshot_root, workspace


def _run_build(payload: dict[str, Any], runtime: RuntimeConfig) -> bool:
    _hosting_project, site = _validate_build_target(payload["buildTarget"], runtime)
    snapshot_uri = _snapshot_uri(payload, runtime)
    run_root, snapshot_root, workspace = _prepare_run_dirs(payload)
    LOGGER.info("Workspace root: %s", run_root)

    storage_client = storage.Client()
    download_snapshot(storage_client, snapshot_uri, snapshot_root)
    validate_snapshot_layout(snapshot_root)

    manifest = load_manifest(snapshot_root)
    validate_manifest(manifest, payload)

    assemble_workspace(
        payload=payload,
        snapshot_root=snapshot_root,
        workspace=workspace,
        themes_root=runtime.themes_root,
        base_config_path=runtime.base_config_path,
    )
    content_count = sum(1 for p in (workspace / "content").rglob("*") if p.is_file())
    data_count = sum(1 for p in (workspace / "data").rglob("*") if p.is_file())
    LOGGER.info(
        "Assembled workspace contentFiles=%d dataFiles=%d path=%s",
        content_count,
        data_count,
        workspace,
    )

    run_hugo_minify(workspace)
    if site == "local":
        local_root = Path(__file__).resolve().parent / "local_output"
        local_output = local_root / payload["jobId"]
        local_output.parent.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(local_output, ignore_errors=True)
        shutil.copytree(workspace / "public", local_output)
        LOGGER.info("Local build output written to %s", local_output)
        return False

    deploy_hosting(workspace, site, runtime.firebase_project)
    return True


def handle_build_job(payload: dict[str, Any], runtime: RuntimeConfig) -> None:
    db = firestore.Client()
    started_at = _utc_now()
    deployed_at: datetime | None = None
    status = "failed"
    error: str | None = None
    lock_acquired = False

    try:
        write_receipt_status(db, payload, "queued", started_at)
        acquire_lock(db, payload, runtime.lock_ttl_seconds)
        lock_acquired = True
        write_receipt_status(db, payload, "building", started_at)
        deployed = _run_build(payload, runtime)
        if deployed:
            deployed_at = _utc_now()
        else:
            deployed_at = _utc_now()
        status = "deployed"
    except Exception as exc:  # pylint: disable=broad-except
        error = str(exc)
        LOGGER.exception("Build failed for jobId=%s", payload.get("jobId"))
    finally:
        finished_at = _utc_now()
        duration_ms = int((finished_at - started_at).total_seconds() * 1000)
        write_receipt(
            db=db,
            payload=payload,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            deployed_at=deployed_at,
            error=error,
        )
        if lock_acquired:
            release_lock(db, payload)
        LOGGER.info(
            "Build result jobId=%s exportId=%s templateKey=%s durationMs=%d result=%s",
            payload.get("jobId"),
            payload.get("exportId"),
            payload.get("templateKey"),
            duration_ms,
            status,
        )
