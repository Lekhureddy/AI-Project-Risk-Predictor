import streamlit as st
import pandas as pd
import pickle

st.set_page_config(page_title="AI Project Risk Predictor", layout="wide")
st.title("🚀 AI-Powered Project Performance Predictor")

uploaded_file = st.file_uploader("Upload Project CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Load model
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)

    # Model expected feature columns
    required_features = list(model.feature_names_in_)

    # One-hot encode uploaded data
    df_encoded = pd.get_dummies(df)

    # Add missing columns as 0
    for col in required_features:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    # Keep only required columns in correct order
    X = df_encoded[required_features]

    # Predict
    preds = model.predict(X)

    # Risk score from probability (if available)
    risk_score = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        risk_score = (proba.max(axis=1) * 100).round(2)

    # Output
    output = df.copy()
    output["Predicted Outcome"] = preds
    if risk_score is not None:
        output["Risk Score"] = risk_score

    st.subheader("📊 Prediction Results")
    output = df.copy()

st.subheader("📊 Prediction Results")
st.dataframe(
    output[["Predicted Outcome", "Risk Score"]]
)

else:
    st.info("Please upload a CSV file to get predictions.")
