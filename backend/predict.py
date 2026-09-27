import os
import joblib
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "churn_model.pkl")

# These are the raw Telco columns used by ChurnGuard.
RAW_COLUMNS = [
    "customerID", "gender", "SeniorCitizen", "Partner", "Dependents",
    "tenure", "PhoneService", "MultipleLines", "InternetService",
    "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
    "StreamingTV", "StreamingMovies", "Contract", "PaperlessBilling",
    "PaymentMethod", "MonthlyCharges", "TotalCharges"
]


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def model_status():
    return {
        "available": os.path.exists(MODEL_PATH),
        "path": MODEL_PATH,
        "name": "Random Forest"
    }


def normalize_columns(df):
    """
    Normalize common CSV header problems:
    - UTF-8 BOM
    - leading/trailing spaces
    - duplicate whitespace around names
    """
    df = df.copy()
    df.columns = [
        str(c).replace("\ufeff", "").strip()
        for c in df.columns
    ]
    return df


def validate_input_dataframe(df):
    """
    Validate a raw customer CSV. Returns a clean copy.
    This deliberately does NOT reject harmless extra columns.
    """
    if df is None or df.empty:
        raise ValueError("The uploaded CSV is empty.")

    df = normalize_columns(df)

    missing = [c for c in RAW_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            "The CSV is missing required customer columns: "
            + ", ".join(missing)
        )

    # Keep required raw columns and ignore harmless extra columns.
    df = df[RAW_COLUMNS].copy()

    if df["customerID"].isna().all():
        raise ValueError("customerID cannot be empty for all rows.")

    # Numeric fields.
    df["SeniorCitizen"] = pd.to_numeric(
        df["SeniorCitizen"], errors="coerce"
    ).fillna(0)

    df["tenure"] = pd.to_numeric(
        df["tenure"], errors="coerce"
    ).fillna(0)

    df["MonthlyCharges"] = pd.to_numeric(
        df["MonthlyCharges"], errors="coerce"
    ).fillna(0)

    # TotalCharges in the Telco dataset may contain blank strings.
    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"].astype(str).str.strip(),
        errors="coerce"
    ).fillna(0)

    # Clean categorical text without changing legitimate values.
    for column in RAW_COLUMNS:
        if column not in {
            "customerID", "SeniorCitizen", "tenure",
            "MonthlyCharges", "TotalCharges"
        }:
            df[column] = df[column].fillna("").astype(str).str.strip()

    df["customerID"] = (
        df["customerID"].fillna("UNKNOWN").astype(str).str.strip()
    )

    return df


def prepare_features(df):
    """
    Convert the 20-column raw Telco customer data into the exact
    feature representation expected by the trained Random Forest.
    """
    df = validate_input_dataframe(df)

    features = df.drop(columns=["customerID"]).copy()

    categorical_columns = features.select_dtypes(
        include=["object", "category", "string"]
    ).columns.tolist()

    features = pd.get_dummies(
        features,
        columns=categorical_columns,
        dtype=int
    )

    return features


def align_features(features, model):
    """
    Reindex to the model's exact training columns.
    Missing dummy columns become 0; extra columns are ignored.
    """
    if not hasattr(model, "feature_names_in_"):
        raise ValueError(
            "The trained model does not contain feature_names_in_. "
            "The model cannot be safely aligned with the uploaded CSV."
        )

    expected = list(model.feature_names_in_)
    return features.reindex(columns=expected, fill_value=0)


def _get_churn_probabilities(model, probability_matrix):
    classes = list(getattr(model, "classes_", []))

    if 1 in classes:
        return probability_matrix[:, classes.index(1)] * 100

    if "Yes" in classes:
        return probability_matrix[:, classes.index("Yes")] * 100

    if probability_matrix.shape[1] == 2:
        return probability_matrix[:, 1] * 100

    return probability_matrix[:, 0] * 0


def predict_dataframe(df):
    """
    Main prediction function used by Flask.

    Input:
        Raw 20-column Telco customer DataFrame.

    Output columns:
        customerID
        Predicted_Churn
        Churn_Probability
        Risk_Level
    """
    clean_df = validate_input_dataframe(df)
    model = load_model()

    customer_ids = clean_df["customerID"].tolist()

    features = prepare_features(clean_df)
    features = align_features(features, model)

    predictions = model.predict(features)
    probabilities = model.predict_proba(features)
    churn_probabilities = _get_churn_probabilities(
        model, probabilities
    )

    results = []

    for i, prediction in enumerate(predictions):
        probability = round(float(churn_probabilities[i]), 2)

        if probability >= 70:
            risk = "High"
        elif probability >= 40:
            risk = "Medium"
        else:
            risk = "Low"

        results.append({
            "customerID": customer_ids[i],
            "Predicted_Churn": "Yes" if prediction == 1 else "No",
            "Churn_Probability": probability,
            "Risk_Level": risk
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    test_file = os.path.join(
        BASE_DIR, "data", "test_customer_data.csv"
    )

    print("=" * 70)
    print("CHURNGUARD PREDICTION SELF-TEST")
    print("=" * 70)
    print("Model:", MODEL_PATH)
    print("CSV:", test_file)

    df = pd.read_csv(test_file)
    print("Input shape:", df.shape)
    print("Input columns:", list(df.columns))

    results = predict_dataframe(df)

    print("\nPrediction successful.")
    print("Output shape:", results.shape)
    print("\nFirst 10 results:")
    print(results.head(10).to_string(index=False))
    print("\nRisk counts:")
    print(results["Risk_Level"].value_counts().to_string())
    print("=" * 70)
