# 🚀 AI-Powered Project Risk Predictor

A deployed **machine learning web application** that predicts **project outcomes**, **risk scores**, and **recommended actions** using historical project performance data.

This project demonstrates an **end-to-end AI system** integrated with **Agile project management using Jira Cloud**.

---

## 🌐 Live Application

🔗 **Streamlit App**  
https://ai-project-risk-predictor-jhb6k9onjkann7g5ugpq.streamlit.app

---

## 📌 Problem Statement

Project managers often identify risks only after delays or failures occur.  
Analyzing multiple project metrics manually is inefficient and error-prone.

This project uses **machine learning** to:
- Predict project outcomes early
- Quantify risk using a score
- Recommend mitigation actions proactively

---

## 🎯 Solution Overview

Users upload a CSV file containing project performance metrics and receive:

- **Predicted Outcome**
  - On Track
  - Delayed
  - Critical
- **Risk Score** (0–100)
- **Risk Band** (Low / Medium / High)
- **Recommended Actions** for mitigation

The application runs entirely in the browser using Streamlit.

---

## 🧠 Machine Learning Model

- **Algorithm**: Random Forest Classifier
- **Input**: Project performance metrics
- **Output**: Project outcome classification
- **Risk Score**: Derived from prediction probabilities

The trained model is stored as:

