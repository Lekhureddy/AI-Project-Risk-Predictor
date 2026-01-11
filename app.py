import streamlit as st
import pandas as pd
import pickle


def recommend_action(score):
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

    # Add missing expected columns as 0
    for col in required_features:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    # Keep only required columns in correct order
    X = df_encoded[required_features]

    # Predict
    preds = model.predict(X)

    # Risk score (if available)
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        risk_scores = (proba.max(axis=1) * 100).round(2)
    else:
        risk_scores = ["N/A"] * len(df)

    # Build output
    output = df.copy()
    output["Predicted Outcome"] = preds
    output["Risk Score"] = risk_scores
    output["Recommended Actions"] = output["Risk Score"].apply(recommend_action)

    st.subheader("📊 Prediction Results")

    # Show summary table
    st.dataframe(
        output[["Predicted Outcome", "Risk Score", "Recommended Actions"]],
        use_container_width=True
    )

    # Download button (MUST be inside the if block)
    csv = output.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download results as CSV",
        data=csv,
        file_name="project_risk_predictions.csv",
        mime="text/csv"
    )

    # Full table expander (also inside the if block)
    with st.expander("See full output table"):
        st.dataframe(output, use_container_width=True)

else:
    st.info("Please upload a CSV file to get predictions.")
