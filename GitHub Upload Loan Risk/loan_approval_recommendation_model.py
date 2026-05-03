"""
Loan Approval Recommendation - Python Analysis and Predictive Model

Purpose:
1. Read internal bank data and external CIBIL data.
2. Merge both datasets using PROSPECTID.
3. Clean sentinel values such as -99999.
4. Convert Approved_Flag into business labels:
   1/P1 = P1, 2/P2 = P2, 3/P3 = P3, 4/P4 = P4.
5. Create a binary risk target:
   P1/P2 = lower risk, P3/P4 = higher risk.
6. Train a Logistic Regression model.
7. Save the trained model for the Streamlit approval recommendation app.

Why Logistic Regression:
The business question is classification: should the applicant be approved,
sent for manual review, or rejected? Logistic Regression gives a risk
probability that is easy to explain in a banking project presentation.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_DIR = Path(r"D:\Internship Analytixlabs\Project 1")
INTERNAL_FILE = PROJECT_DIR / "INTERNAL_BANK_DATA.xlsx"
EXTERNAL_FILE = PROJECT_DIR / "EXTERNAL_CIBIL_DATA.xlsx"
OUTPUT_DIR = Path("approval_model_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def normalize_approved_flag(value):
    """Convert imported numeric or text approval flag into P1/P2/P3/P4."""
    if pd.isna(value):
        return np.nan
    text = str(value).strip().upper()
    mapping = {
        "1": "P1",
        "1.0": "P1",
        "1.00": "P1",
        "P1": "P1",
        "2": "P2",
        "2.0": "P2",
        "2.00": "P2",
        "P2": "P2",
        "3": "P3",
        "3.0": "P3",
        "3.00": "P3",
        "P3": "P3",
        "4": "P4",
        "4.0": "P4",
        "4.00": "P4",
        "P4": "P4",
    }
    return mapping.get(text, text)


def load_and_clean_data():
    """Load, merge, and clean the two project workbooks."""
    internal_df = pd.read_excel(INTERNAL_FILE, sheet_name="case_study1")
    external_df = pd.read_excel(EXTERNAL_FILE, sheet_name="case_study2")

    df = external_df.merge(internal_df, on="PROSPECTID", how="inner")

    # Convert sentinel value to missing. This prevents -99999 from damaging averages/model training.
    df = df.replace(-99999, np.nan)

    df["Approved_Flag"] = df["Approved_Flag"].apply(normalize_approved_flag)

    # Data audit showed HL_Flag and GL_Flag appear swapped against Home_TL and Gold_TL.
    if "HL_Flag" in df.columns and "GL_Flag" in df.columns:
        df["Corrected_HL_Flag"] = df["GL_Flag"]
        df["Corrected_GL_Flag"] = df["HL_Flag"]

    # Model target: P3/P4 customers are considered higher risk.
    df["High_Risk_Target"] = df["Approved_Flag"].isin(["P3", "P4"]).astype(int)

    return df


def train_model(df):
    """Train Logistic Regression model and return model metrics."""
    drop_cols = [
        "PROSPECTID",
        "Approved_Flag",
        "High_Risk_Target",
        "HL_Flag",
        "GL_Flag",
    ]

    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    y = df["High_Risk_Target"]

    categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocess = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, categorical_cols),
        ]
    )

    model = LogisticRegression(max_iter=1000, class_weight="balanced")

    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocess),
            ("model", model),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        "rows_after_join": len(df),
        "low_moderate_risk_customers": int((df["High_Risk_Target"] == 0).sum()),
        "high_risk_customers": int((df["High_Risk_Target"] == 1).sum()),
        "accuracy": accuracy_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_prob),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred),
        "feature_names": X.columns.tolist(),
    }

    return pipeline, metrics


def save_outputs(model, metrics):
    """Save model and model summary for web app and final submission."""
    joblib.dump(model, OUTPUT_DIR / "loan_approval_recommendation_model.pkl")

    pd.Series(metrics["feature_names"], name="feature").to_csv(
        OUTPUT_DIR / "model_features.csv", index=False
    )

    with open(OUTPUT_DIR / "model_metrics.txt", "w", encoding="utf-8") as f:
        f.write("Loan Approval Recommendation Model Metrics\n")
        f.write("========================================\n\n")
        f.write(f"Rows after join: {metrics['rows_after_join']}\n")
        f.write(f"Low / moderate risk customers: {metrics['low_moderate_risk_customers']}\n")
        f.write(f"High risk customers: {metrics['high_risk_customers']}\n")
        f.write(f"Accuracy: {metrics['accuracy']:.4f}\n")
        f.write(f"ROC-AUC: {metrics['roc_auc']:.4f}\n")
        f.write(f"Confusion matrix: {metrics['confusion_matrix']}\n\n")
        f.write(metrics["classification_report"])


def main():
    df = load_and_clean_data()
    model, metrics = train_model(df)
    save_outputs(model, metrics)

    print("Rows after join:", metrics["rows_after_join"])
    print("Low / moderate risk customers:", metrics["low_moderate_risk_customers"])
    print("High risk customers:", metrics["high_risk_customers"])
    print("Model saved to:", OUTPUT_DIR / "loan_approval_recommendation_model.pkl")
    print("Metrics saved to:", OUTPUT_DIR / "model_metrics.txt")
    print("Accuracy:", round(metrics["accuracy"], 4))
    print("ROC-AUC:", round(metrics["roc_auc"], 4))
    print()
    print(metrics["classification_report"])


if __name__ == "__main__":
    main()

