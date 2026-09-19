from __future__ import annotations

from dataclasses import dataclass, asdict

import pandas as pd

from .modeling import FEATURE_COLUMNS, risk_score_from_probabilities


@dataclass(frozen=True)
class Driver:
    feature: str
    contribution: float
    current_value: float | None
    reference_value: float | None
    direction: str


def _risk_score(model, frame: pd.DataFrame) -> float:
    proba = model.predict_proba(frame)[0]
    classes = list(model.classes_)
    probs = {str(label): float(proba[i]) for i, label in enumerate(classes)}
    return risk_score_from_probabilities(probs)


def explain_prediction(model, row: dict | pd.Series, reference_frame: pd.DataFrame, *, top_k: int = 5) -> list[dict]:
    if reference_frame.empty:
        raise ValueError("reference frame is empty")

    base = pd.DataFrame([dict(row)])
    for feature in FEATURE_COLUMNS:
        if feature not in base.columns:
            base[feature] = None
    base = base[list(FEATURE_COLUMNS)].apply(pd.to_numeric, errors="coerce").astype(float)

    reference = reference_frame.copy()
    for feature in FEATURE_COLUMNS:
        if feature not in reference.columns:
            reference[feature] = None
    reference = reference[list(FEATURE_COLUMNS)].apply(pd.to_numeric, errors="coerce").astype(float)
    medians = reference.median(numeric_only=True)

    current_score = _risk_score(model, base)
    drivers: list[Driver] = []

    for feature in FEATURE_COLUMNS:
        counterfactual = base.copy()
        reference_value = medians.get(feature)
        if pd.isna(reference_value):
            continue
        current_value = base.iloc[0][feature]
        counterfactual.loc[counterfactual.index[0], feature] = reference_value
        counterfactual_score = _risk_score(model, counterfactual)
        contribution = round(current_score - counterfactual_score, 2)
        direction = "raises risk" if contribution > 0 else "reduces risk" if contribution < 0 else "neutral"
        drivers.append(
            Driver(
                feature=feature,
                contribution=contribution,
                current_value=None if pd.isna(current_value) else float(current_value),
                reference_value=float(reference_value),
                direction=direction,
            )
        )

    drivers.sort(key=lambda d: abs(d.contribution), reverse=True)
    return [asdict(d) for d in drivers[:top_k]]
