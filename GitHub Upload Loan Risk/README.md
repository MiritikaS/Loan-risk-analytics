# Integrated Loan Risk Analytics and Loan Approval Recommendation App

## Project Overview

This Streamlit application is part of the Data-Powered Loan Risk Analytics project. The project uses internal bank data and external CIBIL data to identify high-risk loan applicants and support better loan approval decisions.

The app combines three major components:

1. EDA Analysis  
2. Live Interactive Dashboards  
3. Loan Approval Recommendation Tool  

This makes the application useful not only for prediction, but also for understanding the overall customer portfolio and credit behaviour patterns.

## Business Objective

The main business objective is to help the bank identify high-risk applicants before loan approval. Loan defaults can create financial losses and reduce portfolio quality. This app supports credit risk teams by showing risk insights and giving a recommendation for each applicant.

The app helps answer:

- What is the overall risk profile of the loan portfolio?
- How are customers distributed across approval tiers?
- Which indicators are linked to higher risk?
- How do credit score, enquiries, missed payments, delinquency and utilization affect risk?
- Should a new applicant be approved, manually reviewed or rejected?

## Tools Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Plotly
- Streamlit
- Joblib
- OpenPyXL

## Data Sources

The app uses two Excel datasets:

1. `INTERNAL_BANK_DATA.xlsx`  
   Contains internal bank-side details such as trade lines, active loans, closed loans, missed payments, secured loans, unsecured loans and loan product counts.

2. `EXTERNAL_CIBIL_DATA.xlsx`  
   Contains external CIBIL-side details such as credit score, enquiries, delinquency history, income, demographics, utilization and approval flag.

Both datasets are merged using:

```text
PROSPECTID
