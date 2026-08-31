import os
import json
import tempfile
from datetime import datetime, timezone
from typing import Dict, Any
from app.shared.schemas import AuditEvent, ActorEnum


def _get_log_dir() -> str:
    """Return a writable log directory, falling back to /tmp for serverless."""
    primary = "logs"
    try:
        os.makedirs(primary, exist_ok=True)
        test_path = os.path.join(primary, ".write_test")
        with open(test_path, "w") as f:
            f.write("ok")
        os.remove(test_path)
        return primary
    except (OSError, PermissionError):
        fallback = os.path.join(tempfile.gettempdir(), "handwrite_logs")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def log_audit_event(actor: ActorEnum, action: str, details: Dict[str, Any]) -> AuditEvent:
    """
    Appends an immutable audit record to logs/audit.jsonl.
    Falls back to /tmp in read-only serverless environments.
    """
    event = AuditEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        actor=actor,
        action=action,
        details=details,
    )

    try:
        log_dir = _get_log_dir()
        audit_file = os.path.join(log_dir, "audit.jsonl")
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")
    except (OSError, PermissionError):
        # Silently continue — audit is best-effort in serverless
        pass

    return event
