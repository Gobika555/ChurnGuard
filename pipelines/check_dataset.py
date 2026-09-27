import pandas as pd
import os

FILE_PATH = "../data/WA_Fn-UseC_-Telco-Customer-Churn.csv"

print("=" * 60)
print("CHURNGUARD DATASET INSPECTION")
print("=" * 60)

df = pd.read_csv(FILE_PATH)

print("\nDataset loaded successfully!")

print("\nRows    :", df.shape[0])
print("Columns :", df.shape[1])

print("\nFile size:")
size_mb = os.path.getsize(FILE_PATH) / (1024 * 1024)
print(round(size_mb, 2), "MB")

print("\nColumns:")
for column in df.columns:
    print("-", column)

print("\nMissing values:")
print(df.isnull().sum())

print("\nChurn distribution:")
print(df["Churn"].value_counts())

print("\nChurn percentage:")
print(
    df["Churn"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("\nFirst 5 rows:")
print(df.head())

print("\n" + "=" * 60)
print("INSPECTION COMPLETED")
print("=" * 60)