import streamlit as st
import pandas as pd
import pickle


# ---------- Helper: Recommended action ----------
def recommend_action(score):
    if pd.isna(score):
        return "No risk score available"

    if score >= 80:
        return "High risk: add buffer, reduce scope, assign senior resources"
    elif score >= 60:
        return "Medium risk: monitor closely, improve planning"
    else:
        return "Low risk: no immediate action required"


# ---------- Page config ----------
st.set_page_config(page_title="AI Project Risk Predictor", layout="wide")
st.title("🚀 AI-Powered Project Performance Predictor")
st.write("Upload a CSV file and get predicted outcome + risk score + recommended action.")

uploaded_file = st.file_uploader("Upload Project CSV", type=["csv"])


# ---------- Main app ----------
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if df.empty:
        st.error("Uploaded CSV is empty.")
        st.stop()

    # Load model
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)

    # Model expected feature columns
    required_features = list(model.feature_names_in_)

    # One-hot encode uploaded data
    df_encoded = pd.get_dummies(df)

    # Add missing expected columns as 0
    for col in required_features:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    # Keep only required columns in correct order
    X = df_encoded[required_features]

    # Predict
    preds = model.predict(X)

    # Risk score from probability
    risk_score = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        risk_score = (proba.max(axis=1) * 100).round(2)

    # Build output
    output = df.copy()
    output["Predicted Outcome"] = preds

    if risk_score is not None:
        output["Risk Score"] = risk_score
    else:
        output["Risk Score"] = pd.NA

    # Risk Band
    output["Risk Band"] = pd.cut(
        pd.to_numeric(output["Risk Score"], errors="coerce"),
        bins=[-1, 59.99, 79.99, 100],
        labels=["Low", "Medium", "High"]
    )

    # Recommended actions
    output["Recommended Actions"] = output["Risk Score"].apply(
        lambda x: recommend_action(pd.to_numeric(x, errors="coerce"))
    )

    # ---------- Sidebar filters ----------
    st.sidebar.header("Filters")

    outcomes = sorted(output["Predicted Outcome"].dropna().unique())
    selected_outcomes = st.sidebar.multiselect(
        "Predicted Outcome",
        options=outcomes,
        default=outcomes
    )

    bands = ["Low", "Medium", "High"]
    selected_bands = st.sidebar.multiselect(
        "Risk Band",
        options=bands,
        default=bands
    )

    filtered = output[
        (output["Predicted Outcome"].isin(selected_outcomes)) &
        (output["Risk Band"].isin(selected_bands))
    ]

    # ---------- Metrics ----------
    st.subheader("📊 Summary")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Projects", len(output))
    c2.metric("Shown After Filters", len(filtered))
    c3.metric("Critical Count", int((output["Predicted Outcome"] == "Critical").sum()))
    c4.metric(
        "Avg Risk Score",
        float(pd.to_numeric(output["Risk Score"], errors="coerce").mean().round(2))
        if output["Risk Score"].notna().any() else 0.0
    )

    # ---------- Main Results Table ----------
    st.subheader("📌 Prediction Results (Filtered View)")
    st.dataframe(
        filtered[["Predicted Outcome", "Risk Score", "Risk Band", "Recommended Actions"]],
        use_container_width=True
    )

    # ---------- Charts ----------
    st.subheader("📈 Insights")
    colA, colB = st.columns(2)

    with colA:
        st.write("Outcome count")
        st.bar_chart(output["Predicted Outcome"].value_counts())

    with colB:
        st.write("Risk Band count")
        st.bar_chart(output["Risk Band"].value_counts())

    # ---------- Download button ----------
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered results as CSV",
        data=csv,
        file_name="project_risk_predictions.csv",
        mime="text/csv"
    )

    # ---------- Full table expander ----------
    with st.expander("See full output table"):
        st.dataframe(output, use_container_width=True)

else:
    st.info("Please upload a CSV file to get predictions.")
