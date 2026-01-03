# Data Quality Auditor (Python, AI-Assisted)

## Overview

**Data Quality Auditor** is a Python CLI utility designed to validate real-world CSV datasets
and identify common data quality issues such as invalid emails, inconsistent dates, missing values,
and invalid country codes.

The tool is intentionally built for **realistic, messy datasets**, not idealised inputs.
It focuses on **clear validation logic, reliable output, and safe failure behaviour**.

This project was developed using **AI-assisted Python workflows**, with all logic typed, tested,
debugged, and validated manually.

---
## Key Features
* ✅ CSV input validation
* 📧 Email format validation
* 📅 Date validation (missing, malformed, future dates)
* 🌍 Country validation using `pycountry` (ISO-aware, not hard-coded lists)
* ⚠️ Issue severity classification (`info`, `warning`, `error`)
* 📊 Summary statistics (total records, total issues, severity breakdown)
* 📄 CSV and JSON report exports
* 🧪 Defensive schema checks and guard rails
* 🚦 Meaningful exit codes for automation / CI use

---
## Why This Tool Exists
In real business environments, data quality issues are:
* expensive
* inconsistent
* rarely clean
* often discovered too late

This tool demonstrates how to:
* validate external datasets **without assuming perfect structure**
* fail safely when input is unexpected
* produce outputs usable by **humans and automation**
* build maintainable validation logic that can evolve over time

---
## Example Usage

```bash
python data_quality_auditor.py --input test_data.csv
```

Export results:
```bash
python data_quality_auditor.py --input test_data.csv --csv report.csv --json report.json
```

Quiet mode (machine-friendly):
```bash
python data_quality_auditor.py --input test_data.csv --quiet
```

---
## Output

### Console
* Total records processed
* Total issues found
* Severity breakdown

### CSV
* Row-level issues with context
* Suitable for review, sorting, and reporting

### JSON
* Full structured output including summary
* Designed for downstream tooling or dashboards

---
## Exit Codes
| Code | Meaning            |
| ---- | ------------------ |
| 0    | No issues detected |
| 1    | Warnings detected  |
| 2    | Errors detected    |

This allows the tool to be used safely in scripts, pipelines, and automated checks.

---

## Design Notes
* Built with **explicit schema assumptions** rather than silent failures
* Uses defensive programming to prevent misleading results
* Prefers clarity over cleverness
* Structured for future versioning (V2+ features planned)

---
## Limitations (Intentional)
* Validation rules are conservative by design
* No automatic data correction (audit, not mutation)
* CSV-focused (database connectors planned for future versions)

These limitations are deliberate to keep V1 safe and predictable.

---
## Tech Stack
* Python 3.x
* Standard library (`csv`, `json`, `argparse`, `datetime`)
* `pycountry` for ISO-compliant country validation

---
## About This Project
This project is part of a broader portfolio focused on:
* AI-assisted Python tooling
* data validation and automation
* pragmatic, business-oriented utilities

All code was written manually with AI used as a **development assistant**, not a code generator.

---
## Next Steps (Planned)
* Configurable validation rules
* Field-level severity tuning
* Schema profiles
* Batch / directory processing
* CI integration examples

---
## Licence
MIT

---
## Author
Darren Williamson
Python Utility Development * Automation * Data Analysis * AI-assisted tooling
Uk Citizen / Spain-based / Remote
LinkedIn: https://www.linkedin.com/in/darren-williamson3/
