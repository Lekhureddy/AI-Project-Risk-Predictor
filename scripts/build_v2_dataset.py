from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from risk_copilot.ingestion.github_client import GitHubClient
from risk_copilot.ingestion.snapshot_builder import collect_repository


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({k for row in rows for k in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Risk Copilot V2 GitHub milestone dataset")
    parser.add_argument("--repo", action="append", required=True, help="owner/name; repeat for multiple repos")
    parser.add_argument("--out", default="data/processed", help="output directory")
    parser.add_argument("--max-milestones", type=int, default=None)
    parser.add_argument("--skip-reviews", action="store_true")
    parser.add_argument("--allow-due-date-proxy", action="store_true")
    args = parser.parse_args()

    client = GitHubClient()
    all_features = []
    all_labels = []
    warnings = []

    for repo in args.repo:
        result = collect_repository(
            client,
            repo,
            max_milestones=args.max_milestones,
            collect_reviews=not args.skip_reviews,
            allow_due_date_proxy=args.allow_due_date_proxy,
        )
        all_features.extend(result.features)
        all_labels.extend(result.labels)
        warnings.extend(result.warnings)

    out = Path(args.out)
    write_csv(out / "milestone_features.csv", all_features)
    write_csv(out / "milestone_labels.csv", all_labels)
    (out / "collection_warnings.json").write_text(json.dumps(warnings, indent=2), encoding="utf-8")

    print(f"features={len(all_features)} labels={len(all_labels)} warnings={len(warnings)}")
    if client.rate_limit.remaining is not None:
        print(f"github_rate_limit_remaining={client.rate_limit.remaining}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
