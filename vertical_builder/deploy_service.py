from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path


LOGGER = logging.getLogger("vertical_builder")
FIREBASE_CMD_TIMEOUT_SECONDS = int(os.environ.get("FIREBASE_CMD_TIMEOUT_SECONDS", "120"))


def _run_cmd(cmd: list[str], cwd: Path | None = None) -> None:
    LOGGER.info("Running command: %s", " ".join(cmd))
    subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=True,
        timeout=FIREBASE_CMD_TIMEOUT_SECONDS,
    )


def _ensure_hosting_site(site: str, firebase_project: str) -> None:
    cmd = [
        "firebase",
        "hosting:sites:create",
        site,
        "--project",
        firebase_project,
        "--non-interactive",
    ]
    LOGGER.info("Ensuring Firebase Hosting site exists: %s", site)
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        timeout=FIREBASE_CMD_TIMEOUT_SECONDS,
    )
    if result.returncode == 0:
        LOGGER.info("Hosting site ready: %s", site)
        return

    output = f"{result.stdout}\n{result.stderr}".lower()
    if "already exists" in output:
        return

    raise subprocess.CalledProcessError(
        result.returncode,
        cmd,
        output=result.stdout,
        stderr=result.stderr,
    )


def run_hugo_minify(workspace: Path) -> None:
    _run_cmd(["hugo", "--minify"], cwd=workspace)


def _write_firebase_config(workspace: Path, site: str) -> Path:
    config_path = workspace / "firebase.json"
    config = {
        "hosting": {
            "site": site,
            "public": "public",
            "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
        }
    }
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return config_path


def deploy_hosting(workspace: Path, site: str, firebase_project: str) -> None:
    _ensure_hosting_site(site, firebase_project)
    config_path = _write_firebase_config(workspace, site)
    _run_cmd(
        [
            "firebase",
            "deploy",
            "--only",
            "hosting",
            "--project",
            firebase_project,
            "--config",
            str(config_path),
            "--non-interactive",
        ],
        cwd=workspace,
    )
