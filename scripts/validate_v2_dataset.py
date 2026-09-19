from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from risk_copilot.data_quality import validate_rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Risk Copilot V2 training data")
    parser.add_argument("csv_path")
    parser.add_argument("--report", default="data/processed/data_quality_report.json")
    parser.add_argument("--min-rows", type=int, default=100)
    parser.add_argument("--min-repositories", type=int, default=5)
    parser.add_argument("--min-eligible-fraction", type=float, default=0.70)
    args = parser.parse_args()

    with open(args.csv_path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    report = validate_rows(
        rows,
        min_rows=args.min_rows,
        min_repositories=args.min_repositories,
        min_eligible_fraction=args.min_eligible_fraction,
    )
    payload = report.to_dict()

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 1 if report.blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
