"""
Live EDA + Loan Approval Recommendation Streamlit App

This version does not use dashboard screenshots.
It creates live Streamlit dashboards directly from the Excel data.

Run:
    python -m streamlit run live_eda_loan_approval_app.py

Login:
    User ID: faculty
    Password: loananalytics123
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_DIR = Path(r"D:\Internship Analytixlabs\Project 1")
INTERNAL_FILE = PROJECT_DIR / "INTERNAL_BANK_DATA.xlsx"
EXTERNAL_FILE = PROJECT_DIR / "EXTERNAL_CIBIL_DATA.xlsx"
MODEL_PATH = Path("model_outputs") / "loan_approval_model.pkl"

USER_ID = "faculty"
PASSWORD = "loananalytics123"


def normalize_approved_flag(value):
    if pd.isna(value):
        return np.nan
    text = str(value).strip().upper()
    mapping = {
        "1": "P1", "1.0": "P1", "1.00": "P1", "P1": "P1",
        "2": "P2", "2.0": "P2", "2.00": "P2", "P2": "P2",
        "3": "P3", "3.0": "P3", "3.00": "P3", "P3": "P3",
        "4": "P4", "4.0": "P4", "4.00": "P4", "P4": "P4",
    }
    return mapping.get(text, text)


@st.cache_data(show_spinner=True)
def load_data():
    internal = pd.read_excel(INTERNAL_FILE, sheet_name="case_study1")
    external = pd.read_excel(EXTERNAL_FILE, sheet_name="case_study2")
    df = external.merge(internal, on="PROSPECTID", how="inner")
    df = df.replace(-99999, np.nan)

    df["Approved_Flag"] = df["Approved_Flag"].apply(normalize_approved_flag)
    df["High_Risk_Target"] = df["Approved_Flag"].isin(["P3", "P4"]).astype(int)
    df["Credit_Score_Risk_Band"] = np.select(
        [
            df["Credit_Score"] < 600,
            df["Credit_Score"].between(600, 749, inclusive="both"),
            df["Credit_Score"] >= 750,
        ],
        ["High Risk", "Medium Risk", "Low Risk"],
        default="Unknown",
    )
    df["Income_Band"] = pd.cut(
        df["NETMONTHLYINCOME"],
        bins=[-1, 14999, 30000, 60000, np.inf],
        labels=["Below 15K", "15K-30K", "30K-60K", "Above 60K"],
    ).astype(str)

    return df


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


def apply_filters(df):
    st.sidebar.header("Dashboard Filters")

    approval = st.sidebar.multiselect(
        "Approval Tier",
        ["P1", "P2", "P3", "P4"],
        default=["P1", "P2", "P3", "P4"],
    )
    gender = st.sidebar.multiselect(
        "Gender",
        sorted(df["GENDER"].dropna().unique().tolist()),
        default=sorted(df["GENDER"].dropna().unique().tolist()),
    )
    education = st.sidebar.multiselect(
        "Education",
        sorted(df["EDUCATION"].dropna().unique().tolist()),
        default=sorted(df["EDUCATION"].dropna().unique().tolist()),
    )
    risk_band = st.sidebar.multiselect(
        "Credit Score Risk Band",
        ["High Risk", "Medium Risk", "Low Risk"],
        default=["High Risk", "Medium Risk", "Low Risk"],
    )

    income_min = int(df["NETMONTHLYINCOME"].fillna(0).min())
    income_max = int(df["NETMONTHLYINCOME"].fillna(0).max())
    selected_income = st.sidebar.slider(
        "Monthly Income Range",
        min_value=income_min,
        max_value=income_max,
        value=(income_min, min(income_max, 2500000)),
        step=1000,
    )

    filtered = df[
        df["Approved_Flag"].isin(approval)
        & df["GENDER"].isin(gender)
        & df["EDUCATION"].isin(education)
        & df["Credit_Score_Risk_Band"].isin(risk_band)
        & df["NETMONTHLYINCOME"].between(selected_income[0], selected_income[1])
    ].copy()

    return filtered


def metric_row(df):
    total = df["PROSPECTID"].nunique()
    high_risk = int((df["High_Risk_Target"] == 1).sum())
    high_pct = high_risk / total if total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Customers", f"{total:,.0f}")
    c2.metric("Avg Credit Score", f"{df['Credit_Score'].mean():.2f}" if total else "0")
    c3.metric("Avg Monthly Income", f"{df['NETMONTHLYINCOME'].mean()/1000:.2f}K" if total else "0")
    c4.metric("High Risk Customers", f"{high_risk:,.0f}")
    c5.metric("High Risk %", f"{high_pct:.2%}")


def approval_order(df):
    order = ["P1", "P2", "P3", "P4"]
    df = df.copy()
    df["Approved_Flag"] = pd.Categorical(df["Approved_Flag"], categories=order, ordered=True)
    return df.sort_values("Approved_Flag")


def approval_decision(probability, credit_score, missed_payments, delinquencies, enquiries, cc_util, pl_util):
    reasons = []
    if credit_score < 600:
        reasons.append("Credit score below 600")
    if missed_payments > 2:
        reasons.append("More than 2 missed payments")
    if delinquencies > 2:
        reasons.append("More than 2 delinquency events")
    if enquiries > 10:
        reasons.append("More than 10 credit enquiries")
    if cc_util > 0.75:
        reasons.append("Credit card utilization above 75%")
    if pl_util > 0.75:
        reasons.append("Personal loan utilization above 75%")

    severe_count = sum([
        credit_score < 600,
        missed_payments > 5,
        delinquencies > 5,
        enquiries > 15,
        cc_util > 1.0,
        pl_util > 1.0,
    ])

    if probability >= 0.75 or severe_count >= 2:
        return "Reject / Very Strict Review", "Applicant shows very high risk. Loan should not be approved without senior review.", reasons or ["High model risk probability"]
    if probability >= 0.40 or reasons:
        return "Manual Review", "Applicant has risk signals. Verify income, repayment capacity and credit behaviour before approval.", reasons
    return "Approve", "Applicant appears lower risk based on model probability and current inputs.", ["No major warning indicators triggered"]


st.set_page_config(page_title="Loan Risk Analytics App", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Loan Risk Analytics Login")
    user_id = st.text_input("User ID")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if user_id == USER_ID and password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid user ID or password.")
    st.info("Demo credentials: User ID = faculty, Password = loananalytics123")
    st.stop()

st.title("Data-Powered Loan Risk Analytics")
st.caption("Live EDA Analysis | Interactive Dashboards | Loan Approval Recommendation")

if not INTERNAL_FILE.exists() or not EXTERNAL_FILE.exists():
    st.error("Excel data files were not found. Check PROJECT_DIR path inside the app file.")
    st.stop()

df = load_data()
filtered_df = apply_filters(df)

tab1, tab2, tab3 = st.tabs([
    "EDA Analysis",
    "Live Dashboards",
    "Loan Approval Recommendation",
])

with tab1:
    st.header("EDA Analysis")
    st.write("This tab summarizes key exploratory and diagnostic analysis from the joined bank and CIBIL dataset.")
    metric_row(filtered_df)

    st.subheader("Dataset Validation")
    v1, v2, v3 = st.columns(3)
    v1.metric("Rows After Join", f"{len(df):,}")
    v2.metric("Unique Customers", f"{df['PROSPECTID'].nunique():,}")
    v3.metric("High Risk Customers", f"{int((df['High_Risk_Target'] == 1).sum()):,}")

    st.subheader("Approval Tier Distribution")
    dist = approval_order(
        filtered_df.groupby("Approved_Flag", observed=False)
        .agg(Customer_Count=("PROSPECTID", "nunique"), Avg_Credit_Score=("Credit_Score", "mean"))
        .reset_index()
    )
    st.dataframe(dist, use_container_width=True, hide_index=True)

    st.subheader("Main EDA Findings")
    st.write("- P1/P2 customers are treated as lower or moderate risk; P3/P4 customers are treated as high risk.")
    st.write("- Credit score, missed payments, delinquency events, enquiries and utilization are key risk indicators.")
    st.write("- `-99999` values are treated as missing values because they are not real numeric values.")
    st.write("- The app allows filters so EDA results change dynamically by approval tier, gender, education and income.")

    st.subheader("Data Quality Notes")
    dq = pd.DataFrame({
        "Issue": ["-99999 sentinel values", "Approved_Flag numeric import", "Zero/non-positive income", "HL/GL flag mismatch"],
        "Treatment": ["Converted to missing values", "Mapped into P1/P2/P3/P4", "Flag for manual review", "Documented and corrected in analysis view"],
    })
    st.dataframe(dq, use_container_width=True, hide_index=True)

with tab2:
    st.header("Live Dashboards")
    st.write("These charts are generated live from the data and update when filters are changed.")
    metric_row(filtered_df)

    left, right = st.columns(2)
    with left:
        st.subheader("Customers by Approval Tier")
        plot_df = approval_order(filtered_df.groupby("Approved_Flag", observed=False)["PROSPECTID"].nunique().reset_index(name="Customers"))
        fig = px.bar(plot_df, x="Approved_Flag", y="Customers", text="Customers", color="Approved_Flag")
        fig.update_layout(showlegend=False, xaxis_title="Approval Tier", yaxis_title="Customers")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Risk Distribution")
        pie_df = filtered_df.groupby("Approved_Flag", observed=False)["PROSPECTID"].nunique().reset_index(name="Customers")
        fig = px.pie(pie_df, values="Customers", names="Approved_Flag", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Average Credit Score by Approval Tier")
        score_df = approval_order(filtered_df.groupby("Approved_Flag", observed=False)["Credit_Score"].mean().reset_index())
        fig = px.bar(score_df, x="Approved_Flag", y="Credit_Score", color="Approved_Flag")
        fig.update_layout(showlegend=False, xaxis_title="Approval Tier", yaxis_title="Average Credit Score")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Average Missed Payments by Approval Tier")
        missed_df = approval_order(filtered_df.groupby("Approved_Flag", observed=False)["Tot_Missed_Pmnt"].mean().reset_index())
        fig = px.bar(missed_df, x="Approved_Flag", y="Tot_Missed_Pmnt", color="Approved_Flag")
        fig.update_layout(showlegend=False, xaxis_title="Approval Tier", yaxis_title="Average Missed Payments")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Product and Credit Behaviour")
    c1, c2 = st.columns(2)
    with c1:
        product_cols = ["Auto_TL", "CC_TL", "Consumer_TL", "Gold_TL", "Home_TL", "PL_TL"]
        product_df = pd.DataFrame({
            "Product": product_cols,
            "Trade Lines": [filtered_df[col].sum() for col in product_cols],
        })
        fig = px.bar(product_df, x="Product", y="Trade Lines", text="Trade Lines")
        fig.update_layout(xaxis_title="Loan Product", yaxis_title="Total Trade Lines")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        secured_df = approval_order(
            filtered_df.groupby("Approved_Flag", observed=False)[["Secured_TL", "Unsecured_TL"]].sum().reset_index()
        )
        secured_long = secured_df.melt(id_vars="Approved_Flag", value_vars=["Secured_TL", "Unsecured_TL"], var_name="Exposure Type", value_name="Trade Lines")
        fig = px.bar(secured_long, y="Approved_Flag", x="Trade Lines", color="Exposure Type", orientation="h")
        fig.update_layout(yaxis_title="Approval Tier", xaxis_title="Trade Lines")
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        enq_df = approval_order(filtered_df.groupby("Approved_Flag", observed=False)["tot_enq"].mean().reset_index())
        fig = px.bar(enq_df, y="Approved_Flag", x="tot_enq", orientation="h", color="Approved_Flag")
        fig.update_layout(showlegend=False, yaxis_title="Approval Tier", xaxis_title="Average Enquiries")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        delinq_df = approval_order(filtered_df.groupby("Approved_Flag", observed=False)["num_times_delinquent"].mean().reset_index())
        fig = px.bar(delinq_df, y="Approved_Flag", x="num_times_delinquent", orientation="h", color="Approved_Flag")
        fig.update_layout(showlegend=False, yaxis_title="Approval Tier", xaxis_title="Average Delinquency Count")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Loan Approval Recommendation")
    st.write("This tab uses the trained Logistic Regression model and business rules to recommend Approve, Manual Review or Reject / Very Strict Review.")

    if not MODEL_PATH.exists():
        st.error("Model file not found. First run: python train_loan_approval_model.py")
        st.stop()

    model = load_model()
    feature_names = list(model.named_steps["preprocess"].feature_names_in_)

    left, right = st.columns(2)
    with left:
        st.subheader("Applicant Details")
        age = st.number_input("Age", min_value=18, max_value=100, value=35)
        gender = st.selectbox("Gender", ["M", "F"])
        marital = st.selectbox("Marital Status", ["Married", "Single"])
        education = st.selectbox("Education", ["GRADUATE", "12TH", "SSC", "UNDER GRADUATE", "POST-GRADUATE", "PROFESSIONAL", "OTHERS"])
        income = st.number_input("Net Monthly Income", min_value=0, value=25000, step=1000)
        employment_months = st.number_input("Months With Current Employer", min_value=0, value=36)

    with right:
        st.subheader("Credit Behaviour")
        credit_score = st.number_input("Credit Score", min_value=300, max_value=900, value=680)
        missed_payments = st.number_input("Missed Payments", min_value=0, value=0)
        delinquencies = st.number_input("Number of Delinquency Events", min_value=0, value=0)
        enquiries = st.number_input("Total Credit Enquiries", min_value=0, value=3)
        enquiries_l3m = st.number_input("Enquiries in Last 3 Months", min_value=0, value=1)
        cc_util = st.slider("Credit Card Utilization", min_value=0.0, max_value=2.0, value=0.30, step=0.01)
        pl_util = st.slider("Personal Loan Utilization", min_value=0.0, max_value=2.0, value=0.30, step=0.01)

    st.subheader("Trade Line Details")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        total_tl = st.number_input("Total Trade Lines", min_value=0, value=4)
        active_tl = st.number_input("Active Trade Lines", min_value=0, value=2)
    with c2:
        cc_tl = st.number_input("Credit Card TL", min_value=0, value=1)
        pl_tl = st.number_input("Personal Loan TL", min_value=0, value=1)
    with c3:
        secured_tl = st.number_input("Secured TL", min_value=0, value=2)
        unsecured_tl = st.number_input("Unsecured TL", min_value=0, value=2)
    with c4:
        age_oldest_tl = st.number_input("Oldest TL Age in Months", min_value=0, value=60)
        age_newest_tl = st.number_input("Newest TL Age in Months", min_value=0, value=12)

    row = {col: 0 for col in feature_names}
    updates = {
        "AGE": age,
        "GENDER": gender,
        "MARITALSTATUS": marital,
        "EDUCATION": education,
        "NETMONTHLYINCOME": income,
        "Time_With_Curr_Empr": employment_months,
        "Credit_Score": credit_score,
        "Tot_Missed_Pmnt": missed_payments,
        "num_times_delinquent": delinquencies,
        "tot_enq": enquiries,
        "enq_L3m": enquiries_l3m,
        "CC_utilization": cc_util,
        "PL_utilization": pl_util,
        "Total_TL": total_tl,
        "Tot_Active_TL": active_tl,
        "CC_TL": cc_tl,
        "PL_TL": pl_tl,
        "Secured_TL": secured_tl,
        "Unsecured_TL": unsecured_tl,
        "Age_Oldest_TL": age_oldest_tl,
        "Age_Newest_TL": age_newest_tl,
    }
    for key, value in updates.items():
        if key in row:
            row[key] = value

    if st.button("Generate Loan Recommendation", type="primary"):
        input_df = pd.DataFrame([row])
        probability = float(model.predict_proba(input_df)[0, 1])
        decision, message, reasons = approval_decision(
            probability,
            credit_score,
            missed_payments,
            delinquencies,
            enquiries,
            cc_util,
            pl_util,
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("High-Risk Probability", f"{probability:.2%}")
        m2.metric("Recommendation", decision)
        m3.metric("Credit Score", f"{credit_score:.0f}")

        if decision.startswith("Approve"):
            st.success(message)
        elif decision.startswith("Manual"):
            st.warning(message)
        else:
            st.error(message)

        st.subheader("Reasons")
        for reason in reasons:
            st.write(f"- {reason}")
        st.info("This app is a decision-support tool. Final approval should still follow bank policy and document verification.")

