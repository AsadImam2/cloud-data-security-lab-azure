
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "src"),
)

import audit_logger


def test_log_event_writes_json_record(tmp_path, monkeypatch):
    log_file = tmp_path / "audit_log.jsonl"
    monkeypatch.setattr(audit_logger, "AUDIT_LOG", log_file)

    audit_logger.log_event(
        event_type="encryption_test",
        status="success",
        resource="sample.enc",
        metadata={"key_id": "demo_key_v2"},
    )

    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    event = json.loads(lines[0])
    assert event["event_type"] == "encryption_test"
    assert event["status"] == "success"
    assert event["resource"] == "sample.enc"
    assert event["metadata"]["key_id"] == "demo_key_v2"
    assert event["timestamp_utc"]


def test_log_event_appends_events(tmp_path, monkeypatch):
    log_file = tmp_path / "audit_log.jsonl"
    monkeypatch.setattr(audit_logger, "AUDIT_LOG", log_file)

    for status in ("success", "failure"):
        audit_logger.log_event(
            event_type="test_event",
            status=status,
            resource="test_resource",
        )

    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["status"] == "success"
    assert json.loads(lines[1])["status"] == "failure"


def test_log_event_rejects_unsupported_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(
        audit_logger,
        "AUDIT_LOG",
        tmp_path / "audit_log.jsonl",
    )

    with pytest.raises(ValueError):
        audit_logger.log_event(
            event_type="test_event",
            status="failure",
            resource="test_resource",
            metadata={"password": "DemoPass123!"},
        )

    assert not (tmp_path / "audit_log.jsonl").exists()
