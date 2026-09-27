import requests


# ============================================================
# CHURNGUARD API TEST
# ============================================================

BASE_URL = "http://127.0.0.1:5000"

CSV_PATH = "../data/test_customer_data.csv"

EMAIL = "test@example.com"
PASSWORD = "test123"


print("=" * 60)
print("CHURNGUARD API TEST")
print("=" * 60)


# ============================================================
# CREATE SESSION
# ============================================================

session = requests.Session()


# ============================================================
# 1. LOGIN
# ============================================================

print("\n1. Logging in...")

login_data = {
    "email": EMAIL,
    "password": PASSWORD
}

login_response = session.post(
    f"{BASE_URL}/login",
    json=login_data
)

print(
    "Login status:",
    login_response.status_code
)

login_result = login_response.json()

print(
    "Login response:",
    login_result
)


# Stop if login failed

if login_response.status_code != 200:

    print("\nLogin failed!")

    print("=" * 60)

    exit()


# ============================================================
# 2. CSV PREDICTION
# ============================================================

print("\n2. Uploading test CSV...")

try:

    with open(CSV_PATH, "rb") as file:

        files = {
            "file": (
                "test_customer_data.csv",
                file,
                "text/csv"
            )
        }

        prediction_response = session.post(
            f"{BASE_URL}/predict",
            files=files
        )


except FileNotFoundError:

    print("\nERROR: Test CSV not found!")

    print(
        "Expected location:",
        CSV_PATH
    )

    exit()


print(
    "\nPrediction status:",
    prediction_response.status_code
)


prediction_result = prediction_response.json()


print("\nPrediction response:")

print(
    "Success:",
    prediction_result.get("success")
)

print(
    "Message:",
    prediction_result.get("message")
)

print(
    "Total records:",
    prediction_result.get("total_records")
)


# ============================================================
# 3. SHOW FIRST 10 PREDICTIONS
# ============================================================

if prediction_result.get("success"):

    print("\nFirst 10 predictions:")

    predictions = prediction_result.get(
        "predictions",
        []
    )

    for prediction in predictions[:10]:

        print(
            prediction["customerID"],
            "|",
            prediction["Predicted_Churn"],
            "|",
            prediction["Churn_Probability"],
            "%"
        )

else:

    print(
        "\nPrediction failed:",
        prediction_result
    )


# ============================================================
# 4. GET PREDICTION HISTORY
# ============================================================

print("\n4. Getting prediction history...")


history_response = session.get(
    f"{BASE_URL}/predictions"
)


print(
    "History status:",
    history_response.status_code
)


history_result = history_response.json()


print(
    "History success:",
    history_result.get("success")
)

print(
    "History count:",
    history_result.get("count")
)


# ============================================================
# 5. SHOW FIRST 5 HISTORY RECORDS
# ============================================================

if history_result.get("success"):

    history = history_result.get(
        "predictions",
        []
    )

    print("\nFirst 5 history records:")

    for record in history[:5]:

        print(
            record["customerID"],
            "|",
            record["prediction"],
            "|",
            record["probability"],
            "%",
            "|",
            record["created_at"]
        )

else:

    print(
        "\nCould not retrieve history:"
    )

    print(history_result)


# ============================================================
# COMPLETED
# ============================================================

print("\n" + "=" * 60)
print("CHURNGUARD API TEST COMPLETED")
print("=" * 60)