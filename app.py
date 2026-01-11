import streamlit as st
import pandas as pd
import pickle

# -----------------------------
# Helper functions
# -----------------------------
def risk_band(score: float) -> str:
    if pd.isna(score):
        return "N/A"
    if score >= 80:
        return "High"
    elif score >= 60:
        return "Medium"
    else:
        return "Low"


def recommend_action(score: float) -> str:
    if pd.isna(score):
        return "No risk score available"
    if score >= 80:
        return "High risk: add buffer, reduce scope, assign senior resources"
    elif score >= 60:
        return "Medium risk: monitor closely, improve planning"
    else:
        return "Low risk: no immediate action required"


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="AI Project Risk Predictor", layout="wide")
st.title("🚀 AI-Powered Project Performance Predictor")
st.write("Upload a CSV file and get predicted outcome + risk score + recommended action.")

with st.expander("✅ How to use this app"):
    st.markdown(
        """
        1. Upload a CSV file (same format used for training).
        2. The app predicts **Outcome**, **Risk Score**, and **Recommended Actions**.
        3. Use filters on the left to narrow results.
        4. Download filtered or full results as CSV.
        """
    )

uploaded_file = st.file_uploader("Upload Project CSV", type=["csv"])

# Stop here if no file
if uploaded_file is None:
    st.info("Please upload a CSV file to get predictions.")
    st.stop()

# -----------------------------
# Read data
# -----------------------------
df = pd.read_csv(uploaded_file)

# -----------------------------
# Load model
# -----------------------------
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# Model expected features
# (This exists for sklearn models trained with DataFrame)
required_features = list(model.feature_names_in_)

# -----------------------------
# Prepare X using one-hot encoding
# -----------------------------
df_encoded = pd.get_dummies(df)

# Add missing columns
for col in required_features:
    if col not in df_encoded.columns:
        df_encoded[col] = 0

# Keep only required columns in correct order
X = df_encoded[required_features]

# -----------------------------
# Predict
# -----------------------------
preds = model.predict(X)

# Risk Score (probability-based)
risk_scores = None
if hasattr(model, "predict_proba"):
    proba = model.predict_proba(X)
    risk_scores = (proba.max(axis=1) * 100).round(2)
else:
    risk_scores = pd.Series([pd.NA] * len(df))

# -----------------------------
# Build output
# -----------------------------
output = df.copy()
output["Predicted Outcome"] = preds
output["Risk Score"] = risk_scores
output["Risk Band"] = output["Risk Score"].apply(risk_band)
output["Recommended Actions"] = output["Risk Score"].apply(recommend_action)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

all_outcomes = sorted(output["Predicted Outcome"].astype(str).unique().tolist())
selected_outcomes = st.sidebar.multiselect(
    "Predicted Outcome",
    options=all_outcomes,
    default=all_outcomes
)

all_bands = ["Low", "Medium", "High"]
selected_bands = st.sidebar.multiselect(
    "Risk Band",
    options=all_bands,
    default=all_bands
)

filtered = output[
    (output["Predicted Outcome"].astype(str).isin(selected_outcomes)) &
    (output["Risk Band"].isin(selected_bands))
].copy()

# -----------------------------
# Summary metrics
# -----------------------------
st.subheader("📊 Summary")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Projects", len(output))
c2.metric("Shown After Filters", len(filtered))
c3.metric("Critical Count", int((filtered["Predicted Outcome"].astype(str) == "Critical").sum()))
c4.metric("Avg Risk Score", round(pd.to_numeric(filtered["Risk Score"], errors="coerce").mean(), 2))

# -----------------------------
# Results Table (Filtered)
# -----------------------------
st.subheader("📌 Prediction Results (Filtered View)")
st.dataframe(
    filtered[["Predicted Outcome", "Risk Score", "Risk Band", "Recommended Actions"]],
    use_container_width=True
)

# -----------------------------
# Download buttons
# -----------------------------
st.subheader("⬇️ Downloads")

col1, col2 = st.columns(2)

with col1:
    csv_filtered = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download FILTERED results CSV",
        data=csv_filtered,
        file_name="project_risk_predictions_filtered.csv",
        mime="text/csv"
    )

with col2:
    csv_full = output.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download FULL results CSV",
        data=csv_full,
        file_name="project_risk_predictions_full.csv",
        mime="text/csv"
    )

# -----------------------------
# Full table (optional)
# -----------------------------
with st.expander("See full output table"):
    st.dataframe(output, use_container_width=True)
