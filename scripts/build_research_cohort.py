from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from risk_copilot.ingestion.github_client import GitHubClient, GitHubAPIError
from risk_copilot.ingestion.snapshot_builder import collect_repository


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a multi-repository Risk Copilot research cohort")
    parser.add_argument("--repos-file", default="configs/public_repositories.txt")
    parser.add_argument("--out", default="data/research")
    parser.add_argument("--max-milestones", type=int, default=4)
    args = parser.parse_args()

    repos = [
        line.strip()
        for line in Path(args.repos_file).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    client = GitHubClient()
    features: list[dict] = []
    labels: list[dict] = []
    warnings: list[str] = []
    failures: list[dict] = []

    for repo in repos:
        try:
            result = collect_repository(
                client,
                repo,
                max_milestones=args.max_milestones,
                collect_reviews=False,
                allow_due_date_proxy=True,
            )
            features.extend(result.features)
            labels.extend(result.labels)
            warnings.extend(result.warnings)
            print(f"{repo}: features={len(result.features)} labels={len(result.labels)}")
        except (GitHubAPIError, ValueError) as exc:
            failures.append({"repo": repo, "error": str(exc)})
            print(f"{repo}: failed: {exc}")

    out = Path(args.out)
    write_csv(out / "milestone_features.csv", features)
    write_csv(out / "milestone_labels.csv", labels)
    (out / "collection_warnings.json").write_text(json.dumps(warnings, indent=2), encoding="utf-8")
    (out / "collection_failures.json").write_text(json.dumps(failures, indent=2), encoding="utf-8")

    print(f"total_features={len(features)} total_labels={len(labels)} failures={len(failures)}")
    return 0 if features else 1


if __name__ == "__main__":
    raise SystemExit(main())
