import streamlit as st
import pandas as pd
import pickle

if uploaded_file:
    df = pd.read_csv(uploaded_file)

# Load model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# These are the exact columns the model expects
required_features = list(model.feature_names_in_)

# 1) One-hot encode uploaded data (same as training)
df_encoded = pd.get_dummies(df)

# 2) Add any missing columns (set them to 0)
for col in required_features:
    if col not in df_encoded.columns:
        df_encoded[col] = 0

# 3) Keep ONLY the required columns in the same order
X = df_encoded[required_features]

# 4) Predict
preds = model.predict(X)

# If your model supports probabilities for risk score
if hasattr(model, "predict_proba"):
    proba = model.predict_proba(X)
    risk_score = (proba.max(axis=1) * 100).round(2)
else:
    risk_score = None

# Output
df_out = df.copy()
df_out["Predicted Outcome"] = preds
if risk_score is not None:
    df_out["Risk Score"] = risk_score

st.subheader("📊 Prediction Results")
st.dataframe(df_out)


