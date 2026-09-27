import os
import joblib
import pandas as pd


# ============================================================
# CHURNGUARD - PREDICTION PIPELINE
# ============================================================

MODEL_PATH = "../models/churn_model.pkl"

# Use the original dataset as a test input for now.
INPUT_FILE = "../data/test_customer_data.csv"

OUTPUT_FILE = "../data/predictions.csv"

TARGET_COLUMN = "Churn"


# ============================================================
# 1. LOAD MODEL
# ============================================================

print("=" * 60)
print("CHURNGUARD - PREDICTION PIPELINE")
print("=" * 60)

print("\nLoading model...")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model not found at: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)

print("Model loaded successfully!")


# ============================================================
# 2. LOAD INPUT DATA
# ============================================================

print("\nLoading input dataset...")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"Input dataset not found at: {INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)

print("Input dataset loaded!")
print("Original shape:", df.shape)


# ============================================================
# 3. KEEP CUSTOMER IDs
# ============================================================

if "customerID" in df.columns:
    customer_ids = df["customerID"].copy()
else:
    customer_ids = pd.Series(
        range(1, len(df) + 1),
        name="customerID"
    )


# ============================================================
# 4. REMOVE CUSTOMER ID
# ============================================================

if "customerID" in df.columns:
    df = df.drop(columns=["customerID"])


# ============================================================
# 5. REMOVE ACTUAL CHURN
# ============================================================

# The actual Churn column is removed because prediction
# should be based only on customer features.

if TARGET_COLUMN in df.columns:
    df = df.drop(columns=[TARGET_COLUMN])


# ============================================================
# 6. CONVERT TOTALCHARGES
# ============================================================

if "TotalCharges" in df.columns:

    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"],
        errors="coerce"
    )


# ============================================================
# 7. HANDLE MISSING VALUES
# ============================================================

numeric_columns = df.select_dtypes(
    include=["int64", "float64"]
).columns

for column in numeric_columns:

    if df[column].isnull().sum() > 0:

        df[column] = df[column].fillna(
            df[column].median()
        )


categorical_columns = df.select_dtypes(
    include=["object"]
).columns

for column in categorical_columns:

    if df[column].isnull().sum() > 0:

        mode_value = df[column].mode()

        if len(mode_value) > 0:
            df[column] = df[column].fillna(
                mode_value[0]
            )


# ============================================================
# 8. ONE-HOT ENCODE
# ============================================================

df = pd.get_dummies(
    df,
    drop_first=True
)


# ============================================================
# 9. MATCH TRAINING FEATURES
# ============================================================

# The Random Forest was trained using 30 features.
# feature_names_in_ contains the exact training columns.

if hasattr(model, "feature_names_in_"):

    training_features = model.feature_names_in_

    # Add missing training columns
    for column in training_features:

        if column not in df.columns:
            df[column] = 0

    # Remove unexpected columns and arrange columns
    # in exactly the same order as during training.

    df = df.reindex(
        columns=training_features,
        fill_value=0
    )

else:

    print(
        "\nWARNING: Model does not contain feature names."
    )


# ============================================================
# 10. CHECK FINAL FEATURES
# ============================================================

print("\nFinal prediction features:")
print("Rows    :", df.shape[0])
print("Columns :", df.shape[1])


# ============================================================
# 11. MAKE PREDICTIONS
# ============================================================

print("\nMaking predictions...")

predictions = model.predict(df)


# ============================================================
# 12. PREDICTION PROBABILITY
# ============================================================

if hasattr(model, "predict_proba"):

    probabilities = model.predict_proba(df)

    churn_probability = probabilities[:, 1] * 100

else:

    churn_probability = [None] * len(df)


# ============================================================
# 13. CREATE RESULT DATAFRAME
# ============================================================

result = pd.DataFrame({

    "customerID": customer_ids,

    "Predicted_Churn": [
        "Yes" if prediction == 1 else "No"
        for prediction in predictions
    ],

    "Churn_Probability": churn_probability

})


# ============================================================
# 14. SAVE PREDICTIONS
# ============================================================

result.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 15. DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 60)
print("PREDICTION COMPLETED")
print("=" * 60)

print("\nPrediction distribution:")

print(
    result["Predicted_Churn"].value_counts()
)

print("\nFirst 10 predictions:")

print(
    result.head(10).to_string(index=False)
)

print("\nPredictions saved to:")

print(OUTPUT_FILE)

print("\n" + "=" * 60)
print("CHURNGUARD PREDICTION PIPELINE COMPLETED")
print("=" * 60)