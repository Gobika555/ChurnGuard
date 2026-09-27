import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# ======================================
# Project Paths
# ======================================

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

REPORT_PATH = os.path.join(
    BASE_DIR,
    "docs",
    "evaluation_report.txt"
)

# ======================================
# Load Dataset
# ======================================

print("=" * 50)
print("Loading Processed Dataset...")
print("=" * 50)

df = pd.read_csv(DATA_PATH)

print("Dataset Loaded Successfully")
print(df.shape)

# ======================================
# Split Dataset
# ======================================

X = df.drop("Churn", axis=1)
y = df["Churn"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# ======================================
# Load Model
# ======================================

print("\nLoading Trained Model...")

model = joblib.load(MODEL_PATH)

print("Model Loaded Successfully")

# ======================================
# Prediction
# ======================================

y_pred = model.predict(X_test)

# ======================================
# Evaluation Metrics
# ======================================

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

cm = confusion_matrix(y_test, y_pred)

report = classification_report(y_test, y_pred)

# ======================================
# Print Results
# ======================================

print("\n========== MODEL EVALUATION ==========")

print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")

print("\nConfusion Matrix")
print(cm)

print("\nClassification Report")
print(report)

# ======================================
# Save Report
# ======================================

os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)

with open(REPORT_PATH, "w") as file:

    file.write("CHURNGUARD MODEL EVALUATION\n\n")

    file.write(f"Accuracy  : {accuracy:.4f}\n")
    file.write(f"Precision : {precision:.4f}\n")
    file.write(f"Recall    : {recall:.4f}\n")
    file.write(f"F1 Score  : {f1:.4f}\n\n")

    file.write("Confusion Matrix\n")
    file.write(str(cm))
    file.write("\n\n")

    file.write("Classification Report\n")
    file.write(report)

print("\nEvaluation Report Saved Successfully")
print(REPORT_PATH)