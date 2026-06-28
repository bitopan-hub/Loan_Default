# Loan Default Risk Assessment Platform

An end-to-end web application that assesses the risk of loan defaults using machine learning. It categorizes applicants into risk tiers (High, Medium, Low) to help automate approval workflows.

## 🚀 Features

- **Machine Learning Prediction:** Uses an optimized XGBoost model to accurately identify high-risk loans based on customer features.
- **Explainable AI (XAI):** Integrates SHAP to provide interpretable, transparent insights into model predictions for loan officers.
- **Secure Backend API:** A RESTful API built with Flask, utilizing JWT for authentication and MySQL for data management.
- **Interactive Dashboard:** A dynamic React.js frontend featuring rich data visualizations via Chart.js.

## 🛠️ Tech Stack

### Frontend
- React.js
- Axios
- Chart.js / react-chartjs-2
- React Router DOM

### Backend & Machine Learning
- Python (Flask)
- MySQL (mysql-connector-python)
- PyJWT (Authentication)
- XGBoost, scikit-learn, pandas, numpy
- SHAP (Explainable AI)

## 📁 Project Structure

- `/frontend` - Contains the React user interface and dashboard.
- `/Backend` - Contains the Flask API, machine learning model pipeline, and SQL initialization scripts.

## ⚙️ Getting Started

### Prerequisites
- Node.js & npm
- Python 3.8+
- MySQL Server

### 1. Database Setup
1. Create a MySQL database (e.g., `loan_default_db`).
2. Execute the schema from `Backend/init_db.sql`.
3. Update the database credentials inside `Backend/app.py`.

### 2. Backend Setup
```bash
cd Backend
pip install -r requirements.txt
python app.py
```
*The Flask server will start on http://localhost:5000*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```
*The React app will open on http://localhost:3000*
