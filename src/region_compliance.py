
import json
from datetime import datetime, timezone
from pathlib import Path
from audit_logger import log_event

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_FILE = PROJECT_ROOT / "data" / "sample" / "inventory.json"
POLICY_FILE = PROJECT_ROOT / "data" / "sample" / "region_policy.json"
REPORT_FILE = PROJECT_ROOT / "reports" / "region_compliance_report.json"


def check_compliance(records, policy):
    allowed_regions = {
        region.casefold()
        for region in policy["allowed_regions"]
    }
    restricted_levels = {
        level.casefold()
        for level in policy["restricted_sensitivity_levels"]
    }

    findings = []

    for record in records:
        region = record.get("storage_region", "")
        sensitivity = record.get("sensitivity", "")

        if not isinstance(region, str) or region.casefold() not in allowed_regions:
            findings.append({
                "record_id": record.get("record_id", "UNKNOWN"),
                "finding_type": "unapproved_storage_region",
                "storage_region": region if isinstance(region, str) else "INVALID",
                "severity": "high",
            })

        if (
            isinstance(sensitivity, str)
            and sensitivity.casefold() in restricted_levels
        ):
            findings.append({
                "record_id": record.get("record_id", "UNKNOWN"),
                "finding_type": "restricted_data_requires_review",
                "sensitivity": sensitivity,
                "severity": "review",
            })

    return findings


def main():
    with INVENTORY_FILE.open("r", encoding="utf-8-sig") as file:
        records = json.load(file)

    with POLICY_FILE.open("r", encoding="utf-8-sig") as file:
        policy = json.load(file)

    findings = check_compliance(records, policy)
    region_violations = sum(
        1
        for finding in findings
        if finding["finding_type"] == "unapproved_storage_region"
    )

    log_event(
        event_type="data_residency_scan",
        status="failure" if region_violations else "success",
        resource="data/sample/inventory.json",
        metadata={"finding_count": len(findings)},
    )

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "policy_name": policy["policy_name"],
        "policy_version": policy["policy_version"],
        "records_checked": len(records),
        "finding_count": len(findings),
        "findings": findings,
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with REPORT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("=== Data Residency Compliance Report ===")
    print(f"Records checked: {len(records)}")
    print(f"Findings: {len(findings)}")

    for finding in findings:
        print(
            f"{finding['finding_type']} | "
            f"{finding['record_id']} | "
            f"severity: {finding['severity']}"
        )

    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
