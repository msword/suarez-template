from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any

from google.cloud import storage

LOGGER = logging.getLogger("vertical_builder")


def validate_manifest(manifest: dict[str, Any], payload: dict[str, Any]) -> None:
    required = (
        "exportId",
        "orgId",
        "verticalKey",
        "templateKey",
        "env",
        "generatedAt",
        "sourceUpdatedAt",
        "contentHash",
        "assetHash",
        "files",
    )
    missing = [field for field in required if field not in manifest]
    if missing:
        raise RuntimeError(f"manifest.json missing fields: {', '.join(missing)}")
    files = manifest.get("files", {})
    if not isinstance(files, dict):
        raise RuntimeError("manifest.json field files must be an object")
    for key in ("markdownCount", "assetCount"):
        if key not in files:
            raise RuntimeError(f"manifest.json missing files.{key}")

    for field in ("orgId", "verticalKey", "templateKey", "exportId"):
        if manifest[field] != payload[field]:
            raise RuntimeError(
                f"manifest.json mismatch for {field}: "
                f"manifest={manifest[field]} payload={payload[field]}"
            )
    build_target = payload.get("buildTarget")
    site = build_target.get("site") if isinstance(build_target, dict) else ""
    allow_env_override = bool(build_target.get("allowEnvOverride", False)) if isinstance(build_target, dict) else False
    if manifest["env"] != payload["env"] and not (site == "local" and allow_env_override):
        raise RuntimeError(
            f"manifest.json mismatch for env: "
            f"manifest={manifest['env']} payload={payload['env']}"
        )


def _parse_gs_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("gs://"):
        raise ValueError("snapshotUri must be gs://bucket/path")
    bucket_and_path = uri.removeprefix("gs://")
    parts = bucket_and_path.split("/", 1)
    if len(parts) != 2:
        raise ValueError("snapshotUri must include object prefix path")
    return parts[0], parts[1].rstrip("/")


def download_snapshot(
    storage_client: storage.Client,
    snapshot_uri: str,
    destination: Path,
) -> None:
    bucket_name, prefix = _parse_gs_uri(snapshot_uri)
    bucket = storage_client.bucket(bucket_name)
    blobs = list(storage_client.list_blobs(bucket, prefix=prefix + "/"))
    LOGGER.info(
        "Downloading snapshot from bucket=%s prefix=%s blobCount=%d",
        bucket_name,
        prefix,
        len(blobs),
    )
    if not blobs:
        raise RuntimeError(
            "No snapshot files found at "
            f"{snapshot_uri}. Verify export bucket/env/path and exportId."
        )
    sample = [blob.name for blob in blobs[:10]]
    LOGGER.info("Snapshot blob sample: %s", sample)
    for blob in blobs:
        rel = Path(blob.name).relative_to(prefix)
        target = destination / rel
        if blob.name.endswith("/"):
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(str(target))


def validate_snapshot_layout(snapshot_root: Path) -> None:
    required_dirs = ("content", "data", "static")
    missing = [name for name in required_dirs if not (snapshot_root / name).exists()]
    if missing:
        raise RuntimeError(
            "Snapshot missing required directories: "
            + ", ".join(missing)
            + ". Expected content/, data/, static/."
        )

    empty = []
    for name in required_dirs:
        file_count = sum(1 for p in (snapshot_root / name).rglob("*") if p.is_file())
        LOGGER.info("Snapshot %s fileCount=%d", name, file_count)
        if file_count == 0:
            empty.append(name)
    if empty:
        raise RuntimeError(
            "Snapshot directories are empty: "
            + ", ".join(empty)
            + ". Export appears incomplete."
        )


def load_manifest(snapshot_root: Path) -> dict[str, Any]:
    manifest_path = snapshot_root / "manifest.json"
    if not manifest_path.exists():
        raise RuntimeError("manifest.json not found in snapshot")
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, dict):
        raise RuntimeError("manifest.json must be an object")
    return manifest


def assemble_workspace(
    *,
    payload: dict[str, Any],
    snapshot_root: Path,
    workspace: Path,
    themes_root: Path,
    base_config_path: Path,
) -> None:
    workspace.mkdir(parents=True, exist_ok=True)

    for top in ("content", "data", "static"):
        src = snapshot_root / top
        dst = workspace / top
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.mkdir(parents=True, exist_ok=True)

    if payload["templateKey"] != "gymnastics":
        raise RuntimeError(
            f"Unsupported templateKey={payload['templateKey']}. Expected gymnastics."
        )

    theme_src = themes_root / "gymnastics"
    theme_dst = workspace / "themes" / "gymnastics"
    shutil.copytree(theme_src, theme_dst, dirs_exist_ok=True)
    shutil.copy2(base_config_path, workspace / "config.yaml")
