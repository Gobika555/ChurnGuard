import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "processed_data.csv"
)
MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "churn_model.pkl"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "prediction_results.csv"
)
print("=" * 50)
print("Loading Processed Dataset...")
print("=" * 50)

df = pd.read_csv(DATA_PATH)

print("Dataset Shape :", df.shape)
X = df.drop(columns=["Churn"])
y = df["Churn"]

# ======================================
# Train-Test Split
# ======================================

_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# ======================================
# Load Model
# ======================================

print("\nLoading Model...")

model = joblib.load(MODEL_PATH)

print("Model Loaded Successfully")

# ======================================
# Prediction
# ======================================

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# ======================================
# Evaluation
# ======================================

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
roc_auc = roc_auc_score(y_test, y_prob)

print("\n========== MODEL PERFORMANCE ==========")
print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")
print(f"ROC AUC  : {roc_auc:.4f}")

print("\nConfusion Matrix")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report")
print(classification_report(y_test, y_pred))

# ======================================
# Save Predictions
# ======================================

results = X_test.copy()
results["Actual_Churn"] = y_test.values
results["Predicted_Churn"] = y_pred
results["Probability"] = y_prob

results.to_csv(OUTPUT_PATH, index=False)

print("\nPrediction Results Saved Successfully")
print(OUTPUT_PATH)