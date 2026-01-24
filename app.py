import streamlit as st
import pandas as pd
import pickle

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def risk_band(score: float) -> str:
    """Convert numeric risk score into a simple risk band."""
    if pd.isna(score):
        return "N/A"
    if score >= 80:
        return "High"
    if score >= 60:
        return "Medium"
    return "Low"


def recommend_action(score: float) -> str:
    """Return a short, practical recommendation based on the risk score."""
    if pd.isna(score):
        return "Risk score not available"
    if score >= 80:
        return "Escalate: add buffer, reduce scope, and assign senior support"
    if score >= 60:
        return "Hold: monitor closely and revisit plan assumptions"
    return "Go: no immediate action required"


def safe_mean(series: pd.Series):
    val = pd.to_numeric(series, errors="coerce").mean()
    return None if pd.isna(val) else round(float(val), 2)


# ------------------------------------------------------------
# Page setup
# ------------------------------------------------------------
st.set_page_config(page_title="AI Project Risk Predictor", layout="wide")

# ------------------------------------------------------------
# Sidebar: Navigation + Links
# ------------------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Risk Predictor", "Power BI", "Architecture", "DevOps", "Java Decision Layer", "Jira and Workflow"],
)

st.sidebar.divider()
st.sidebar.subheader("Project Links")
st.sidebar.write("Jira board (private):")
st.sidebar.write("https://lekhureddy-122.atlassian.net/jira/software/projects/KAN/boards/1")
st.sidebar.caption(
    "If you are viewing this from the public app, the repository folders mentioned below (powerbi/, "
    "java-risk-service/, docs/) are available in the project GitHub repo."
)

# ------------------------------------------------------------
# PAGE 1: Risk Predictor (Main App)
# ------------------------------------------------------------
if page == "Risk Predictor":
    st.title("AI Project Risk Predictor")
    st.write(
        "Upload a CSV file to generate a predicted outcome, risk score, and recommended action. "
        "This is the main prediction workflow used in the project."
    )

    with st.expander("How to use"):
        st.markdown(
            """
            1. Upload a CSV file (the same format used during training).
            2. The app will generate Predicted Outcome, Risk Score, Risk Band, and a Recommended Action.
            3. Use the filters on the left to narrow the results.
            4. Download either the filtered results or the full output as a CSV.
            """
        )

    uploaded_file = st.file_uploader("Upload project dataset (CSV)", type=["csv"])
    if uploaded_file is None:
        st.info("Upload a CSV file to continue.")
        st.stop()

    # -----------------------------
    # Read data
    # -----------------------------
    df = pd.read_csv(uploaded_file)

    # If user uploads a dataset that already includes the target column, drop it
    if "Outcome" in df.columns:
        df = df.drop(columns=["Outcome"])

    # -----------------------------
    # Load model + feature columns
    # -----------------------------
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)

    with open("feature_columns.pkl", "rb") as f:
        required_features = pickle.load(f)

    # -----------------------------
    # Encode uploaded data to match training
    # Training used: pd.get_dummies(..., drop_first=True) + fillna
    # -----------------------------
    df_encoded = pd.get_dummies(df, drop_first=True)

    # Fill missing numeric values (median), then fill any remaining missing values with 0
    num_cols = df_encoded.select_dtypes(include="number").columns
    if len(num_cols) > 0:
        df_encoded[num_cols] = df_encoded[num_cols].fillna(df_encoded[num_cols].median())
    df_encoded = df_encoded.fillna(0)

    # Add missing columns that training had
    for col in required_features:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    # Keep ONLY training columns in the same order
    X = df_encoded[required_features]

    # -----------------------------
    # Predict
    # -----------------------------
    preds = model.predict(X)

    # Risk score from probabilities (if available)
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        risk_scores = (proba.max(axis=1) * 100).round(2)
    else:
        risk_scores = pd.Series([pd.NA] * len(df))

    # -----------------------------
    # Output table
    # -----------------------------
    output = df.copy()
    output["Predicted Outcome"] = preds
    output["Risk Score"] = risk_scores
    output["Risk Band"] = output["Risk Score"].apply(risk_band)
    output["Recommended Action"] = output["Risk Score"].apply(recommend_action)

    # -----------------------------
    # Sidebar filters (only on main page)
    # -----------------------------
    st.sidebar.divider()
    st.sidebar.subheader("Filters (Risk Predictor)")

    all_outcomes = sorted(output["Predicted Outcome"].astype(str).unique().tolist())
    selected_outcomes = st.sidebar.multiselect(
        "Predicted Outcome",
        options=all_outcomes,
        default=all_outcomes,
    )

    all_bands = ["Low", "Medium", "High"]
    selected_bands = st.sidebar.multiselect(
        "Risk Band",
        options=all_bands,
        default=all_bands,
    )

    filtered = output[
        (output["Predicted Outcome"].astype(str).isin(selected_outcomes))
        & (output["Risk Band"].isin(selected_bands))
    ].copy()

    # -----------------------------
    # Summary
    # -----------------------------
    st.subheader("Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records", len(output))
    c2.metric("Shown After Filters", len(filtered))
    c3.metric("Critical Count", int((filtered["Predicted Outcome"].astype(str) == "Critical").sum()))
    avg_risk = safe_mean(filtered["Risk Score"])
    c4.metric("Average Risk Score", avg_risk if avg_risk is not None else "N/A")

    # -----------------------------
    # Results
    # -----------------------------
    st.subheader("Prediction Results")
    st.dataframe(
        filtered[["Predicted Outcome", "Risk Score", "Risk Band", "Recommended Action"]],
        use_container_width=True,
    )

    # -----------------------------
    # Downloads
    # -----------------------------
    st.subheader("Download Results")
    col1, col2 = st.columns(2)

    with col1:
        csv_filtered = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download filtered CSV",
            data=csv_filtered,
            file_name="project_risk_predictions_filtered.csv",
            mime="text/csv",
        )

    with col2:
        csv_full = output.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download full CSV",
            data=csv_full,
            file_name="project_risk_predictions_full.csv",
            mime="text/csv",
        )

    with st.expander("View full output table"):
        st.dataframe(output, use_container_width=True)

    with st.expander("Notes about the output"):
        st.markdown(
            """
            - Predicted Outcome is the model output (classification).
            - Risk Score is derived from prediction confidence (when `predict_proba` is available).
            - Recommended Action is a simple, readable suggestion based on the risk score.
            """
        )

# ------------------------------------------------------------
# PAGE 2: Power BI
# ------------------------------------------------------------
elif page == "Power BI":
    st.title("Power BI Dashboard")
    st.write(
        "This project includes a Power BI dashboard created from the prediction output. "
        "The goal is to make results easy to review for non-technical stakeholders."
    )

    st.subheader("What the dashboard shows")
    st.markdown(
        """
        - Overall risk distribution and predicted outcome summary
        - Decision breakdown (GO / HOLD / ESCALATE)
        - Risk score comparisons
        - Detailed table view for drill-down and review
        """
    )

    st.subheader("Where to find it in the repository")
    st.markdown(
        """
        - Folder: `powerbi/`
        - Screenshots: `powerbi/dashboard_screenshots/`
        - Dashboard file: `.pbix` (if included in the repo)
        """
    )

    st.subheader("How to use with this app")
    st.markdown(
        """
        - Use the Risk Predictor page to download output CSV files.
        - Load the output file into Power BI to refresh visuals.
        - Use the Overview page for quick monitoring and the Details page for drill-down.
        """
    )

# ------------------------------------------------------------
# PAGE 3: Architecture
# ------------------------------------------------------------
elif page == "Architecture":
    st.title("System Architecture and Networking")
    st.write(
        "The current implementation is intentionally simple and practical. "
        "It runs as a single Streamlit application where preprocessing and inference happen on the server."
    )

    st.subheader("High-level components")
    st.markdown(
        """
        - Client: web browser
        - Server: Streamlit app (Python)
        - Model artifacts: `model.pkl` and `feature_columns.pkl` loaded locally at runtime
        - Output: CSV results for reporting (Power BI)
        """
    )

    st.subheader("Communication flow (current setup)")
    st.markdown(
        """
        - The browser connects to the app over HTTPS when deployed.
        - The app processes the uploaded CSV inside the same runtime environment.
        - No external API calls are required for inference in the current prototype.
        """
    )

    st.subheader("Repository documentation")
    st.markdown(
        """
        If you included an architecture document or diagram in the repo, reference it here:
        - Example: `docs/architecture/architecture_diagram.png`
        - Example: `NETWORKING_SYSTEM_ARCHITECTURE.md`
        """
    )

# ------------------------------------------------------------
# PAGE 4: DevOps
# ------------------------------------------------------------
elif page == "DevOps":
    st.title("DevOps and Deployment")
    st.write(
        "This project includes basic DevOps practices to keep the application reproducible and easy to deploy."
    )

    st.subheader("What is included")
    st.markdown(
        """
        - Docker setup for consistent local runs
        - GitHub Actions workflow for basic CI checks
        - Streamlit Cloud deployment for the live application
        """
    )

    st.subheader("Why this matters")
    st.markdown(
        """
        - Docker helps avoid “works on my machine” issues.
        - CI checks help catch missing dependencies or broken builds early.
        - Streamlit Cloud allows quick sharing and testing without manual deployment steps.
        """
    )

    st.subheader("Repository locations")
    st.markdown(
        """
        - `Dockerfile` (if included)
        - `.github/workflows/` for GitHub Actions
        """
    )

# ------------------------------------------------------------
# PAGE 5: Java Decision Layer
# ------------------------------------------------------------
elif page == "Java Decision Layer":
    st.title("Java Decision Layer")
    st.write(
        "The Java module is a small post-processing step that converts model outputs into clear actions. "
        "This reflects how many teams apply business rules after predictions."
    )

    st.subheader("What it does")
    st.markdown(
        """
        - Reads a CSV that contains at least Predicted Outcome and Risk Score
        - Assigns a decision (GO / HOLD / ESCALATE)
        - Adds a short reason for the decision
        - Writes a clean output CSV for reporting and dashboards
        """
    )

    st.subheader("Where to find it in the repository")
    st.markdown(
        """
        - Folder: `java-risk-service/`
        - README: `java-risk-service/README.md`
        - Example files:
          - `sample_input_predictions.csv`
          - `sample_output_decisions.csv`
        """
    )

# ------------------------------------------------------------
# PAGE 6: Jira and Workflow
# ------------------------------------------------------------
elif page == "Jira and Workflow":
    st.title("Jira and Project Workflow")
    st.write(
        "This project was planned and tracked using Jira to keep work structured and realistic. "
        "The goal was to manage tasks, progress, and risks the way a project team would."
    )

    st.subheader("Jira board")
    st.write("https://lekhureddy-122.atlassian.net/jira/software/projects/KAN/boards/1")
    st.caption(
        "The board is private. This is normal for real project work. If needed, screenshots or a walkthrough can be shared."
    )

    st.subheader("How Jira was used")
    st.markdown(
        """
        - Epics and user stories to organize work
        - Tasks for implementation steps (modeling, app, dashboard, documentation)
        - Status tracking to monitor progress
        - Risk-related tasks to reflect project health and mitigation steps
        """
    )

    st.subheader("Product documentation")
    st.markdown(
        """
        Product-level notes are documented in the repository:
        - `PRODUCT_MANAGEMENT.md`
        """
    )
