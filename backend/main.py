from flask import Flask, request, jsonify, session, send_from_directory
import os
import threading
import webbrowser
import pandas as pd
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from database import init_database
from models import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    save_prediction,
    get_user_predictions
)
from schemas import validate_signup_data, validate_login_data
from predict import (
    predict_dataframe,
    model_status,
    RAW_COLUMNS
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

app.secret_key = os.environ.get(
    "CHURNGUARD_SECRET_KEY",
    "churnguard-development-secret-key"
)

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

CORS(app, supports_credentials=True)

init_database()


def login_required():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return user_id


def send_page(filename):
    path = os.path.join(FRONTEND_DIR, filename)
    if not os.path.exists(path):
        return jsonify({
            "success": False,
            "message": f"Frontend page not found: {filename}"
        }), 404
    return send_from_directory(FRONTEND_DIR, filename)


@app.route("/", methods=["GET"])
def home():
    return send_page("index.html")


@app.route("/health", methods=["GET"])
def health():
    model = model_status()
    return jsonify({
        "success": True,
        "status": "healthy",
        "service": "ChurnGuard Flask API",
        "database": "available",
        "model": model
    })


@app.route("/login.html")
def login_page():
    return send_page("login.html")


@app.route("/signup.html")
def signup_page():
    return send_page("signup.html")


@app.route("/dashboard.html")
def dashboard_page():
    return send_page("dashboard.html")


@app.route("/prediction.html")
def prediction_page():
    return send_page("prediction.html")


@app.route("/history.html")
def history_page():
    return send_page("history.html")


@app.route("/monitoring.html")
def monitoring_page():
    return send_page("monitoring.html")


@app.route("/report.html")
def report_page():
    return send_page("report.html")


@app.route("/reports.html")
def reports_page():
    return send_page("reports.html")


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    valid, message = validate_signup_data(data)
    if not valid:
        return jsonify({
            "success": False,
            "message": message
        }), 400

    username = str(data["username"]).strip()
    email = str(data["email"]).strip().lower()
    password = str(data["password"])

    if get_user_by_email(email):
        return jsonify({
            "success": False,
            "message": "Email already registered"
        }), 409

    user_id = create_user(
        username,
        email,
        generate_password_hash(password)
    )

    if user_id is None:
        return jsonify({
            "success": False,
            "message": "Unable to create account. Username or email may already exist."
        }), 409

    return jsonify({
        "success": True,
        "message": "Account created successfully",
        "user_id": user_id
    }), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    valid, message = validate_login_data(data)
    if not valid:
        return jsonify({
            "success": False,
            "message": message
        }), 400

    email = str(data["email"]).strip().lower()
    password = str(data["password"])

    user = get_user_by_email(email)

    if not user or not check_password_hash(
        user["password"], password
    ):
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    session.clear()
    session["user_id"] = user["id"]

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    })


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })


@app.route("/me", methods=["GET"])
def current_user():
    user_id = login_required()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Not logged in"
        }), 401

    user = get_user_by_id(user_id)

    if not user:
        session.clear()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    })


@app.route("/model-info", methods=["GET"])
def model_info():
    status = model_status()
    return jsonify({
        "success": True,
        "model": status,
        "expected_features": 30,
        "input_columns": RAW_COLUMNS
    })


@app.route("/predict", methods=["POST"])
def predict():
    user_id = login_required()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please login first"
        }), 401

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "CSV file is required"
        }), 400

    file = request.files["file"]

    if not file or not file.filename:
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400

    if not file.filename.lower().endswith(".csv"):
        return jsonify({
            "success": False,
            "message": "Only CSV files are supported"
        }), 400

    try:
        # Read directly into pandas. No temporary file is needed.
        try:
            df = pd.read_csv(file)
        except UnicodeDecodeError:
            file.stream.seek(0)
            df = pd.read_csv(file, encoding="latin-1")

        # Normalize headers before reporting missing columns.
        df.columns = [
            str(c).replace("\ufeff", "").strip()
            for c in df.columns
        ]

        if df.empty:
            return jsonify({
                "success": False,
                "message": "The uploaded CSV contains no rows."
            }), 400

        if len(df) > 5000:
            return jsonify({
                "success": False,
                "message": "Maximum 5000 customer rows are allowed per upload."
            }), 400

        # Helpful diagnostics for the frontend.
        missing = [c for c in RAW_COLUMNS if c not in df.columns]

        if missing:
            return jsonify({
                "success": False,
                "message": (
                    "This CSV is not a ChurnGuard customer CSV. "
                    "Required customer columns are missing."
                ),
                "missing_columns": missing,
                "received_columns": list(df.columns)
            }), 400

        results = predict_dataframe(df)

        if results.empty:
            return jsonify({
                "success": False,
                "message": "The model returned no predictions."
            }), 500

        # Save only after the entire prediction succeeds.
        for row in results.to_dict(orient="records"):
            save_prediction(
                user_id=user_id,
                customer_id=str(row["customerID"]),
                prediction=str(row["Predicted_Churn"]),
                probability=float(row["Churn_Probability"])
            )

        records = results.to_dict(orient="records")

        high = sum(r["Risk_Level"] == "High" for r in records)
        medium = sum(r["Risk_Level"] == "Medium" for r in records)
        low = sum(r["Risk_Level"] == "Low" for r in records)
        avg = (
            sum(float(r["Churn_Probability"]) for r in records)
            / len(records)
        )

        return jsonify({
            "success": True,
            "message": "Prediction completed successfully",
            "total_records": len(records),
            "summary": {
                "high": high,
                "medium": medium,
                "low": low,
                "average_risk": round(avg, 2)
            },
            "predictions": records
        })

    except Exception as error:
        app.logger.exception("Prediction failed")
        return jsonify({
            "success": False,
            "message": "Prediction failed.",
            "error": str(error)
        }), 500


@app.route("/predictions", methods=["GET"])
def prediction_history():
    user_id = login_required()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please login first"
        }), 401

    predictions = get_user_predictions(user_id)

    records = []

    for p in predictions:
        probability = float(p["probability"] or 0)

        if probability >= 70:
            risk = "High"
        elif probability >= 40:
            risk = "Medium"
        else:
            risk = "Low"

        records.append({
            "id": p["id"],
            "customerID": p["customer_id"],
            "prediction": p["prediction"],
            "probability": probability,
            "risk": risk,
            "created_at": p["created_at"]
        })

    return jsonify({
        "success": True,
        "count": len(records),
        "predictions": records
    })


@app.route("/dashboard/stats", methods=["GET"])
def dashboard_stats():
    user_id = login_required()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please login first"
        }), 401

    predictions = get_user_predictions(user_id)
    probabilities = [float(p["probability"] or 0) for p in predictions]

    high = sum(p >= 70 for p in probabilities)
    medium = sum(40 <= p < 70 for p in probabilities)
    low = sum(p < 40 for p in probabilities)
    total = len(probabilities)

    return jsonify({
        "success": True,
        "stats": {
            "total": total,
            "high": high,
            "medium": medium,
            "low": low,
            "average_risk": round(
                sum(probabilities) / total, 2
            ) if total else 0
        }
    })


@app.route("/report", methods=["GET"])
def report_data():
    return prediction_history()


@app.route("/monitoring", methods=["GET"])
def monitoring_data():
    user_id = login_required()

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please login first"
        }), 401

    predictions = get_user_predictions(user_id)
    probabilities = [float(p["probability"] or 0) for p in predictions]
    total = len(probabilities)

    high = sum(p >= 70 for p in probabilities)
    medium = sum(40 <= p < 70 for p in probabilities)
    low = sum(p < 40 for p in probabilities)

    return jsonify({
        "success": True,
        "monitoring": {
            "total_predictions": total,
            "high_risk": high,
            "medium_risk": medium,
            "low_risk": low,
            "average_risk": round(
                sum(probabilities) / total, 2
            ) if total else 0,
            "status": "active" if total else "waiting_for_predictions"
        }
    })


@app.errorhandler(413)
def too_large(_error):
    return jsonify({
        "success": False,
        "message": "File is too large. Maximum upload size is 10 MB."
    }), 413


if __name__ == "__main__":
    print("=" * 70)
    print("CHURNGUARD APPLICATION")
    print("=" * 70)
    print("Website: http://127.0.0.1:5000")
    print("Health:  http://127.0.0.1:5000/health")
    print("Model:   ", model_status())
    print("=" * 70)

    def open_browser():
        webbrowser.open("http://127.0.0.1:5000")

    threading.Timer(1.5, open_browser).start()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )
