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

    required_features = list(model.feature_names_in_)

missing = [c for c in required_features if c not in df.columns]
extra = [c for c in df.columns if c not in required_features]

if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

X = df[required_features]
preds = model.predict(X)

