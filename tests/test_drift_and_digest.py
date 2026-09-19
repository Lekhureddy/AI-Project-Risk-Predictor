import pandas as pd

from risk_copilot.digest import build_weekly_digest
from risk_copilot.drift import drift_summary, feature_drift_report
from risk_copilot.modeling import FEATURE_COLUMNS


def frame(offset:float=0.0):
    rows=[]
    for i in range(30):
        rows.append({feature:float(i)+offset for feature in FEATURE_COLUMNS})
    return pd.DataFrame(rows)


def test_drift_report_detects_distribution_shift():
    report=feature_drift_report(frame(0),frame(100))
    summary=drift_summary(report)
    assert summary["feature_count"]==len(FEATURE_COLUMNS)
    assert summary["alert"] is True


def test_weekly_digest_separates_worsening_and_improving():
    previous=[
        {"project_id":"A","project_name":"A","risk_score":40,"risk_band":"Medium"},
        {"project_id":"B","project_name":"B","risk_score":70,"risk_band":"High"},
    ]
    current=[
        {"project_id":"A","project_name":"A","risk_score":65,"risk_band":"High"},
        {"project_id":"B","project_name":"B","risk_score":55,"risk_band":"Medium"},
        {"project_id":"C","project_name":"C","risk_score":30,"risk_band":"Low"},
    ]
    digest=build_weekly_digest(previous,current)
    assert digest["worsening"][0]["project_id"]=="A"
    assert digest["improving"][0]["project_id"]=="B"
    assert digest["new"][0]["project_id"]=="C"
