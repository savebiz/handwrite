import os
import json
from datetime import datetime, timezone
from typing import Dict, Any
from app.shared.schemas import AuditEvent, ActorEnum


LOG_DIR = "logs"
AUDIT_FILE = os.path.join(LOG_DIR, "audit.jsonl")


def log_audit_event(actor: ActorEnum, action: str, details: Dict[str, Any]) -> AuditEvent:
    """
    Appends an immutable audit record to logs/audit.jsonl.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    event = AuditEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        actor=actor,
        action=action,
        details=details,
    )

    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(event.model_dump_json() + "\n")

    return event
