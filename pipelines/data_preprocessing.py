import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

# -------------------------------
# File Paths
# -------------------------------

RAW_DATA_PATH = "data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv"
PROCESSED_DATA_PATH = "data/processed/processed_data.csv"

MODELS_DIR = "models"
ENCODER_PATH = os.path.join(MODELS_DIR, "encoder.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")

# Create folders if they don't exist
os.makedirs("data/processed", exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# -------------------------------
# Load Dataset
# -------------------------------

print("Loading dataset...")

df = pd.read_csv(RAW_DATA_PATH)

print(f"Dataset Shape : {df.shape}")

# -------------------------------
# Dataset Information
# -------------------------------

print("\nDataset Information")
print(df.info())

print("\nMissing Values")
print(df.isnull().sum())

# -------------------------------
# Remove Duplicates
# -------------------------------

duplicates = df.duplicated().sum()

print(f"\nDuplicate Records : {duplicates}")

if duplicates > 0:
    df.drop_duplicates(inplace=True)
    print("Duplicates removed.")

# -------------------------------
# Handle TotalCharges
# -------------------------------

df["TotalCharges"] = pd.to_numeric(
    df["TotalCharges"],
    errors="coerce"
)

df["TotalCharges"].fillna(
    df["TotalCharges"].median(),
    inplace=True
)

# -------------------------------
# Drop customerID
# -------------------------------

df.drop("customerID", axis=1, inplace=True)

# -------------------------------
# Encode Categorical Columns
# -------------------------------

encoder = LabelEncoder()

categorical_columns = df.select_dtypes(include="object").columns

for column in categorical_columns:
     df[column] encoder.fit_transform(df[column])

joblib.dump(encoder, ENCODER_PATH)

print("\nEncoder saved.")

# -------------------------------
# Scale Numerical Features
# -------------------------------

scaler = StandardScaler()

numerical_columns = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges"
]

df[numerical_columns] = scaler.fit_transform(
    df[numerical_columns]
)

joblib.dump(scaler, SCALER_PATH)

print("Scaler saved.")

# -------------------------------
# Save Processed Dataset
# -------------------------------

df.to_csv(PROCESSED_DATA_PATH, index=False)

print("\nProcessed dataset saved.")

print(f"Location : {PROCESSED_DATA_PATH}")

print("\nCleaning Completed Successfully!")

print(df.head())