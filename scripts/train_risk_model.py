from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import pandas as pd

from risk_copilot.data_quality import validate_rows
from risk_copilot.modeling import (
    calibrate_model,
    evaluate_classifier,
    grouped_split,
    prepare_training_frame,
    train_candidates,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Train and evaluate the Risk Copilot predictive model")
    parser.add_argument("csv_path")
    parser.add_argument("--out", default="artifacts/model")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--min-rows", type=int, default=100)
    parser.add_argument("--min-repositories", type=int, default=5)
    parser.add_argument("--min-eligible-fraction", type=float, default=0.70)
    args = parser.parse_args()

    raw = pd.read_csv(args.csv_path)
    quality = validate_rows(
        raw.to_dict(orient="records"),
        min_rows=args.min_rows,
        min_repositories=args.min_repositories,
        min_eligible_fraction=args.min_eligible_fraction,
    )
    if quality.blockers:
        print(json.dumps({"status": "blocked", "quality": quality.to_dict()}, indent=2))
        return 2

    df = prepare_training_frame(raw)
    split = grouped_split(df, test_size=args.test_size, random_state=args.random_state)
    models, metrics = train_candidates(split, random_state=args.random_state)

    non_baseline = {k: v for k, v in metrics.items() if k != "majority_baseline"}
    selected_name = max(non_baseline, key=lambda name: non_baseline[name]["macro_f1"])
    baseline_f1 = metrics["majority_baseline"]["macro_f1"]
    selected_f1 = metrics[selected_name]["macro_f1"]
    lift = selected_f1 - baseline_f1

    calibrated = calibrate_model(models[selected_name], split.train)
    calibrated_metrics = evaluate_classifier(calibrated, split.test)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "risk_model.pkl").open("wb") as handle:
        pickle.dump(calibrated, handle)

    report = {
        "status": "trained",
        "validation_profile": {
            "min_rows": args.min_rows,
            "min_repositories": args.min_repositories,
            "min_eligible_fraction": args.min_eligible_fraction,
        },
        "data_quality": quality.to_dict(),
        "selected_model": selected_name,
        "baseline_macro_f1": baseline_f1,
        "selected_macro_f1": selected_f1,
        "macro_f1_lift_vs_majority": lift,
        "candidate_metrics": metrics,
        "calibrated_metrics": calibrated_metrics,
        "train_rows": len(split.train),
        "test_rows": len(split.test),
        "train_repositories": sorted(split.train["repo"].unique().tolist()),
        "test_repositories": sorted(split.test["repo"].unique().tolist()),
        "reference_feature_medians": {
            col: (None if pd.isna(split.train[col].median()) else float(split.train[col].median()))
            for col in split.train.columns
            if col in __import__("risk_copilot.modeling", fromlist=["FEATURE_COLUMNS"]).FEATURE_COLUMNS
        },
    }
    (out / "model_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
