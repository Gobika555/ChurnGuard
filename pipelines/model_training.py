import os
import joblib
import mlflow
import mlflow.sklearn
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "../data/processed_data.csv"
MODEL_DIR = "../models"
MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.pkl")

TARGET_COLUMN = "Churn"

TEST_SIZE = 0.20
RANDOM_STATE = 42


# ============================================================
# CREATE MODEL DIRECTORY
# ============================================================

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# LOAD PROCESSED DATASET
# ============================================================

print("=" * 60)
print("CHURNGUARD - FULL DATASET TRAINING")
print("=" * 60)

print("\nLoading processed dataset...")

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)


# ============================================================
# CHECK TARGET
# ============================================================

if TARGET_COLUMN not in df.columns:
    raise ValueError(
        f"Target column '{TARGET_COLUMN}' not found."
    )


# ============================================================
# SPLIT FEATURES AND TARGET
# ============================================================

X = df.drop(columns=[TARGET_COLUMN])
y = df[TARGET_COLUMN]

print("\nFeatures shape:", X.shape)
print("Target shape:", y.shape)

print("\nTarget distribution:")
print(y.value_counts())


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y
)

print("\nTrain samples:", len(X_train))
print("Test samples :", len(X_test))


# ============================================================
# RANDOM FOREST MODEL
# ============================================================

print("\nCreating Random Forest model...")

model = RandomForestClassifier(
    n_estimators=100,
    random_state=RANDOM_STATE,
    n_jobs=-1
)


# ============================================================
# MLFLOW
# ============================================================

mlflow.set_experiment("ChurnGuard")

with mlflow.start_run():

    print("\nTraining Random Forest...")
    print("Please wait...")

    model.fit(X_train, y_train)

    print("Training completed!")


    # ========================================================
    # PREDICTION
    # ========================================================

    y_pred = model.predict(X_test)


    # ========================================================
    # EVALUATION
    # ========================================================

    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    print(f"\nAccuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")


    print("\nConfusion Matrix:")

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    print(cm)


    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            y_pred,
            zero_division=0
        )
    )


    # ========================================================
    # LOG PARAMETERS TO MLFLOW
    # ========================================================

    mlflow.log_param(
        "model",
        "RandomForestClassifier"
    )

    mlflow.log_param(
        "n_estimators",
        100
    )

    mlflow.log_param(
        "test_size",
        TEST_SIZE
    )

    mlflow.log_param(
        "random_state",
        RANDOM_STATE
    )

    mlflow.log_param(
        "dataset_rows",
        len(df)
    )

    mlflow.log_param(
        "dataset_columns",
        len(df.columns)
    )


    # ========================================================
    # LOG METRICS
    # ========================================================

    mlflow.log_metric(
        "accuracy",
        accuracy
    )

    mlflow.log_metric(
        "precision",
        precision
    )

    mlflow.log_metric(
        "recall",
        recall
    )

    mlflow.log_metric(
        "f1_score",
        f1
    )


    # ========================================================
    # SAVE MODEL
    # ========================================================

    joblib.dump(
        model,
        MODEL_PATH
    )

    print("\nModel saved successfully!")

    print("Model path:")
    print(MODEL_PATH)


    # ========================================================
    # LOG MODEL TO MLFLOW
    # ========================================================

    mlflow.sklearn.log_model(
        model,
        "churn_model"
    )


# ============================================================
# COMPLETED
# ============================================================

print("\n" + "=" * 60)
print("FULL DATASET TRAINING COMPLETED")
print("=" * 60)

print("\nDataset used :", len(df), "rows")
print("Model        : Random Forest")
print("Model file   :", MODEL_PATH)

print("\nChurnGuard model is ready for prediction.")