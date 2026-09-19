from __future__ import annotations

from dataclasses import dataclass, asdict
from math import log

import numpy as np
import pandas as pd

from .modeling import FEATURE_COLUMNS


@dataclass(frozen=True)
class FeatureDrift:
    feature: str
    psi: float | None
    reference_mean: float | None
    current_mean: float | None
    status: str


def _psi(reference: pd.Series, current: pd.Series, bins: int = 10) -> float | None:
    ref = pd.to_numeric(reference, errors="coerce").dropna().to_numpy(dtype=float)
    cur = pd.to_numeric(current, errors="coerce").dropna().to_numpy(dtype=float)
    if len(ref) < 10 or len(cur) < 10:
        return None
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    edges[0] = -np.inf
    edges[-1] = np.inf
    ref_counts, _ = np.histogram(ref, bins=edges)
    cur_counts, _ = np.histogram(cur, bins=edges)
    eps = 1e-6
    ref_pct = np.maximum(ref_counts / max(ref_counts.sum(), 1), eps)
    cur_pct = np.maximum(cur_counts / max(cur_counts.sum(), 1), eps)
    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


def feature_drift_report(reference: pd.DataFrame, current: pd.DataFrame) -> list[dict]:
    report=[]
    for feature in FEATURE_COLUMNS:
        if feature not in reference.columns or feature not in current.columns:
            continue
        psi=_psi(reference[feature],current[feature])
        ref_vals=pd.to_numeric(reference[feature],errors="coerce")
        cur_vals=pd.to_numeric(current[feature],errors="coerce")
        if psi is None:
            status="insufficient_data"
        elif psi >= 0.25:
            status="high"
        elif psi >= 0.10:
            status="moderate"
        else:
            status="low"
        item=FeatureDrift(
            feature=feature,
            psi=None if psi is None else round(psi,4),
            reference_mean=None if ref_vals.dropna().empty else round(float(ref_vals.mean()),4),
            current_mean=None if cur_vals.dropna().empty else round(float(cur_vals.mean()),4),
            status=status,
        )
        report.append(asdict(item))
    return report


def drift_summary(report:list[dict])->dict:
    counts={"high":0,"moderate":0,"low":0,"insufficient_data":0}
    for item in report:
        counts[item["status"]]=counts.get(item["status"],0)+1
    return {
        "feature_count":len(report),
        "status_counts":counts,
        "alert":counts.get("high",0)>0,
    }
