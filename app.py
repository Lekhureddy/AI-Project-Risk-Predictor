import streamlit as st
import pandas as pd
import pickle

st.set_page_config(page_title="AI Project Risk Predictor", layout="wide")

st.title("🚀 AI-Powered Project Performance Predictor")

uploaded_file = st.file_uploader("Upload Project CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    with open("model.pkl", "rb") as f:
        model = pickle.load(f)

    X = df.select_dtypes(include="number")
    preds = model.predict(X)
    risk_scores = model.predict_proba(X).max(axis=1) * 100

    df["Predicted Outcome"] = preds
    df["Risk Score"] = risk_scores.round(2)

    st.subheader("📊 Prediction Results")
    st.dataframe(df)
