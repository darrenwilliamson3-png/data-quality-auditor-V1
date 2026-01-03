import argparse
import csv
import json
from datetime import datetime, date
import sys
import pycountry

# EXIT CODES:
EXIT_OK = 0
EXIT_WARNING = 5
EXIT_ISSUES_FOUND = 10
EXIT_INPUT_ERROR = 20
EXIT_INTERNAL_ERROR = 30

SEVERITY_RANK = {
    "info": 1,
    "warning": 2,
    "error": 3
}

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
        help="Path to CSV or JSON file."
    )

    parser.add_argument(
        "--output-csv",
        help="Write issues to CSV file"
    )

    parser.add_argument(
        "--output-json",
        help="Write issues to json file"
    )

    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Return a non-sero exit code if any issues are found"
    )

    parser.add_argument(
        "--severity-threshold",
        choices=["info", "warning", "error"],
        default="warning",
        help="Minimum severity that counts toward exit code (default: warning)"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output"
    )

    return parser.parse_args()

def load_records(path: str):
    """
    Load records from CSV or JSON file.
    """
    records = []

    with open(path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            records.append(row)

    # Normalise keys ONCE
    records = [
        {k.strip().lower(): v for k, v in record.items()}
        for record in records
    ]

    return records

def check_invalid_emails(records):
    issues = []

    for idx, record in enumerate(records, start=1):
        email = record.get("email", "").strip()

        if not email:
            issues.append({
                "row": idx,
                "field": "email",
                "value": email,
                "reason": "email missing or empty"
            })
            continue

        # Rule 1: must contain exactly one "@"
        if email.count("@") != 1:
            issues.append({
                "row": idx,
                "field": "email",
                "value": email,
                "issue": "missing or multiple @",
                "severity": "warning"
            })
            continue

        local, domain = email.split("@")

        #Rule 2: local and domain must not be empty
        if not local or not domain:
            issues.append({
                "row": idx,
                "field": "email",
                "value": email,
                "reason": "Invalid local or domain part",
                "severity": "warning"
            })
            continue

        # Rule 3: domain must contain a dot
        if "." not in domain:
            issues.append({
                "row": idx,
                "field": "email",
                "value": email,
                "reason": "domain missing dot",
                "severity": "warning"
            })
            continue

        # Rule 4: domain must not start or end with a dot
        if domain.startswith(".") or domain.endswith("."):
            issues.append({
                "row": idx,
                "field": "email",
                "value": email,
                "reason": "domain starts or ends with a dot",
                "severity": "warning"
            })

    return issues

def check_invalid_ages(records):
    issues = []

    for idx, record in enumerate(records, start=1):
        age_raw = record.get("age", "").strip()

        # Rule 1:missing
        if not age_raw:
            issues.append({
                "row": idx,
                "field": "age",
                "value": age_raw,
                "reason": "age missing",
                "severity": "warning"
            })
            continue

        # Rule 2: must be numeric
        if not age_raw.isdigit():
            issues.append({
                "row": idx,
                "field": "age",
                "value": age_raw,
                "reason": "age not numerical",
                "severity": "warning"
            })
            continue

        age = int(age_raw)

        # Rule 3: sensible bounds
        if age < 1 or age > 120:
            issues.append({
                "row": idx,
                "field": "age",
                "value": age,
                "reason": "age out of range",
                "severity": "warning"
            })

    return issues

def load_country_reference(path):
    with open(path) as f:
        return {line.strip().upper() for line in f if line.strip()}

UK_ALIASES = {"UK", "U.K.", "UNITED KINGDOM"}

def resolve_country(value: str | None)-> str | None:
    if not value:
        return None

    raw = value.strip().upper()

    if raw in UK_ALIASES:
        return "United Kingdom"

    # Try exact name
    try:
        return pycountry.countries.lookup(raw).name
    except LookupError:
        return None

def check_invalid_countries(records):
    issues = []

    for idx, record in enumerate(records, start=1):
        raw_country = record.get("country")
        resolved = resolve_country(raw_country)

        if not resolved:
            issues.append({
                "row": idx,
                "field": "country",
                "value": raw_country,
                "reason": "country missing or null",
                "severity": "warning"
            })

    return issues

def check_invalid_signup_dates(records):
    issues = []

    accepted_formats = [
        "%d/%m/%Y",
        "%y/%m/%d",
    ]

    today = date.today()

    for idx, record in enumerate(records, start=1):
        raw_date = record.get("signup_date", "").strip()

        if not raw_date:
            issues.append({
                "row": idx,
                "field": "signup_date",
                "value": raw_date,
                "reason": "signup date missing or empty",
                "severity": "warning"
            })
            continue

        parsed_date = None

        for fmt in accepted_formats:
            try:
                parsed_date = datetime.strptime(raw_date, fmt).date()
                break
            except ValueError:
                continue

        if parsed_date is None:
            issues.append({
                "row": idx,
                "field": "signup_date",
                "value": raw_date,
                "reason": "Invalid date format",
                "severity": "warning"
            })
            continue

        # Optional business rule (recommended)
        if parsed_date > today:
            issues.append({
                "row": idx,
                "field": "signup_date",
                "value": raw_date,
                "reason": "signup_date is in the future",
                "severity": "warning"
            })

    return issues

def build_summary(records, issues):
    return {
        "total_records": len(records),
        "total_issues": len(issues),
        "severity_counts": count_issues_by_severity(issues),
    }

def filter_issues_by_severity(issues, threshold):
    threshold_rank = SEVERITY_RANK[threshold]

    return [
        issue for issue in issues
        if SEVERITY_RANK.get(issue.get("severity", "warning"), 0) >= threshold_rank
    ]

def count_issues_by_severity(issues):
    counts = {
        "info": 0,
        "warning": 0,
        "error": 0,
    }

    for issue in issues:
        severity = issue.get("severity", "warning")
        if severity in counts:
            counts[severity] += 1

    return counts

def export_csv(issues, path):
    if not issues:
        return

    fieldnames = ["row", "field", "value", "reason"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        cleaned = [
            {
                "row": i.get("row"),
                "field": i.get("field"),
                "value": i.get("value"),
                "reason": i.get("reason")
            }
            for i in issues
        ]
        writer.writerows(cleaned)


def export_json(issues, summary, path):
    output = {
        "summary": summary,
        "issues": issues
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

def run_all_checks(records):
    issues = []
    issues.extend(check_invalid_emails(records))
    issues.extend(check_invalid_ages(records))
    issues.extend(check_invalid_countries(records))
    issues.extend(check_invalid_signup_dates(records))
    return issues

def print_summary(summary):
    print(f"Total records: {summary['total_records']}")
    print(f"Total issues: {summary['total_issues']}")
    print("Severity breakdown:")
    for level, count in summary["severity_counts"].items():
        print(f"  {level}: {count}")

def handle_exports(issues, summary, args):
    if args.output_csv:
        export_csv(issues, args.output_csv)

    if args.output_json:
        export_json(
            issues,
            summary,
            args.output_json
        )

def determine_exit_code(summary, issues, args):
    if summary["total_records"] == 0:
        return EXIT_OK

    blocking = filter_issues_by_severity(
        issues,
        args.severity_threshold
    )

    if blocking and args.fail_on_warning:
        return EXIT_WARNING

    if blocking:
        return EXIT_ISSUES_FOUND

    return EXIT_OK

def main():
    args = parse_arguments()

    # 'Loaded records' confirms input parsing; 'Total records' reflects records evaluated
    records = load_records(args.input)
    print(f"Loaded records: {len(records)}")

    all_issues = run_all_checks(records)
    summary = build_summary(records, all_issues)

    filtered_issues = filter_issues_by_severity(
        all_issues,
        args.severity_threshold
    )

    handle_exports(filtered_issues, summary, args)

    if not args.quiet:
        print_summary(summary)

    return determine_exit_code(summary, filtered_issues, args)

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(EXIT_INTERNAL_ERROR)


