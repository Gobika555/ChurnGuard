import pandas as pd
import os

# ============================================================
# CHURNGUARD - DATA PREPROCESSING
# ============================================================

# Input dataset
INPUT_FILE = "../data/WA_Fn-UseC_-Telco-Customer-Churn.csv"

# Output processed dataset
OUTPUT_FILE = "../data/processed_data.csv"

# Target column
TARGET_COLUMN = "Churn"


# ============================================================
# 1. LOAD DATASET
# ============================================================

print("=" * 60)
print("CHURNGUARD DATA PREPROCESSING")
print("=" * 60)

print("\nLoading dataset...")

df = pd.read_csv(INPUT_FILE)

print("Dataset loaded successfully!")
print("Original shape:", df.shape)


# ============================================================
# 2. CHECK DATASET
# ============================================================

print("\nDataset columns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())


# ============================================================
# 3. REMOVE CUSTOMER ID
# ============================================================

if "customerID" in df.columns:
    df = df.drop(columns=["customerID"])
    print("\ncustomerID removed.")


# ============================================================
# 4. CONVERT TOTALCHARGES TO NUMERIC
# ============================================================

if "TotalCharges" in df.columns:

    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"],
        errors="coerce"
    )

    print("TotalCharges converted to numeric.")


# ============================================================
# 5. HANDLE MISSING VALUES
# ============================================================

print("\nHandling missing values...")

# Numeric columns
numeric_columns = df.select_dtypes(
    include=["int64", "float64"]
).columns

for column in numeric_columns:

    if df[column].isnull().sum() > 0:

        df[column] = df[column].fillna(
            df[column].median()
        )


# Categorical columns
categorical_columns = df.select_dtypes(
    include=["object"]
).columns

for column in categorical_columns:

    if df[column].isnull().sum() > 0:

        df[column] = df[column].fillna(
            df[column].mode()[0]
        )


print("Missing values handled.")


# ============================================================
# 6. ENCODE TARGET
# ============================================================

print("\nEncoding target column...")

if TARGET_COLUMN not in df.columns:
    raise ValueError(
        f"Target column '{TARGET_COLUMN}' not found."
    )

df[TARGET_COLUMN] = df[TARGET_COLUMN].map({
    "No": 0,
    "Yes": 1
})

print("Churn encoding:")
print("No  -> 0")
print("Yes -> 1")


# ============================================================
# 7. SEPARATE FEATURES AND TARGET
# ============================================================

X = df.drop(columns=[TARGET_COLUMN])
y = df[TARGET_COLUMN]


# ============================================================
# 8. ENCODE CATEGORICAL FEATURES
# ============================================================

print("\nEncoding categorical features...")

X = pd.get_dummies(
    X,
    drop_first=True
)


# ============================================================
# 9. COMBINE FEATURES AND TARGET
# ============================================================

processed_df = pd.concat(
    [X, y],
    axis=1
)


# ============================================================
# 10. SAVE PROCESSED DATASET
# ============================================================

processed_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 11. DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 60)
print("PREPROCESSING COMPLETED")
print("=" * 60)

print("\nOriginal dataset shape:")
print(df.shape)

print("\nProcessed dataset shape:")
print(processed_df.shape)

print("\nFinal missing values:")
print(
    processed_df.isnull().sum().sum()
)

print("\nChurn distribution:")
print(
    processed_df[TARGET_COLUMN].value_counts()
)

print("\nProcessed dataset saved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 60)
print("READY FOR MODEL TRAINING")
print("=" * 60)