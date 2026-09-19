from __future__ import annotations

from collections import Counter


def build_weekly_digest(previous:list[dict], current:list[dict])->dict:
    prev={str(x["project_id"]):dict(x) for x in previous}
    cur={str(x["project_id"]):dict(x) for x in current}
    changes=[]

    for project_id,item in cur.items():
        old=prev.get(project_id)
        old_score=float(old["risk_score"]) if old else None
        new_score=float(item["risk_score"])
        delta=None if old_score is None else round(new_score-old_score,2)
        changes.append({
            "project_id":project_id,
            "project_name":item.get("project_name",project_id),
            "previous_risk_score":old_score,
            "current_risk_score":new_score,
            "risk_change":delta,
            "risk_band":item.get("risk_band"),
            "is_new":old is None,
        })

    worsening=sorted(
        [x for x in changes if x["risk_change"] is not None and x["risk_change"]>0],
        key=lambda x:x["risk_change"],
        reverse=True,
    )
    improving=sorted(
        [x for x in changes if x["risk_change"] is not None and x["risk_change"]<0],
        key=lambda x:x["risk_change"],
    )
    new=[x for x in changes if x["is_new"]]

    return {
        "project_count":len(cur),
        "worsening":worsening,
        "improving":improving,
        "new":new,
        "attention_count":sum(1 for x in cur.values() if x.get("risk_band") in {"High","Critical"}),
    }
