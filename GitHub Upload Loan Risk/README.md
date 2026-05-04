# Data-Powered Loan Risk Analytics

This project identifies high-risk loan applicants using internal bank data and external CIBIL data.

## Tools Used
- SQL Server
- Power BI
- Python
- Streamlit

## Files Included
- Final Bankloan Queries.sql: SQL cleaning, EDA and KPI queries
- loan_approval_recommendation_model.py: Python model training code
- loan_approval_recommendation_app.py: Streamlit web app code
- requirements.txt: Python package requirements

## Python App
The app gives a loan approval recommendation:
- Approve
- Manual Review
- Reject / Very Strict Review

## How To Run
Install packages:
pandas
numpy
scikit-learn
joblibs
streamlit
openpyxl



```bash
pip install -r requirements.txt

Train model:
python loan_approval_recommendation_model.py

Run app:
python -m streamlit run loan_approval_recommendation_app.py

Demo App Login Link :
Local URL: http://localhost:8501
Network URL: http://192.168.1.49:8501


Demo Login - Loan_approval_recommend
User ID: faculty
Password: loanapproval123

GitHub Repositary Link - https://github.com/MiritikaS/Loan-risk-analytics 

