from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from risk_copilot.demo import demo_assessments
from risk_copilot.digest import build_weekly_digest
from risk_copilot.evidence_graph import build_evidence_graph
from risk_copilot.modeling import FEATURE_COLUMNS
from risk_copilot.live_repository import inspect_milestone, list_due_milestones
from risk_copilot.portfolio import build_portfolio_summary
from risk_copilot.service import RiskCopilotService
from risk_copilot.simulation import simulate_scenario


st.set_page_config(
    page_title="Risk Copilot",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

service = RiskCopilotService(db_path=os.getenv("RISK_COPILOT_DB", "data/risk_copilot.db"))


FEATURE_LABELS = {
    "open_issue_count": "Open issues",
    "closed_issue_count": "Closed issues",
    "open_pr_count": "Open pull requests",
    "closed_pr_count": "Closed pull requests",
    "median_open_issue_age_days": "Median open issue age (days)",
    "scope_added_14d": "Scope added in last 14 days",
    "scope_removed_14d": "Scope removed in last 14 days",
    "reviews_14d": "Reviews in last 14 days",
    "median_first_review_latency_hours": "Median first-review latency (hours)",
    "commit_count_14d": "Commits in last 14 days",
    "active_contributors_14d": "Active contributors in last 14 days",
    "horizon_days": "Days before due date",
}


def badge(value: str) -> str:
    icons = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🟢",
    }
    return f"{icons.get(value, '⚪')} {value}"


def timeline_chart(points: list[dict]) -> go.Figure:
    frame = pd.DataFrame(points)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frame["timestamp"],
            y=frame["risk_score"],
            mode="lines+markers",
            name="Risk score",
        )
    )
    fig.update_layout(
        yaxis_title="Risk score",
        xaxis_title="",
        yaxis_range=[0, 100],
        height=330,
        margin=dict(l=10, r=10, t=20, b=10),
    )
    return fig


def evidence_graph_chart(project_id: str, project_name: str, evidence: list[dict]) -> go.Figure:
    graph = build_evidence_graph(
        project_id=project_id,
        project_label=project_name,
        evidence_items=evidence,
    )
    pos = nx.spring_layout(graph, seed=42)

    edge_x = []
    edge_y = []
    for source, target in graph.edges():
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    nodes = list(graph.nodes())
    node_x = [pos[n][0] for n in nodes]
    node_y = [pos[n][1] for n in nodes]
    labels = [graph.nodes[n].get("label", n) for n in nodes]
    types = [graph.nodes[n].get("node_type", "unknown") for n in nodes]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            hoverinfo="none",
            line=dict(width=1),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=labels,
            textposition="top center",
            customdata=types,
            hovertemplate="%{text}<br>%{customdata}<extra></extra>",
            marker=dict(size=18),
            showlegend=False,
        )
    )
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def portfolio_page(demo_mode: bool):
    st.title("Risk Copilot")
    st.caption("Evidence-grounded delivery intelligence for engineering teams")

    if demo_mode:
        st.info(
            "Demo mode is using clearly labeled illustrative project records. "
            "No demo metric is presented as measured model performance."
        )

    summary = service.portfolio(demo=demo_mode)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Active", summary["active_count"])
    c2.metric("Critical", summary["band_counts"]["Critical"])
    c3.metric("High", summary["band_counts"]["High"])
    c4.metric("Medium", summary["band_counts"]["Medium"])
    c5.metric("Low", summary["band_counts"]["Low"])

    st.subheader("Needs attention")
    rows = []
    for item in summary["needs_attention"]:
        rows.append(
            {
                "Project": item.get("project_name", item.get("project_id")),
                "Risk": item["risk_score"],
                "Band": item["risk_band"],
                "Change": item.get("risk_change", 0),
            }
        )
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No saved assessments yet.")

    st.subheader("Emerging risks")
    emerging = summary["emerging_risks"]
    if emerging:
        for item in emerging:
            st.write(
                f"**{item.get('project_name', item.get('project_id'))}** — "
                f"{badge(item['risk_band'])} · {item['risk_score']:.0f} · "
                f"↑ {item.get('risk_change', 0):.0f}"
            )
    else:
        st.caption("No rapidly worsening items are currently available.")


def project_page(demo_mode: bool):
    st.title("Project Intelligence")

    if demo_mode:
        projects = demo_assessments()
        options = {p["project_name"]: p["project_id"] for p in projects}
    else:
        saved = service.store.list_assessments()
        latest = {}
        for item in saved:
            latest[item["project_id"]] = item
        options = {
            item.get("project_name", project_id): project_id
            for project_id, item in latest.items()
        }

    if not options:
        st.info("No project assessments are available yet.")
        return

    selected_name = st.selectbox("Project", list(options))
    project_id = options[selected_name]

    detail = service.project_detail(project_id, demo=demo_mode)
    latest = detail["latest"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Risk score", f"{latest['risk_score']:.0f}/100")
    c2.metric("Risk band", badge(latest["risk_band"]))
    c3.metric(
        "Trend",
        detail["timeline_summary"]["direction"].title(),
        detail["timeline_summary"]["net_change"],
    )

    st.subheader("Risk timeline")
    st.plotly_chart(timeline_chart(detail["timeline"]), use_container_width=True)

    st.subheader("Why Risk Copilot is concerned")
    if detail["drivers"]:
        for i, driver in enumerate(detail["drivers"], 1):
            with st.expander(f"{i}. {driver.get('claim', driver.get('feature', 'Risk driver'))}"):
                if driver.get("contribution") is not None:
                    st.metric("Model contribution", f"{driver['contribution']:+.1f} risk points")
                for citation in driver.get("citations", []):
                    st.code(
                        f"{citation.get('evidence_id')}: {citation.get('quote')}",
                        language=None,
                    )
    else:
        st.caption("No verified explanatory drivers are available.")

    st.subheader("Evidence")
    if detail["evidence"]:
        st.plotly_chart(
            evidence_graph_chart(
                project_id,
                latest.get("project_name", project_id),
                detail["evidence"],
            ),
            use_container_width=True,
        )
        for item in detail["evidence"]:
            st.markdown(f"**{item['evidence_id']} — {item['title']}**")
            st.caption(item["text"])
    else:
        st.caption("No evidence records are available.")

    st.subheader("Challenge this assessment")
    evidence_ids = [x["evidence_id"] for x in detail["evidence"]]
    challenged = st.multiselect(
        "Evidence you believe is stale, irrelevant, or incorrect",
        evidence_ids,
    )
    if st.button("Challenge evidence", disabled=not challenged):
        result = service.challenge(
            drivers=detail["drivers"],
            evidence_ids=challenged,
        )
        st.success(
            f"Removed {result['challenge']['removed_driver_count']} evidence-backed driver(s) "
            "from the narrative review."
        )
        st.caption(result["challenge"]["note"])

    st.subheader("Was this assessment useful?")
    feedback_col1, feedback_col2 = st.columns(2)
    note = st.text_input("Optional feedback note", key=f"feedback_note_{latest['assessment_id']}")
    with feedback_col1:
        if st.button("Agree", key=f"agree_{latest['assessment_id']}"):
            service.store.save_feedback(
                assessment_id=latest["assessment_id"],
                verdict="agree",
                note=note or None,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            st.success("Feedback recorded.")
    with feedback_col2:
        if st.button("Disagree", key=f"disagree_{latest['assessment_id']}"):
            service.store.save_feedback(
                assessment_id=latest["assessment_id"],
                verdict="disagree",
                note=note or None,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            st.success("Feedback recorded.")


def assessment_page():
    st.title("New Assessment")

    if not service.model_available:
        st.warning(
            "The validated V2 model artifact is not available yet. "
            "Assessment is intentionally disabled instead of falling back to the legacy synthetic model."
        )
        st.caption(
            "The data pipeline and model-training system are implemented; a production assessment "
            "will be enabled only after real-data validation passes."
        )
        return

    project_id = st.text_input("Project ID", "my-project")
    project_name = st.text_input("Project name", "My Project")

    features = {}
    cols = st.columns(2)
    for idx, feature in enumerate(FEATURE_COLUMNS):
        default = 14.0 if feature == "horizon_days" else 0.0
        with cols[idx % 2]:
            features[feature] = st.number_input(
                FEATURE_LABELS.get(feature, feature),
                min_value=0.0,
                value=default,
                step=1.0,
                key=f"assess_{feature}",
            )

    if st.button("Run assessment", type="primary"):
        result = service.assess_features(
            project_id=project_id,
            project_name=project_name,
            features=features,
        )
        st.success("Assessment saved.")
        c1, c2 = st.columns(2)
        c1.metric("Risk score", result["risk_score"])
        c2.metric("Risk band", badge(result["risk_band"]))
        st.json(result["probabilities"])


def decision_lab_page():
    st.title("Decision Lab")
    st.write(
        "Explore how the predictive model responds to explicit feature scenarios. "
        "Results are model-based scenario estimates, not causal forecasts."
    )

    if not service.model_available:
        st.warning(
            "Decision Lab requires the validated V2 model artifact. "
            "It remains disabled rather than generating illustrative numbers that could be mistaken for model output."
        )
        return

    model = service.load_model()
    current = {}
    changes = {}

    st.subheader("Current state")
    cols = st.columns(2)
    for idx, feature in enumerate(FEATURE_COLUMNS):
        default = 14.0 if feature == "horizon_days" else 0.0
        with cols[idx % 2]:
            current[feature] = st.number_input(
                FEATURE_LABELS.get(feature, feature),
                min_value=0.0,
                value=default,
                step=1.0,
                key=f"current_{feature}",
            )

    st.subheader("Scenario changes")
    candidates = st.multiselect(
        "Choose features to change",
        FEATURE_COLUMNS,
        format_func=lambda x: FEATURE_LABELS.get(x, x),
    )
    for feature in candidates:
        changes[feature] = st.number_input(
            f"Scenario: {FEATURE_LABELS.get(feature, feature)}",
            min_value=0.0,
            value=float(current[feature]),
            step=1.0,
            key=f"scenario_{feature}",
        )

    if st.button("Run scenario", disabled=not changes, type="primary"):
        result = simulate_scenario(model, current, changes)
        c1, c2, c3 = st.columns(3)
        c1.metric("Current risk", result["current_risk_score"])
        c2.metric("Scenario risk", result["scenario_risk_score"])
        c3.metric("Change", result["delta"])
        st.info(result["disclaimer"])


def interventions_page(demo_mode: bool):
    st.title("Intervention Memory")
    st.write(
        "Record human decisions about recommended interventions and later compare them with observed outcomes."
    )

    assessments = demo_assessments() if demo_mode else service.store.list_assessments()
    if not assessments:
        st.info("No assessments are available.")
        return

    names = {
        f"{a.get('project_name', a['project_id'])} · {a['assessment_id']}": a
        for a in assessments
    }
    selected = st.selectbox("Assessment", list(names))
    assessment = names[selected]

    recommendation = st.text_input(
        "Recommendation",
        "Review the highest-impact delivery bottleneck with the project owner.",
    )
    decision = st.selectbox("Manager decision", ["accepted", "modified", "rejected"])
    reason = st.text_area("Decision note", "")

    if st.button("Save intervention"):
        record = service.record_intervention(
            assessment_id=assessment["assessment_id"],
            recommendation=recommendation,
            decision=decision,
            risk_before=assessment["risk_score"],
            decision_reason=reason or None,
        )
        st.success(f"Intervention recorded: {record['intervention_id']}")

    history = service.store.list_interventions()
    if history:
        st.subheader("Recorded interventions")
        st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)


def digest_page(demo_mode: bool):
    st.title("Weekly Risk Digest")
    current = demo_assessments() if demo_mode else service.store.list_assessments()
    if not current:
        st.info("No assessments are available for a digest yet.")
        return

    if demo_mode:
        previous = []
        for item in current:
            row = dict(item)
            row["risk_score"] = float(item["risk_score"]) - float(item.get("risk_change", 0))
            previous.append(row)
    else:
        grouped = {}
        for item in current:
            grouped.setdefault(item["project_id"], []).append(item)
        previous = []
        latest = []
        for items in grouped.values():
            ordered = sorted(items, key=lambda x: x["created_at"])
            latest.append(ordered[-1])
            if len(ordered) > 1:
                previous.append(ordered[-2])
        current = latest

    digest = build_weekly_digest(previous, current)
    c1, c2 = st.columns(2)
    c1.metric("Projects reviewed", digest["project_count"])
    c2.metric("Need attention", digest["attention_count"])

    st.subheader("Worsening")
    if digest["worsening"]:
        st.dataframe(pd.DataFrame(digest["worsening"]), use_container_width=True, hide_index=True)
    else:
        st.caption("No worsening projects in the comparison window.")

    st.subheader("Improving")
    if digest["improving"]:
        st.dataframe(pd.DataFrame(digest["improving"]), use_container_width=True, hide_index=True)
    else:
        st.caption("No improving projects in the comparison window.")

    if digest["new"]:
        st.subheader("New")
        st.dataframe(pd.DataFrame(digest["new"]), use_container_width=True, hide_index=True)


def repository_page():
    st.title("Repository Explorer")
    st.write(
        "Inspect current public GitHub milestone evidence directly. "
        "This view does not claim historical risk unless the validated model pipeline is available."
    )

    repo = st.text_input("Public GitHub repository", "pytorch/pytorch")
    if st.button("Load milestones"):
        try:
            st.session_state["repo_milestones"] = list_due_milestones(repo)
            st.session_state["repo_name"] = repo
        except Exception as exc:
            st.error(f"GitHub data could not be loaded: {exc}")

    milestones = st.session_state.get("repo_milestones", [])
    if milestones:
        options = {
            f"#{m['number']} · {m['title']} · {m['due_on']}": m["number"]
            for m in milestones
        }
        selected = st.selectbox("Milestone", list(options))
        selected_number = options[selected]
        col_a, col_b = st.columns(2)
        with col_a:
            inspect_clicked = st.button("Inspect evidence")
        with col_b:
            assess_clicked = st.button("Assess with Risk Copilot", disabled=not service.model_available)

        if inspect_clicked:
            try:
                result = inspect_milestone(
                    st.session_state.get("repo_name", repo),
                    selected_number,
                )
                st.subheader(result["milestone"]["title"] or "Delivery target")
                c1, c2, c3 = st.columns(3)
                c1.metric("Items", result["summary"]["items"])
                c2.metric("Issues", result["summary"]["issues"])
                c3.metric("Pull requests", result["summary"]["pull_requests"])
                st.caption(result["note"])
                for item in result["evidence"][:50]:
                    with st.expander(f"{item['evidence_id']} · {item['title']}"):
                        st.write(item["text"] or "No body text available.")
                        if item["url"]:
                            st.link_button("Open on GitHub", item["url"])
            except Exception as exc:
                st.error(f"Repository evidence could not be loaded: {exc}")

        if assess_clicked:
            try:
                assessment = service.assess_github_milestone(
                    repo=st.session_state.get("repo_name", repo),
                    milestone_number=selected_number,
                )
                st.success("Assessment completed and saved.")
                a1, a2, a3 = st.columns(3)
                a1.metric("Risk score", f"{assessment['risk_score']:.1f}/100")
                a2.metric("Risk band", badge(assessment["risk_band"]))
                a3.metric("Narrative confidence", str(assessment.get("narrative_confidence") or "N/A").title())
                st.subheader("Verified drivers")
                if assessment.get("drivers"):
                    for driver in assessment["drivers"]:
                        st.write(f"**{driver.get('claim', driver.get('feature', 'Driver'))}**")
                        for citation in driver.get("citations", []):
                            st.code(citation.get("quote", ""), language=None)
                else:
                    st.caption("No verified drivers were produced; Risk Copilot abstained.")
                if assessment.get("mitigations"):
                    st.subheader("Suggested mitigations")
                    for mitigation in assessment["mitigations"]:
                        st.write(f"- {mitigation}")
            except Exception as exc:
                st.error(f"Risk assessment could not be completed: {exc}")

        if not service.model_available:
            st.caption("Risk assessment is disabled until the research model artifact has been generated by the validation workflow.")


def trust_page():
    st.title("AI Trust Center")
    trust = service.trust_center()

    model = trust["predictive_model"]
    st.subheader("Predictive model")
    if model["status"] == "not_validated":
        st.warning("No validated production model report is available yet.")
    status = model.get("deployment_status") or model.get("status") or "unknown"
    approved = bool(model.get("production_approved"))
    st.caption(f"Model deployment status: {status} · Production approved: {'Yes' if approved else 'No'}")
    if model.get("limitations"):
        with st.expander("Model limitations"):
            for limitation in model["limitations"]:
                st.write(f"- {limitation}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Macro F1", "Not measured" if model["macro_f1"] is None else f"{model['macro_f1']:.3f}")
    c2.metric("Mean Brier", "Not measured" if model["mean_brier"] is None else f"{model['mean_brier']:.3f}")
    c3.metric(
        "Lift vs baseline",
        "Not measured" if model["lift_vs_baseline"] is None else f"{model['lift_vs_baseline']:+.3f}",
    )

    st.subheader("Security checks")
    security = trust["security"]
    c1, c2 = st.columns(2)
    c1.metric("Checks passed", f"{security['checks_passed']}/{security['checks_total']}")
    c2.metric("All passed", "Yes" if security["all_passed"] else "No")

    st.subheader("Human feedback")
    feedback = trust["human_feedback"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Agree", feedback["agree"])
    c2.metric("Disagree", feedback["disagree"])
    c3.metric("Total", feedback["total"])

    st.caption(
        "Risk Copilot does not display target thresholds as achieved results. "
        "Metrics appear here only after the corresponding evaluation has actually run."
    )


st.sidebar.title("Risk Copilot")
demo_mode = st.sidebar.toggle("Demo mode", value=not service.model_available)
if not service.model_available:
    st.sidebar.caption("Validated model unavailable — demo mode is recommended.")

page = st.sidebar.radio(
    "Workspace",
    [
        "Portfolio",
        "Project Intelligence",
        "Weekly Risk Digest",
        "Repository Explorer",
        "New Assessment",
        "Decision Lab",
        "Intervention Memory",
        "AI Trust Center",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Read-only AI decision support. Human approval remains required.")

if page == "Portfolio":
    portfolio_page(demo_mode)
elif page == "Project Intelligence":
    project_page(demo_mode)
elif page == "Weekly Risk Digest":
    digest_page(demo_mode)
elif page == "Repository Explorer":
    repository_page()
elif page == "New Assessment":
    assessment_page()
elif page == "Decision Lab":
    decision_lab_page()
elif page == "Intervention Memory":
    interventions_page(demo_mode)
elif page == "AI Trust Center":
    trust_page()
