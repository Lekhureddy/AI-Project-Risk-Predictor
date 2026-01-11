import streamlit as st
import pandas as pd
import pickle

def recommend_action(row):
    score = row.get("Risk Score", 0)

    if score == "N/A":
        return "No risk score available"

    if score >= 80:
        return "High risk: add buffer, reduce scope, assign senior resources"
    elif score >= 60:
        return "Medium risk: monitor closely, improve planning"
    else:
        return "Low risk: no immediate action required"

st.set_page_config(page_title="AI Project Risk Predictor", layout="wide")
st.title("🚀 AI-Powered Project Performance Predictor")

uploaded_file = st.file_uploader("Upload Project CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Load model
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)

    # Model expected feature columns (from training)
    required_features = list(model.feature_names_in_)

    # One-hot encode uploaded data
    df_encoded = pd.get_dummies(df)

    # Add any missing expected columns as 0
    for col in required_features:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    # Keep only required columns in the correct order
    X = df_encoded[required_features]

    # Predict
    preds = model.predict(X)

    # Risk score from probability (if available)
    risk_score = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        risk_score = (proba.max(axis=1) * 100).round(2)

    # Build output table ONCE (do not overwrite it later)
    output = df.copy()
    output["Predicted Outcome"] = preds
    if risk_score is not None:
        output["Risk Score"] = risk_score
    else:
        output["Risk Score"] = "N/A"

    st.subheader("📊 Prediction Results")

    # Show only key columns (this is where you add your dataframe line)
    st.dataframe(output[["Predicted Outcome", "Risk Score"]], use_container_width=True)

    # Optional: show full output also
    with st.expander("See full output table"):
        st.dataframe(output, use_container_width=True)

else:
    st.info("Please upload a CSV file to get predictions.")
