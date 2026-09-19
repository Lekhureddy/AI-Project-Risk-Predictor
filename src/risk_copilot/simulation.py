from __future__ import annotations

from dataclasses import dataclass, asdict

import pandas as pd

from .modeling import FEATURE_COLUMNS, risk_score_from_probabilities


@dataclass(frozen=True)
class ScenarioResult:
    current_risk_score: float
    scenario_risk_score: float
    delta: float
    changed_features: dict[str, dict[str, float | None]]
    disclaimer: str


def _score(model, row: pd.DataFrame) -> float:
    probabilities = model.predict_proba(row)[0]
    classes = list(model.classes_)
    mapped = {str(label): float(probabilities[i]) for i, label in enumerate(classes)}
    return risk_score_from_probabilities(mapped)


def simulate_scenario(
    model,
    current_features: dict,
    changes: dict[str, float],
    *,
    bounds: dict[str, tuple[float | None, float | None]] | None = None,
) -> dict:
    unknown = sorted(set(changes) - set(FEATURE_COLUMNS))
    if unknown:
        raise ValueError(f"unsupported scenario features: {unknown}")

    base = pd.DataFrame([{k: current_features.get(k) for k in FEATURE_COLUMNS}])
    base = base.apply(pd.to_numeric, errors="coerce")
    scenario = base.copy()
    applied = {}

    for feature, value in changes.items():
        numeric = float(value)
        if bounds and feature in bounds:
            lower, upper = bounds[feature]
            if lower is not None and numeric < lower:
                raise ValueError(f"{feature} is below allowed bound")
            if upper is not None and numeric > upper:
                raise ValueError(f"{feature} is above allowed bound")
        before = scenario.iloc[0][feature]
        scenario.loc[scenario.index[0], feature] = numeric
        applied[feature] = {
            "before": None if pd.isna(before) else float(before),
            "after": numeric,
        }

    current_score = _score(model, base)
    scenario_score = _score(model, scenario)
    result = ScenarioResult(
        current_risk_score=current_score,
        scenario_risk_score=scenario_score,
        delta=round(scenario_score - current_score, 2),
        changed_features=applied,
        disclaimer=(
            "Model-based scenario estimate only. This is not a causal forecast or a guarantee "
            "that changing these inputs will produce the predicted outcome."
        ),
    )
    return asdict(result)
