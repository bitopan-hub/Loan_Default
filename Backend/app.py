from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import shap
import numba
import mysql.connector
from mysql.connector import Error
from preprocessing import preprocess_data
from xai import build_explanations, build_xai_response
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # In production, use an environment variable
CORS(app) # Enable CORS for all routes

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            # Token usually comes as "Bearer <token>"
            if token.startswith('Bearer '):
                token = token.split(" ")[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # You could add user lookup here if needed
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        return f(*args, **kwargs)
    return decorated

# Database Configuration (Using placeholders per request)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Bito@2004', # replace with actual password
    'database': 'loan_default_db'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return None

import json

# Load bundle
try:
    config = joblib.load("loan_model_bundle.pkl")
    model = config["bestModel"]
    threshold = config["threshold"]
    train_stats = config["train_stats"]
    features = config["features"]
    
    # Initialize SHAP explainer (once)
    explainer = shap.TreeExplainer(model)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    explainer = None

# Load feature ranges
try:
    with open("feature_ranges.json", "r") as f:
        feature_ranges = json.load(f)
except Exception as e:
    print(f"Error loading feature ranges: {e}")
    feature_ranges = None

def get_risk_level(prob):
    if prob >= 0.7:
        return "High"
    elif prob >= 0.3:
        return "Medium"
    else:
        return "Low"

def get_decision(risk):
    if risk == "High":
        return "Reject"
    elif risk == "Medium":
        return "Review"
    else:
        return "Approve"

@app.route("/api/customers", methods=["GET"])
@token_required
def get_customers():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, PAN, dob, occupation, period_of_service FROM customers")
        customers = cursor.fetchall()
        return jsonify(customers)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()

@app.route("/api/customers", methods=["POST"])
@token_required
def add_customer():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        data = request.json
        fields = [
            'name', 'dob', 'occupation', 'period_of_service', 
            'RevolvingUtilizationOfUnsecuredLines', 'age', 
            'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 
            'MonthlyIncome', 'NumberOfOpenCreditLinesAndLoans', 
            'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines', 
            'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents'
        ]
        values = [data.get(field) for field in fields]
        
        placeholders = ', '.join(['%s'] * len(fields))
        columns = ', '.join([f'`{f}`' if '-' in f else f for f in fields])
        
        cursor = conn.cursor()
        query = f"INSERT INTO customers ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()
        return jsonify({"message": "Customer added successfully", "id": cursor.lastrowid}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()

@app.route("/api/customers/<int:customer_id>", methods=["PUT"])
@token_required
def update_customer(customer_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        data = request.json
        fields = [
            'name', 'dob', 'occupation', 'period_of_service', 
            'RevolvingUtilizationOfUnsecuredLines', 'age', 
            'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 
            'MonthlyIncome', 'NumberOfOpenCreditLinesAndLoans', 
            'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines', 
            'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents'
        ]
        
        update_parts = []
        values = []
        for field in fields:
            if field in data:
                col_name = f'`{field}`' if '-' in field else field
                update_parts.append(f"{col_name} = %s")
                values.append(data.get(field))
        
        if not update_parts:
            return jsonify({"message": "No fields to update"}), 400
            
        values.append(customer_id)
        query = f"UPDATE customers SET {', '.join(update_parts)} WHERE id = %s"
        
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        return jsonify({"message": "Customer updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()

@app.route("/api/customers/<int:customer_id>", methods=["DELETE"])
@token_required
def delete_customer(customer_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify({"message": "Customer deleted successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()

@app.route("/api/customers/<int:customer_id>", methods=["GET"])
@token_required
def get_customer_details(customer_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
        customer = cursor.fetchone()
        if customer:
            return jsonify(customer)
        return jsonify({"error": "Customer not found"}), 404
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()

@app.route("/predict", methods=["POST"])
@token_required
def predict():
    if not model:
        return jsonify({"error": "Model not loaded"}), 500
        
    data = request.json

    # Extract ID
    customer_id = data.get("id", None)
    df = pd.DataFrame([data])

    df = preprocess_data(df, train_stats)

    # Align features
    df = df[features]

    # Probabilty and Prediction
    prob = model.predict_proba(df)[:, 1][0]
    pred = int(prob >= threshold)

    # Risk + decision
    risk_level = get_risk_level(prob)
    decision = get_decision(risk_level)

    shap_values = explainer.shap_values(df)
    explanations = build_explanations(
        shap_values[0],
        df.iloc[0].values,
        features,
        feature_ranges
    )
    xai_output = build_xai_response(explanations)

    # Final response
    return jsonify({
        "id": customer_id,
        "probability": float(prob),
        "prediction": pred,
        "risk_level": risk_level,
        "decision": decision,
        "explanations": xai_output
    })

@app.route("/api/register", methods=["POST"])
def register():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        data = request.json
        full_name = data.get("full_name")
        email = data.get("email")
        phone = data.get("phone")
        username = data.get("username")
        password = data.get("password")
        
        if not all([full_name, email, phone, username, password]):
            return jsonify({"error": "All fields are required"}), 400
            
        cursor = conn.cursor()
        # Check if username or email exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            return jsonify({"error": "Username or email already exists"}), 400
            
        # Insert new user
        cursor.execute(
            "INSERT INTO users (full_name, email, phone, username, password) VALUES (%s, %s, %s, %s, %s)",
            (full_name, email, phone, username, password)
        )
        conn.commit()
        return jsonify({"message": "Account created successfully"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()

@app.route("/api/login", methods=["POST"])
def login():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        if user:
            token = jwt.encode({
                'user_id': user['id'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            return jsonify({
                "message": "Login successful",
                "token": token,
                "user": user
            }), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()

@app.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        data = request.json
        email = data.get("email")
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            # Generate a reset token valid for 1 hour
            reset_token = jwt.encode({
                'reset_password': True,
                'user_id': user['id'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            # In a real application, send this token via email.
            # For this professional mock, we print it and return a success message.
            print(f"\n--- PASSWORD RESET LINK (MOCK EMAIL) ---")
            print(f"To: {email}")
            print(f"Link: http://localhost:3000/reset-password/{reset_token}")
            print(f"----------------------------------------\n")
            
            # Note: Returning token for easy local testing without checking logs
            return jsonify({
                "message": "If that email exists, a reset link has been sent.",
                "resetTokenForTesting": reset_token
            }), 200
        else:
            # Still return success to prevent email enumeration attacks
            return jsonify({"message": "If that email exists, a reset link has been sent."}), 200
            
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()

@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        data = request.json
        token = data.get("token")
        new_password = data.get("password")
        
        if not token or not new_password:
            return jsonify({"error": "Token and new password are required"}), 400
            
        try:
            # Verify token
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            if not payload.get('reset_password'):
                return jsonify({"error": "Invalid token type"}), 400
                
            user_id = payload['user_id']
            
            # Update password
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user_id))
            conn.commit()
            
            return jsonify({"message": "Password has been reset successfully"}), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Reset token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid reset token"}), 401
            
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()

@app.route("/api/analytics", methods=["GET"])
@token_required
def get_analytics():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Total customers
        cursor.execute("SELECT COUNT(*) as total FROM customers")
        total = cursor.fetchone()['total']
        
        # Average income
        cursor.execute("SELECT AVG(MonthlyIncome) as avg_income FROM customers")
        avg_income = cursor.fetchone()['avg_income']
        
        # Occupation breakdown
        cursor.execute("SELECT occupation, COUNT(*) as count FROM customers GROUP BY occupation")
        occupations = cursor.fetchall()
        
        # Age distribution
        cursor.execute("SELECT age, COUNT(*) as count FROM customers GROUP BY age")
        ages = cursor.fetchall()
        
        # Debt ratio stats
        cursor.execute("SELECT AVG(DebtRatio) as avg_debt_ratio FROM customers")
        avg_debt_ratio = cursor.fetchone()['avg_debt_ratio']

        return jsonify({
            "total_customers": total,
            "average_monthly_income": float(avg_income) if avg_income else 0,
            "average_debt_ratio": float(avg_debt_ratio) if avg_debt_ratio else 0,
            "occupation_distribution": occupations,
            "age_distribution": ages
        })
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)