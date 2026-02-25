from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REQUIRED_PAYLOAD_FIELDS = (
    "jobId",
    "env",
    "orgId",
    "verticalKey",
    "templateKey",
    "exportId",
    "buildTarget",
)


@dataclass(frozen=True)
class RuntimeConfig:
    env: str
    firebase_project: str
    export_bucket: str
    themes_root: Path
    base_config_path: Path
    lock_ttl_seconds: int


def load_runtime_config() -> RuntimeConfig:
    module_root = Path(__file__).resolve().parent
    env = os.environ.get("ENV")
    if not env:
        raise RuntimeError("Missing required environment variable ENV")
    firebase_project = os.environ.get("FIREBASE_PROJECT")
    if not firebase_project:
        raise RuntimeError("Missing required environment variable FIREBASE_PROJECT")
    return RuntimeConfig(
        env=env,
        firebase_project=firebase_project,
        export_bucket=os.environ.get("EXPORT_BUCKET", f"buzzpoint-sites-{env}"),
        themes_root=Path(
            os.environ.get("VERTICAL_THEMES_ROOT", str(module_root / "themes"))
        ),
        base_config_path=Path(
            os.environ.get(
                "VERTICAL_BASE_CONFIG",
                str(module_root / "config" / "base-config.yaml"),
            )
        ),
        lock_ttl_seconds=int(os.environ.get("VERTICAL_LOCK_TTL_SECONDS", "900")),
    )
