import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dlp_scanner import main, scan_file

def test_detects_sensitive_values(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text(
        "Email: demo.user@example.com\n"
        "API key: sk-demo-1234567890abcdef\n"
        "Password: DemoPass123!\n",
        encoding="utf-8",
    )

    findings = scan_file(sample)

    # The scanner records findings without storing matched values.
    assert len(findings) == 3
    assert {item["finding_type"] for item in findings} == {
        "email_address",
        "api_key_label",
        "password_label",
    }
    assert all(item["value_redacted"] is True for item in findings)


def test_report_does_not_expose_sensitive_values(tmp_path, monkeypatch):
    import dlp_scanner

    scan_dir = tmp_path / "dlp_samples"
    scan_dir.mkdir()

    sample = scan_dir / "sample.txt"
    sample.write_text(
        "Email: demo.user@example.com\n"
        "API key: sk-demo-1234567890abcdef\n"
        "Password: DemoPass123!\n",
        encoding="utf-8",
    )

    report_file = tmp_path / "reports" / "dlp_report.json"

    monkeypatch.setattr(dlp_scanner, "SCAN_DIR", scan_dir)
    monkeypatch.setattr(dlp_scanner, "REPORT_FILE", report_file)

    main()

    report_text = report_file.read_text(encoding="utf-8")
    report = json.loads(report_text)

    assert report["finding_count"] == 3
    assert "demo.user@example.com" not in report_text
    assert "sk-demo-1234567890abcdef" not in report_text
    assert "DemoPass123!" not in report_text
