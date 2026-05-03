"""
Loan Approval Recommendation Streamlit App

Run from Command Prompt:
    cd "path\\to\\Loan_Approval_Recommendation_App"
    python -m streamlit run loan_approval_recommendation_app.py

Demo login:
    User ID: faculty
    Password: loanapproval123
"""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


MODEL_PATH = Path("approval_model_outputs") / "loan_approval_recommendation_model.pkl"
USER_ID = "faculty"
PASSWORD = "loanapproval123"


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


def approval_decision(probability, credit_score, missed_payments, delinquencies, enquiries, cc_util, pl_util):
    """
    Convert model probability plus business rules into an approval decision.

    Reject:
      Very high risk probability or severe credit stress.
    Manual Review:
      Medium risk probability or warning indicators.
    Approve:
      Low model probability and no severe warning indicators.
    """
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

    severe_flags = sum(
        [
            credit_score < 600,
            missed_payments > 5,
            delinquencies > 5,
            enquiries > 15,
            cc_util > 1.0,
            pl_util > 1.0,
        ]
    )

    if probability >= 0.75 or severe_flags >= 2:
        decision = "Reject / Very Strict Review"
        message = "Applicant shows very high credit risk. Loan should not be approved without senior-level review."
    elif probability >= 0.40 or reasons:
        decision = "Manual Review"
        message = "Applicant has risk signals. Verify income, repayment capacity and recent credit behaviour before approval."
    else:
        decision = "Approve"
        message = "Applicant appears lower risk based on current inputs and model probability."

    if not reasons:
        reasons = ["No major warning indicators triggered"]

    return decision, message, reasons


st.set_page_config(page_title="Loan Approval Recommendation", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Loan Approval Recommendation Login")
    user_id = st.text_input("User ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if user_id == USER_ID and password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid user ID or password.")

    st.info("Demo credentials: User ID = faculty, Password = loanapproval123")
    st.stop()

st.title("Loan Approval Recommendation App")
st.write("Enter applicant details to get a loan approval recommendation, risk probability and business reasons.")

if not MODEL_PATH.exists():
    st.error("Model file not found. First run: python loan_approval_recommendation_model.py")
    st.stop()

model = load_model()
feature_names = list(model.named_steps["preprocess"].feature_names_in_)

left, right = st.columns([1, 1])

with left:
    st.subheader("Applicant Profile")
    age = st.number_input("Age", min_value=18, max_value=100, value=35)
    gender = st.selectbox("Gender", ["M", "F"])
    marital = st.selectbox("Marital Status", ["Married", "Single"])
    education = st.selectbox(
        "Education",
        ["GRADUATE", "12TH", "SSC", "UNDER GRADUATE", "POST-GRADUATE", "PROFESSIONAL", "OTHERS"],
    )
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

    st.subheader("Business Interpretation")
    st.write(
        "This recommendation combines the Logistic Regression model probability with simple credit-policy rules. "
        "The final decision should support, not replace, bank policy and manual credit underwriting."
    )

