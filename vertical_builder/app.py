from __future__ import annotations

import base64
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from flask import Flask, Response, request

# Allow direct script execution: `python vertical_builder/app.py`.
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vertical_builder.builder_service import handle_build_job
from vertical_builder.config import REQUIRED_PAYLOAD_FIELDS, load_runtime_config


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("vertical_builder")

app = Flask(__name__)
RUNTIME = load_runtime_config()
EXECUTOR = ThreadPoolExecutor(max_workers=1)


def _decode_pubsub_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    if "message" not in envelope or "data" not in envelope["message"]:
        raise ValueError("Missing Pub/Sub message.data")
    encoded_data = envelope["message"]["data"]
    decoded = base64.b64decode(encoded_data).decode("utf-8")
    payload = json.loads(decoded)
    if not isinstance(payload, dict):
        raise ValueError("Payload must decode to an object")
    return payload


def _validate_payload(payload: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_PAYLOAD_FIELDS if field not in payload]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    build_target = payload.get("buildTarget")
    if not isinstance(build_target, dict):
        raise ValueError("buildTarget must be an object")
    hosting_project = build_target.get("hostingProject")
    site = build_target.get("site")
    allow_env_override = bool(build_target.get("allowEnvOverride", False))
    if payload["env"] != RUNTIME.env and not (site == "local" and allow_env_override):
        raise ValueError(
            f"Environment mismatch: payload env={payload['env']} runtime env={RUNTIME.env}"
        )
    if not hosting_project:
        raise ValueError("buildTarget must include hostingProject")
    if not site:
        raise ValueError("buildTarget must include site")
    if site != "local" and hosting_project != RUNTIME.firebase_project:
        raise ValueError(
            "buildTarget.hostingProject must match runtime FIREBASE_PROJECT "
            "for non-local deploys"
        )


@app.post("/modules/vertical-builder")
def vertical_builder_handler() -> tuple[Response, int]:
    try:
        if not request.is_json:
            raise ValueError("Content-Type must be application/json")
        envelope = request.get_json(force=True, silent=False)
        if not isinstance(envelope, dict):
            raise ValueError("Request body must be a JSON object")
        payload = _decode_pubsub_envelope(envelope)
        _validate_payload(payload)
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.error("Invalid Pub/Sub request: %s", exc)
        response = {"status": "invalid", "error": str(exc)}
        return Response(json.dumps(response), mimetype="application/json"), 400

    EXECUTOR.submit(handle_build_job, payload, RUNTIME)
    response = {"status": "accepted", "jobId": payload["jobId"]}
    return Response(json.dumps(response), mimetype="application/json"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
