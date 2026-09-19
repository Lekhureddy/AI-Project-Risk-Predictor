from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from typing import Iterable


FEATURE_COLUMNS = (
    "open_issue_count",
    "closed_issue_count",
    "open_pr_count",
    "closed_pr_count",
    "median_open_issue_age_days",
    "scope_added_14d",
    "scope_removed_14d",
    "reviews_14d",
    "median_first_review_latency_hours",
    "commit_count_14d",
    "active_contributors_14d",
)

REQUIRED_COLUMNS = (
    "repo",
    "milestone_title",
    "snapshot_date",
    "horizon_days",
    "due_on_at_snapshot",
    "due_date_source",
    "membership_history_complete",
    "training_eligible",
    "label",
    "label_version",
)


@dataclass(frozen=True)
class QualityReport:
    row_count: int
    repository_count: int
    project_count: int
    eligible_row_count: int
    eligible_fraction: float
    label_counts: dict[str, int]
    horizon_counts: dict[str, int]
    duplicate_identity_count: int
    missing_required_counts: dict[str, int]
    feature_missing_fraction: dict[str, float]
    due_date_source_counts: dict[str, int]
    membership_history_complete_fraction: float
    blockers: list[str]
    warnings: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def _truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _missing(value) -> bool:
    return value is None or str(value).strip() in {"", "None", "nan", "NaN"}


def validate_rows(
    rows: Iterable[dict],
    *,
    min_rows: int = 100,
    min_repositories: int = 5,
    min_eligible_fraction: float = 0.70,
    max_feature_missing_fraction: float = 0.40,
) -> QualityReport:
    rows = list(rows)
    n = len(rows)
    repos = {str(r.get("repo")) for r in rows if not _missing(r.get("repo"))}
    projects = {
        (str(r.get("repo")), str(r.get("milestone_title")))
        for r in rows
        if not _missing(r.get("repo")) and not _missing(r.get("milestone_title"))
    }

    eligible = sum(_truthy(r.get("training_eligible")) for r in rows)
    eligible_fraction = eligible / n if n else 0.0

    labels = Counter(str(r.get("label") or "Missing") for r in rows)
    horizons = Counter(str(r.get("horizon_days") or "Missing") for r in rows)
    sources = Counter(str(r.get("due_date_source") or "Missing") for r in rows)

    missing_required = {
        col: sum(_missing(r.get(col)) for r in rows)
        for col in REQUIRED_COLUMNS
    }

    feature_missing_fraction = {}
    for col in FEATURE_COLUMNS:
        missing = sum(_missing(r.get(col)) for r in rows)
        feature_missing_fraction[col] = round(missing / n, 4) if n else 1.0

    identities = Counter(
        (r.get("repo"), r.get("milestone_title"), r.get("snapshot_date"), r.get("horizon_days"))
        for r in rows
    )
    duplicates = sum(count - 1 for count in identities.values() if count > 1)

    membership_complete = sum(_truthy(r.get("membership_history_complete")) for r in rows)
    membership_fraction = membership_complete / n if n else 0.0

    blockers: list[str] = []
    warnings: list[str] = []

    if n < min_rows:
        blockers.append(f"too_few_rows:{n}<{min_rows}")
    if len(repos) < min_repositories:
        blockers.append(f"too_few_repositories:{len(repos)}<{min_repositories}")
    if eligible_fraction < min_eligible_fraction:
        blockers.append(
            f"eligible_fraction_too_low:{eligible_fraction:.3f}<{min_eligible_fraction:.3f}"
        )
    if duplicates:
        blockers.append(f"duplicate_snapshot_identity:{duplicates}")
    for col, count in missing_required.items():
        if count:
            blockers.append(f"missing_required:{col}:{count}")

    for col, frac in feature_missing_fraction.items():
        if frac > max_feature_missing_fraction:
            warnings.append(
                f"feature_missingness_high:{col}:{frac:.3f}>{max_feature_missing_fraction:.3f}"
            )

    supported = {"On Track", "Delayed", "Critical"}
    supported_counts = {k: v for k, v in labels.items() if k in supported}
    if len([v for v in supported_counts.values() if v > 0]) < 2:
        blockers.append("insufficient_supported_label_diversity")
    if labels.get("Unknown", 0):
        warnings.append(f"unknown_labels_present:{labels['Unknown']}")

    return QualityReport(
        row_count=n,
        repository_count=len(repos),
        project_count=len(projects),
        eligible_row_count=eligible,
        eligible_fraction=round(eligible_fraction, 4),
        label_counts=dict(sorted(labels.items())),
        horizon_counts=dict(sorted(horizons.items())),
        duplicate_identity_count=duplicates,
        missing_required_counts=missing_required,
        feature_missing_fraction=feature_missing_fraction,
        due_date_source_counts=dict(sorted(sources.items())),
        membership_history_complete_fraction=round(membership_fraction, 4),
        blockers=blockers,
        warnings=warnings,
    )
