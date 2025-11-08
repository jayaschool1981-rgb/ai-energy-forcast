# ⚡ AI-Powered Energy Consumption Forecasting

This is a full-stack AI project that predicts **hourly electricity usage (kWh)** using a trained **MLP Machine Learning model**.  
It includes: Data → Training → Model Export → FastAPI Backend → React Frontend.

### Why this project?
Electricity usage is seasonal + time-based. Most buildings waste power because they don’t forecast demand.  
This project solves that by predicting *future* consumption from **timestamp + temperature**.

---

## 📦 Tech Stack

| Layer | Tech |
|---|---|
| Model | Scikit-learn MLPRegressor |
| Serving | FastAPI |
| UI | React + Vite |
| Data | Mock dataset with hourly seasonality & temperature effect |

---

## 🚀 Getting Started (Local)

### 1) Backend

```bash
# activate venv
.\.venv\Scripts\activate

# run API
uvicorn api.main:app --reload --port 8000
