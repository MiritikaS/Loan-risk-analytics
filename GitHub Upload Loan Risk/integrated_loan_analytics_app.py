"""
Integrated Streamlit App:
1. EDA Analysis
2. Power BI Dashboard Screenshots and Insights
3. Loan Approval Recommendation App

Run:
    python -m streamlit run integrated_loan_analytics_app.py

Login:
    User ID: faculty
    Password: loananalytics123
"""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


MODEL_PATH = Path("model_outputs") / "loan_approval_model.pkl"
DASHBOARD_1 = Path("assets") / "loan_portfolio_risk_summary.png"
DASHBOARD_2 = Path("assets") / "product_credit_behaviour.png"

USER_ID = "faculty"
PASSWORD = "loananalytics123"


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


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
st.caption("EDA Analysis | Power BI Dashboard Insights | Loan Approval Recommendation")

tab1, tab2, tab3 = st.tabs([
    "EDA Analysis",
    "Power BI Dashboards",
    "Loan Approval Recommendation",
])

with tab1:
    st.header("EDA Analysis Summary")
    st.write(
        "This section summarizes the main exploratory and diagnostic analysis completed using SQL Server, Power BI and Python."
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Customers", "51,336")
    k2.metric("Avg Credit Score", "679.86")
    k3.metric("High Risk Customers", "13,334")
    k4.metric("High Risk %", "25.97%")

    st.subheader("Approval Tier Distribution")
    st.dataframe(
        pd.DataFrame({
            "Approval Tier": ["P1", "P2", "P3", "P4"],
            "Customer Count": [5803, 32199, 7452, 5882],
            "Risk Meaning": ["Best approval tier", "Lower / moderate risk", "Higher risk", "Highest risk"],
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Key EDA Findings")
    st.write("- Total customer records after joining internal and external data: 51,336.")
    st.write("- P2 has the largest customer group, with 32.2K customers.")
    st.write("- P3 and P4 together form the high-risk group of 13,334 customers.")
    st.write("- Average credit score is 679.86, indicating a mostly medium-risk portfolio.")
    st.write("- High enquiries, missed payments, delinquency and utilization are important warning indicators.")

    st.subheader("Diagnostic Risk Drivers")
    st.write("- Lower credit score indicates weaker creditworthiness.")
    st.write("- More missed payments indicate repayment stress.")
    st.write("- Higher delinquency count indicates historical repayment issues.")
    st.write("- More credit enquiries indicate credit-seeking behaviour.")
    st.write("- High CC/PL utilization indicates financial pressure.")

    st.subheader("Data Quality Treatment")
    st.write("- `-99999` sentinel values were converted to missing/null values.")
    st.write("- `Approved_Flag` was mapped from numeric SQL import values into P1/P2/P3/P4.")
    st.write("- P1/P2 were treated as lower/moderate risk and P3/P4 as high risk.")
    st.write("- Suspected HL/GL flag mismatch was documented and corrected in the analysis view.")

with tab2:
    st.header("Power BI Dashboard Insights")

    st.subheader("Dashboard 1: Loan Portfolio Risk Summary")
    if DASHBOARD_1.exists():
        st.image(str(DASHBOARD_1), use_container_width=True)
    else:
        st.warning("Dashboard image not found: assets/loan_portfolio_risk_summary.png")

    st.write("**Purpose:** Give management a quick summary of overall loan portfolio risk.")
    st.write("**Main insights:**")
    st.write("- Total customers: 51.336K.")
    st.write("- High-risk customers: 13.334K.")
    st.write("- P2 has the largest share of customers.")
    st.write("- Average missed payments vary by approval tier.")
    st.write("- P3/P4 customers require closer monitoring.")

    st.divider()

    st.subheader("Dashboard 2: Product and Credit Behaviour")
    if DASHBOARD_2.exists():
        st.image(str(DASHBOARD_2), use_container_width=True)
    else:
        st.warning("Dashboard image not found: assets/product_credit_behaviour.png")

    st.write("**Purpose:** Understand product exposure, utilization, enquiries and delinquency behaviour.")
    st.write("**Main insights:**")
    st.write("- Total active trade lines are 107.20K.")
    st.write("- Average total trade lines are 4.86.")
    st.write("- Average CC utilization is 0.63 and average PL utilization is 0.75.")
    st.write("- P4 shows higher enquiries and delinquency, which indicates repayment stress.")
    st.write("- Secured and unsecured exposure differs across approval tiers.")

with tab3:
    st.header("Loan Approval Recommendation App")
    st.write(
        "This section uses the trained Logistic Regression model and business rules to recommend Approve, Manual Review, or Reject / Very Strict Review."
    )

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

    input_df = pd.DataFrame([row])

    if st.button("Generate Loan Recommendation", type="primary"):
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

