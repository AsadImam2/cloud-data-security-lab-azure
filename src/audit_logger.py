
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIT_LOG = PROJECT_ROOT / "reports" / "audit_log.jsonl"

# Only allow known, non-secret metadata fields.
ALLOWED_FIELDS = {
    "record_id",
    "key_id",
    "reason_code",
    "finding_count",
}


def log_event(
    event_type,
    status,
    resource,
    metadata=None,
):
    if metadata is None:
        metadata = {}

    if not isinstance(metadata, dict):
        raise TypeError("metadata must be a dictionary")

    # Reject unexpected fields to reduce accidental secret logging.
    unexpected = set(metadata) - ALLOWED_FIELDS
    if unexpected:
        raise ValueError(
            f"Unsupported metadata fields: {sorted(unexpected)}"
        )

    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "status": status,
        "resource": resource,
        "metadata": metadata,
    }

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

    # JSON Lines: one independent JSON event per line.
    with AUDIT_LOG.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")


if __name__ == "__main__":
    log_event(
        event_type="audit_logger_test",
        status="success",
        resource="cloud-data-security-lab",
        metadata={"reason_code": "LOGGER_INITIALIZED"},
    )

    print(f"Audit event written to: {AUDIT_LOG}")
