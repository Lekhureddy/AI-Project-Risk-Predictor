# 🚀 AI-Powered Project Risk Predictor

A deployed machine learning application that predicts **project outcomes**, **risk scores**, and **recommended actions** using historical project data.

🔗 **Live App**:  
[https://ai-project-risk-predictor-jhb6k9onjkann7g5ugpq.streamlit.app](https://ai-project-risk-predictor-jhb6k9onjkannf7g5ugpqj.streamlit.app/)

---

## 📌 Problem Statement
Project managers often struggle to proactively identify projects at risk of delay or failure. This tool uses machine learning to predict project performance and provide actionable recommendations before issues escalate.

---

## 🎯 Solution Overview
This application allows users to upload a CSV file containing project metrics and receive:
- Predicted project outcome (On Track / Delayed / Critical)
- Risk score (0–100)
- Risk band (Low / Medium / High)
- Recommended actions for mitigation

The solution is fully deployed and accessible via a web interface.

---

## 🧠 Machine Learning Model
- Algorithm: **Random Forest Classifier**
- Input: Project performance metrics
- Output: Project outcome classification
- Risk score derived from prediction probabilities

The model is stored as `model.pkl` and loaded at runtime.

---

## 🛠️ Tech Stack
- Python
- Pandas, NumPy
- Scikit-learn
- Streamlit
- GitHub
- Streamlit Cloud (Deployment)

---

## 📂 Project Structure

