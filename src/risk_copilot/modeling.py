from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

SUPPORTED_LABELS = ("On Track", "Delayed", "Critical")

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
    "horizon_days",
)


@dataclass
class SplitData:
    train: pd.DataFrame
    test: pd.DataFrame


def prepare_training_frame(rows: list[dict] | pd.DataFrame) -> pd.DataFrame:
    df = rows.copy() if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    if df.empty:
        raise ValueError("training dataset is empty")

    required = set(FEATURE_COLUMNS) | {"repo", "label", "training_eligible"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"missing required training columns: {missing}")

    eligible = df["training_eligible"].astype(str).str.lower().isin({"true", "1", "yes"})
    df = df[eligible & df["label"].isin(SUPPORTED_LABELS)].copy()
    if df.empty:
        raise ValueError("no training-eligible supported labels remain")

    for col in FEATURE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df["label"].nunique() < 2:
        raise ValueError("at least two supported outcome classes are required")

    return df


def grouped_split(df: pd.DataFrame, *, test_size: float = 0.2, random_state: int = 42) -> SplitData:
    if df["repo"].nunique() < 2:
        raise ValueError("at least two repositories are required for grouped validation")

    desired_labels = set(df["label"].unique())
    best = None
    for offset in range(100):
        splitter = GroupShuffleSplit(
            n_splits=1,
            test_size=test_size,
            random_state=random_state + offset,
        )
        train_idx, test_idx = next(splitter.split(df, groups=df["repo"]))
        train = df.iloc[train_idx].copy()
        test = df.iloc[test_idx].copy()

        if set(train["repo"]) & set(test["repo"]):
            raise AssertionError("repository leakage detected across train/test split")

        train_labels = set(train["label"].unique())
        test_labels = set(test["label"].unique())
        score = len(train_labels & desired_labels) + len(test_labels & desired_labels)
        if best is None or score > best[0]:
            best = (score, train, test)

        if desired_labels.issubset(train_labels) and desired_labels.issubset(test_labels):
            return SplitData(train=train, test=test)

    if best is None:
        raise ValueError("unable to create grouped validation split")
    _, train, test = best
    if train["label"].nunique() < 2 or test["label"].nunique() < 2:
        raise ValueError(
            "grouped split cannot provide adequate label diversity; collect more repositories per outcome"
        )
    return SplitData(train=train, test=test)


def _numeric_pipeline(estimator: Any) -> Pipeline:
    transformer = ColumnTransformer(
        [("numeric", SimpleImputer(strategy="median"), list(FEATURE_COLUMNS))],
        remainder="drop",
    )
    return Pipeline([("features", transformer), ("model", estimator)])


def candidate_models(random_state: int = 42) -> dict[str, Pipeline]:
    return {
        "majority_baseline": _numeric_pipeline(DummyClassifier(strategy="most_frequent")),
        "logistic_regression": _numeric_pipeline(
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=random_state)
        ),
        "hist_gradient_boosting": _numeric_pipeline(
            HistGradientBoostingClassifier(
                learning_rate=0.08,
                max_iter=200,
                max_leaf_nodes=15,
                l2_regularization=0.5,
                random_state=random_state,
            )
        ),
    }


def evaluate_classifier(model: Pipeline, test: pd.DataFrame) -> dict[str, Any]:
    X = test[list(FEATURE_COLUMNS)]
    y = test["label"].astype(str)
    pred = model.predict(X)

    result: dict[str, Any] = {
        "macro_f1": float(f1_score(y, pred, average="macro", zero_division=0)),
        "macro_precision": float(precision_score(y, pred, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(y, pred, average="macro", zero_division=0)),
        "classification_report": classification_report(y, pred, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y, pred, labels=list(SUPPORTED_LABELS)).tolist(),
    }

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        classes = list(model.classes_)
        per_class_brier = {}
        for label in SUPPORTED_LABELS:
            if label in classes:
                binary_truth = (y == label).astype(int)
                per_class_brier[label] = float(
                    brier_score_loss(binary_truth, proba[:, classes.index(label)])
                )
        result["brier_by_class"] = per_class_brier
        result["mean_brier"] = float(np.mean(list(per_class_brier.values()))) if per_class_brier else None

    return result


def train_candidates(split: SplitData, *, random_state: int = 42) -> tuple[dict[str, Pipeline], dict[str, dict[str, Any]]]:
    trained = {}
    metrics = {}
    X_train = split.train[list(FEATURE_COLUMNS)]
    y_train = split.train["label"].astype(str)

    for name, model in candidate_models(random_state=random_state).items():
        model.fit(X_train, y_train)
        trained[name] = model
        metrics[name] = evaluate_classifier(model, split.test)

    return trained, metrics


def calibrate_model(base_model: Pipeline, train: pd.DataFrame, *, cv: int = 3) -> CalibratedClassifierCV:
    label_counts = train["label"].value_counts()
    feasible_cv = min(cv, int(label_counts.min()))
    if feasible_cv < 2:
        raise ValueError("calibration requires at least two examples in every training class")

    calibrated = CalibratedClassifierCV(estimator=base_model, method="isotonic", cv=feasible_cv)
    calibrated.fit(train[list(FEATURE_COLUMNS)], train["label"].astype(str))
    return calibrated


def risk_score_from_probabilities(probabilities: dict[str, float]) -> float:
    delayed = float(probabilities.get("Delayed", 0.0))
    critical = float(probabilities.get("Critical", 0.0))
    return round(100.0 * (0.5 * delayed + critical), 2)
