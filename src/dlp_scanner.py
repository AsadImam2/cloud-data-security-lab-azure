
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCAN_DIR = PROJECT_ROOT / "data" / "dlp_samples"
REPORT_FILE = PROJECT_ROOT / "reports" / "dlp_report.json"

# Demonstration patterns only; these are not universal secret detectors.
PATTERNS = {
    "email_address": re.compile(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        re.IGNORECASE,
    ),
    "api_key_label": re.compile(
        r"\bAPI\s*key\s*:\s*\S+",
        re.IGNORECASE,
    ),
    "password_label": re.compile(
        r"\bpassword\s*:\s*\S+",
        re.IGNORECASE,
    ),
}


def scan_file(file_path):
    findings = []

    with file_path.open("r", encoding="utf-8", errors="replace") as file:
        for line_number, line in enumerate(file, start=1):
            for finding_type, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append({
                        "file": (
    str(file_path.relative_to(PROJECT_ROOT))
    if file_path.is_relative_to(PROJECT_ROOT)
    else file_path.name
),
                        "line": line_number,
                        "finding_type": finding_type,
                        "value_redacted": True,
                    })

    return findings


def main():
    if not SCAN_DIR.is_dir():
        raise FileNotFoundError(f"Scan directory not found: {SCAN_DIR}")

    findings = []

    for file_path in SCAN_DIR.rglob("*"):
        if file_path.is_file():
            findings.extend(scan_file(file_path))

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scan_directory": (
    str(SCAN_DIR.relative_to(PROJECT_ROOT))
    if SCAN_DIR.is_relative_to(PROJECT_ROOT)
    else SCAN_DIR.name
),
        "files_scanned": sum(
            1 for path in SCAN_DIR.rglob("*") if path.is_file()
        ),
        "finding_count": len(findings),
        "findings": findings,
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("=== DLP Scan Report ===")
    print(f"Files scanned: {report['files_scanned']}")
    print(f"Findings: {report['finding_count']}")

    for finding in findings:
        print(
            f"{finding['finding_type']} | "
            f"{finding['file']} | line {finding['line']} | "
            "value redacted"
        )

    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
