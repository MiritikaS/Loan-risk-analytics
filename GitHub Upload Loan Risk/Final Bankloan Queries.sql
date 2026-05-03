USE BANKLOAN;
GO

--Basic Data Check

SELECT COUNT(*) AS Internal_Count
FROM dbo.Internal_Bank_Data;

SELECT COUNT(*) AS External_Count
FROM dbo.External_Cibil_Data;
GO


--PART 1: CREATE FINAL MERGED TABLE


DROP TABLE IF EXISTS dbo.FINAL_LOAN_DATA_RAW;
GO

SELECT
    c.*,
    b.Total_TL,
    b.Tot_Closed_TL,
    b.Tot_Active_TL,
    b.Total_TL_opened_L6M,
    b.Tot_TL_closed_L6M,
    b.pct_tl_open_L6M,
    b.pct_tl_closed_L6M,
    b.pct_active_tl,
    b.pct_closed_tl,
    b.Total_TL_opened_L12M,
    b.Tot_TL_closed_L12M,
    b.pct_tl_open_L12M,
    b.pct_tl_closed_L12M,
    b.Tot_Missed_Pmnt,
    b.Auto_TL,
    b.CC_TL,
    b.Consumer_TL,
    b.Gold_TL,
    b.Home_TL,
    b.PL_TL,
    b.Secured_TL,
    b.Unsecured_TL,
    b.Other_TL,
    b.Age_Oldest_TL,
    b.Age_Newest_TL
INTO dbo.FINAL_LOAN_DATA_RAW
FROM dbo.External_Cibil_Data c
INNER JOIN dbo.Internal_Bank_Data b
    ON c.PROSPECTID = b.PROSPECTID;
GO

SELECT COUNT(*) AS Final_Merged_Count
FROM dbo.FINAL_LOAN_DATA_RAW;
GO



--PART 2: CREATE CLEAN POWER BI / ANALYSIS VIEW


DROP VIEW IF EXISTS dbo.vw_POWERBI_LOAN_RISK;
GO

CREATE VIEW dbo.vw_POWERBI_LOAN_RISK AS
SELECT
    PROSPECTID,

    CASE
    WHEN TRY_CONVERT(FLOAT, Approved_Flag) = 1 THEN 'P1'
    WHEN TRY_CONVERT(FLOAT, Approved_Flag) = 2 THEN 'P2'
    WHEN TRY_CONVERT(FLOAT, Approved_Flag) = 3 THEN 'P3'
    WHEN TRY_CONVERT(FLOAT, Approved_Flag) = 4 THEN 'P4'
    ELSE 'Unknown'
END AS Approved_Flag,
    CONVERT(VARCHAR(10), GENDER) AS GENDER,
    CONVERT(VARCHAR(30), EDUCATION) AS EDUCATION,
    CONVERT(VARCHAR(20), MARITALSTATUS) AS MARITALSTATUS,

    TRY_CONVERT(FLOAT, Credit_Score) AS Credit_Score,
    TRY_CONVERT(FLOAT, NETMONTHLYINCOME) AS NETMONTHLYINCOME,
    TRY_CONVERT(FLOAT, Time_With_Curr_Empr) AS Time_With_Curr_Empr,

    TRY_CONVERT(FLOAT, Total_TL) AS Total_TL,
    TRY_CONVERT(FLOAT, Tot_Closed_TL) AS Tot_Closed_TL,
    TRY_CONVERT(FLOAT, Tot_Active_TL) AS Tot_Active_TL,
    TRY_CONVERT(FLOAT, Total_TL_opened_L6M) AS Total_TL_opened_L6M,
    TRY_CONVERT(FLOAT, Tot_TL_closed_L6M) AS Tot_TL_closed_L6M,
    TRY_CONVERT(FLOAT, Total_TL_opened_L12M) AS Total_TL_opened_L12M,
    TRY_CONVERT(FLOAT, Tot_TL_closed_L12M) AS Tot_TL_closed_L12M,
    TRY_CONVERT(FLOAT, Tot_Missed_Pmnt) AS Tot_Missed_Pmnt,

    TRY_CONVERT(FLOAT, Auto_TL) AS Auto_TL,
    TRY_CONVERT(FLOAT, CC_TL) AS CC_TL,
    TRY_CONVERT(FLOAT, Consumer_TL) AS Consumer_TL,
    TRY_CONVERT(FLOAT, Gold_TL) AS Gold_TL,
    TRY_CONVERT(FLOAT, Home_TL) AS Home_TL,
    TRY_CONVERT(FLOAT, PL_TL) AS PL_TL,
    TRY_CONVERT(FLOAT, Secured_TL) AS Secured_TL,
    TRY_CONVERT(FLOAT, Unsecured_TL) AS Unsecured_TL,
    TRY_CONVERT(FLOAT, Other_TL) AS Other_TL,

    NULLIF(TRY_CONVERT(FLOAT, Age_Oldest_TL), -99999) AS Age_Oldest_TL,
    NULLIF(TRY_CONVERT(FLOAT, Age_Newest_TL), -99999) AS Age_Newest_TL,

    NULLIF(TRY_CONVERT(FLOAT, time_since_recent_payment), -99999) AS time_since_recent_payment,
    NULLIF(TRY_CONVERT(FLOAT, time_since_first_deliquency), -99999) AS time_since_first_deliquency,
    NULLIF(TRY_CONVERT(FLOAT, time_since_recent_deliquency), -99999) AS time_since_recent_deliquency,

    TRY_CONVERT(FLOAT, num_times_delinquent) AS num_times_delinquent,
    NULLIF(TRY_CONVERT(FLOAT, max_delinquency_level), -99999) AS max_delinquency_level,
    TRY_CONVERT(FLOAT, max_recent_level_of_deliq) AS max_recent_level_of_deliq,

    TRY_CONVERT(FLOAT, num_deliq_6mts) AS num_deliq_6mts,
    TRY_CONVERT(FLOAT, num_deliq_12mts) AS num_deliq_12mts,
    TRY_CONVERT(FLOAT, num_deliq_6_12mts) AS num_deliq_6_12mts,

    TRY_CONVERT(FLOAT, num_times_30p_dpd) AS num_times_30p_dpd,
    TRY_CONVERT(FLOAT, num_times_60p_dpd) AS num_times_60p_dpd,

    NULLIF(TRY_CONVERT(FLOAT, tot_enq), -99999) AS tot_enq,
    NULLIF(TRY_CONVERT(FLOAT, CC_enq), -99999) AS CC_enq,
    NULLIF(TRY_CONVERT(FLOAT, CC_enq_L6m), -99999) AS CC_enq_L6m,
    NULLIF(TRY_CONVERT(FLOAT, CC_enq_L12m), -99999) AS CC_enq_L12m,
    NULLIF(TRY_CONVERT(FLOAT, PL_enq), -99999) AS PL_enq,
    NULLIF(TRY_CONVERT(FLOAT, PL_enq_L6m), -99999) AS PL_enq_L6m,
    NULLIF(TRY_CONVERT(FLOAT, PL_enq_L12m), -99999) AS PL_enq_L12m,
    NULLIF(TRY_CONVERT(FLOAT, enq_L3m), -99999) AS enq_L3m,
    NULLIF(TRY_CONVERT(FLOAT, enq_L6m), -99999) AS enq_L6m,
    NULLIF(TRY_CONVERT(FLOAT, enq_L12m), -99999) AS enq_L12m,

    NULLIF(TRY_CONVERT(FLOAT, CC_utilization), -99999) AS CC_utilization,
    NULLIF(TRY_CONVERT(FLOAT, PL_utilization), -99999) AS PL_utilization,
    NULLIF(TRY_CONVERT(FLOAT, pct_currentBal_all_TL), -99999) AS pct_currentBal_all_TL,
    NULLIF(TRY_CONVERT(FLOAT, max_unsec_exposure_inPct), -99999) AS max_unsec_exposure_inPct,

    TRY_CONVERT(INT, CC_Flag) AS CC_Flag,
    TRY_CONVERT(INT, PL_Flag) AS PL_Flag,

    /* Audit observation: HL_Flag and GL_Flag appear swapped */
    TRY_CONVERT(INT, GL_Flag) AS Corrected_HL_Flag,
    TRY_CONVERT(INT, HL_Flag) AS Corrected_GL_Flag,

    CASE
    WHEN TRY_CONVERT(FLOAT, Approved_Flag) IN (1, 2) THEN 0
    WHEN TRY_CONVERT(FLOAT, Approved_Flag) IN (3, 4) THEN 1
    ELSE NULL
END AS High_Risk_Target,

    CASE
        WHEN TRY_CONVERT(FLOAT, Credit_Score) < 600 THEN 'High Risk'
        WHEN TRY_CONVERT(FLOAT, Credit_Score) BETWEEN 600 AND 749 THEN 'Medium Risk'
        WHEN TRY_CONVERT(FLOAT, Credit_Score) >= 750 THEN 'Low Risk'
        ELSE 'Unknown'
    END AS Credit_Score_Risk_Band

FROM dbo.FINAL_LOAN_DATA_RAW;
GO

SELECT COUNT(*) AS PowerBI_View_Count
FROM dbo.vw_POWERBI_LOAN_RISK;
GO
SELECT 
    Approved_Flag,
    High_Risk_Target,
    COUNT(*) AS Customer_Count
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY Approved_Flag, High_Risk_Target
ORDER BY Approved_Flag;

--PART 3: KPI SUMMARY

SELECT
    COUNT(*) AS Total_Customers,

    AVG(TRY_CONVERT(FLOAT, Credit_Score)) AS Avg_Credit_Score,
    AVG(TRY_CONVERT(FLOAT, NETMONTHLYINCOME)) AS Avg_Monthly_Income,
    AVG(TRY_CONVERT(FLOAT, Tot_Missed_Pmnt)) AS Avg_Missed_Payments,
    AVG(TRY_CONVERT(FLOAT, Total_TL)) AS Avg_Total_Trade_Lines,
    SUM(TRY_CONVERT(FLOAT, Tot_Active_TL)) AS Total_Active_Trade_Lines,

    SUM(
        CASE 
            WHEN TRY_CONVERT(FLOAT, Approved_Flag) IN (3, 4)
            THEN 1 ELSE 0
        END
    ) AS High_Risk_Customers,

    SUM(
        CASE 
            WHEN TRY_CONVERT(FLOAT, Approved_Flag) IN (1, 2)
            THEN 1 ELSE 0
        END
    ) AS Low_Risk_Customers,

    ROUND(
        100.0 *
        SUM(
            CASE 
                WHEN TRY_CONVERT(FLOAT, Approved_Flag) IN (3, 4)
                THEN 1 ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS High_Risk_Percentage

FROM dbo.FINAL_LOAN_DATA_RAW;
GO

--PART 4: DESCRIPTIVE EDA
-- Approval flag distribution
SELECT
    Approved_Flag,
    COUNT(*) AS Customer_Count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS Customer_Percentage,
    AVG(Credit_Score) AS Avg_Credit_Score,
    AVG(NETMONTHLYINCOME) AS Avg_Income,
    AVG(Tot_Missed_Pmnt) AS Avg_Missed_Payments
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY Approved_Flag
ORDER BY Approved_Flag;
GO

-- Credit score risk band
SELECT
    Credit_Score_Risk_Band,
    COUNT(*) AS Customer_Count,
    AVG(Credit_Score) AS Avg_Credit_Score,
    AVG(NETMONTHLYINCOME) AS Avg_Income
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY Credit_Score_Risk_Band
ORDER BY Customer_Count DESC;
GO

-- Gender profile
SELECT
    GENDER,
    COUNT(*) AS Customer_Count,
    AVG(Credit_Score) AS Avg_Credit_Score,
    AVG(NETMONTHLYINCOME) AS Avg_Income,
    SUM(CASE WHEN High_Risk_Target = 1 THEN 1 ELSE 0 END) AS High_Risk_Customers
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY GENDER;
GO

-- Education profile
SELECT
    EDUCATION,
    COUNT(*) AS Customer_Count,
    AVG(Credit_Score) AS Avg_Credit_Score,
    AVG(NETMONTHLYINCOME) AS Avg_Income,
    SUM(CASE WHEN High_Risk_Target = 1 THEN 1 ELSE 0 END) AS High_Risk_Customers
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY EDUCATION
ORDER BY Customer_Count DESC;
GO

-- Marital status profile
SELECT
    MARITALSTATUS,
    COUNT(*) AS Customer_Count,
    AVG(Credit_Score) AS Avg_Credit_Score,
    AVG(NETMONTHLYINCOME) AS Avg_Income,
    SUM(CASE WHEN High_Risk_Target = 1 THEN 1 ELSE 0 END) AS High_Risk_Customers
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY MARITALSTATUS;
GO

-- Income band analysis
SELECT
    CASE
        WHEN NETMONTHLYINCOME < 15000 THEN 'Below 15K'
        WHEN NETMONTHLYINCOME BETWEEN 15000 AND 30000 THEN '15K-30K'
        WHEN NETMONTHLYINCOME BETWEEN 30001 AND 60000 THEN '30K-60K'
        WHEN NETMONTHLYINCOME > 60000 THEN 'Above 60K'
        ELSE 'Unknown'
    END AS Income_Band,
    COUNT(*) AS Customer_Count,
    AVG(Credit_Score) AS Avg_Credit_Score,
    AVG(Tot_Missed_Pmnt) AS Avg_Missed_Payments,
    SUM(CASE WHEN High_Risk_Target = 1 THEN 1 ELSE 0 END) AS High_Risk_Customers
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY
    CASE
        WHEN NETMONTHLYINCOME < 15000 THEN 'Below 15K'
        WHEN NETMONTHLYINCOME BETWEEN 15000 AND 30000 THEN '15K-30K'
        WHEN NETMONTHLYINCOME BETWEEN 30001 AND 60000 THEN '30K-60K'
        WHEN NETMONTHLYINCOME > 60000 THEN 'Above 60K'
        ELSE 'Unknown'
    END
ORDER BY Customer_Count DESC;
GO



--PART 5: LOAN AND PRODUCT ANALYSIS

-- Loan product distribution
SELECT
    SUM(Auto_TL) AS Auto_Loans,
    SUM(CC_TL) AS Credit_Cards,
    SUM(Consumer_TL) AS Consumer_Loans,
    SUM(Gold_TL) AS Gold_Loans,
    SUM(Home_TL) AS Home_Loans,
    SUM(PL_TL) AS Personal_Loans,
    SUM(Secured_TL) AS Secured_Trade_Lines,
    SUM(Unsecured_TL) AS Unsecured_Trade_Lines,
    SUM(Other_TL) AS Other_Trade_Lines
FROM dbo.vw_POWERBI_LOAN_RISK;
GO

-- Secured vs unsecured exposure
SELECT
    SUM(Secured_TL) AS Total_Secured_TL,
    SUM(Unsecured_TL) AS Total_Unsecured_TL,
    AVG(Secured_TL) AS Avg_Secured_TL,
    AVG(Unsecured_TL) AS Avg_Unsecured_TL
FROM dbo.vw_POWERBI_LOAN_RISK;
GO



--PART 6: DIAGNOSTIC ANALYSIS
-- High risk vs low/moderate risk comparison
SELECT
    CASE
        WHEN High_Risk_Target = 1 THEN 'High Risk'
        ELSE 'Low / Moderate Risk'
    END AS Risk_Group,
    COUNT(*) AS Customer_Count,
    AVG(Credit_Score) AS Avg_Credit_Score,
    AVG(NETMONTHLYINCOME) AS Avg_Income,
    AVG(tot_enq) AS Avg_Total_Enquiries,
    AVG(enq_L3m) AS Avg_Recent_Enquiries_L3M,
    AVG(num_times_delinquent) AS Avg_Delinquency_Count,
    AVG(Tot_Missed_Pmnt) AS Avg_Missed_Payments,
    AVG(CC_utilization) AS Avg_CC_Utilization,
    AVG(PL_utilization) AS Avg_PL_Utilization
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY
    CASE
        WHEN High_Risk_Target = 1 THEN 'High Risk'
        ELSE 'Low / Moderate Risk'
    END;
GO

-- Missed payment band
SELECT
    CASE
        WHEN Tot_Missed_Pmnt = 0 THEN 'No Missed Payment'
        WHEN Tot_Missed_Pmnt BETWEEN 1 AND 2 THEN '1-2 Missed Payments'
        WHEN Tot_Missed_Pmnt BETWEEN 3 AND 5 THEN '3-5 Missed Payments'
        ELSE 'More than 5 Missed Payments'
    END AS Missed_Payment_Band,
    COUNT(*) AS Customer_Count,
    AVG(Credit_Score) AS Avg_Credit_Score,
    SUM(CASE WHEN High_Risk_Target = 1 THEN 1 ELSE 0 END) AS High_Risk_Customers
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY
    CASE
        WHEN Tot_Missed_Pmnt = 0 THEN 'No Missed Payment'
        WHEN Tot_Missed_Pmnt BETWEEN 1 AND 2 THEN '1-2 Missed Payments'
        WHEN Tot_Missed_Pmnt BETWEEN 3 AND 5 THEN '3-5 Missed Payments'
        ELSE 'More than 5 Missed Payments'
    END;
GO

-- Delinquency band
SELECT
    CASE
        WHEN num_times_delinquent = 0 THEN 'No Delinquency'
        WHEN num_times_delinquent BETWEEN 1 AND 2 THEN '1-2 Delinquencies'
        WHEN num_times_delinquent BETWEEN 3 AND 5 THEN '3-5 Delinquencies'
        ELSE 'More than 5 Delinquencies'
    END AS Delinquency_Band,
    COUNT(*) AS Customer_Count,
    AVG(Credit_Score) AS Avg_Credit_Score,
    AVG(Tot_Missed_Pmnt) AS Avg_Missed_Payments,
    SUM(CASE WHEN High_Risk_Target = 1 THEN 1 ELSE 0 END) AS High_Risk_Customers
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY
    CASE
        WHEN num_times_delinquent = 0 THEN 'No Delinquency'
        WHEN num_times_delinquent BETWEEN 1 AND 2 THEN '1-2 Delinquencies'
        WHEN num_times_delinquent BETWEEN 3 AND 5 THEN '3-5 Delinquencies'
        ELSE 'More than 5 Delinquencies'
    END;
GO

-- Enquiry band
SELECT
    CASE
        WHEN tot_enq IS NULL THEN 'Missing'
        WHEN tot_enq = 0 THEN 'No Enquiry'
        WHEN tot_enq BETWEEN 1 AND 5 THEN '1-5 Enquiries'
        WHEN tot_enq BETWEEN 6 AND 10 THEN '6-10 Enquiries'
        ELSE 'More than 10 Enquiries'
    END AS Enquiry_Band,
    COUNT(*) AS Customer_Count,
    AVG(Credit_Score) AS Avg_Credit_Score,
    AVG(NETMONTHLYINCOME) AS Avg_Income,
    SUM(CASE WHEN High_Risk_Target = 1 THEN 1 ELSE 0 END) AS High_Risk_Customers
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY
    CASE
        WHEN tot_enq IS NULL THEN 'Missing'
        WHEN tot_enq = 0 THEN 'No Enquiry'
        WHEN tot_enq BETWEEN 1 AND 5 THEN '1-5 Enquiries'
        WHEN tot_enq BETWEEN 6 AND 10 THEN '6-10 Enquiries'
        ELSE 'More than 10 Enquiries'
    END;
GO



--PART 7: UTILIZATION ANALYSIS
-- Credit card utilization
SELECT
    CASE
        WHEN CC_utilization IS NULL THEN 'Missing / No CC'
        WHEN CC_utilization <= 0.30 THEN 'Low Utilization'
        WHEN CC_utilization <= 0.75 THEN 'Medium Utilization'
        WHEN CC_utilization > 0.75 THEN 'High Utilization'
    END AS CC_Utilization_Band,
    COUNT(*) AS Customer_Count,
    AVG(Credit_Score) AS Avg_Credit_Score,
    SUM(CASE WHEN High_Risk_Target = 1 THEN 1 ELSE 0 END) AS High_Risk_Customers
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY
    CASE
        WHEN CC_utilization IS NULL THEN 'Missing / No CC'
        WHEN CC_utilization <= 0.30 THEN 'Low Utilization'
        WHEN CC_utilization <= 0.75 THEN 'Medium Utilization'
        WHEN CC_utilization > 0.75 THEN 'High Utilization'
    END;
GO

-- Personal loan utilization
SELECT
    CASE
        WHEN PL_utilization IS NULL THEN 'Missing / No PL'
        WHEN PL_utilization <= 0.30 THEN 'Low Utilization'
        WHEN PL_utilization <= 0.75 THEN 'Medium Utilization'
        WHEN PL_utilization > 0.75 THEN 'High Utilization'
    END AS PL_Utilization_Band,
    COUNT(*) AS Customer_Count,
    AVG(Credit_Score) AS Avg_Credit_Score,
    SUM(CASE WHEN High_Risk_Target = 1 THEN 1 ELSE 0 END) AS High_Risk_Customers
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY
    CASE
        WHEN PL_utilization IS NULL THEN 'Missing / No PL'
        WHEN PL_utilization <= 0.30 THEN 'Low Utilization'
        WHEN PL_utilization <= 0.75 THEN 'Medium Utilization'
        WHEN PL_utilization > 0.75 THEN 'High Utilization'
    END;
GO



--PART 8: BUSINESS RISK SEGMENTATION


SELECT
    CASE
        WHEN Credit_Score < 600
          OR Tot_Missed_Pmnt > 2
          OR num_times_delinquent > 2
          OR CC_utilization > 0.75
          OR PL_utilization > 0.75
          OR tot_enq > 10
        THEN 'High Monitoring Required'

        WHEN Credit_Score BETWEEN 600 AND 700
          OR Tot_Missed_Pmnt BETWEEN 1 AND 2
          OR tot_enq BETWEEN 6 AND 10
        THEN 'Medium Monitoring Required'

        ELSE 'Low Monitoring Required'
    END AS Business_Risk_Segment,
    COUNT(*) AS Customer_Count,
    AVG(Credit_Score) AS Avg_Credit_Score,
    AVG(NETMONTHLYINCOME) AS Avg_Income,
    AVG(Tot_Missed_Pmnt) AS Avg_Missed_Payments
FROM dbo.vw_POWERBI_LOAN_RISK
GROUP BY
    CASE
        WHEN Credit_Score < 600
          OR Tot_Missed_Pmnt > 2
          OR num_times_delinquent > 2
          OR CC_utilization > 0.75
          OR PL_utilization > 0.75
          OR tot_enq > 10
        THEN 'High Monitoring Required'

        WHEN Credit_Score BETWEEN 600 AND 700
          OR Tot_Missed_Pmnt BETWEEN 1 AND 2
          OR tot_enq BETWEEN 6 AND 10
        THEN 'Medium Monitoring Required'

        ELSE 'Low Monitoring Required'
    END;
GO



--PART 9: HIGH RISK CUSTOMER LIST

SELECT TOP 100
    PROSPECTID,
    Approved_Flag,
    Credit_Score,
    Credit_Score_Risk_Band,
    NETMONTHLYINCOME,
    Tot_Missed_Pmnt,
    num_times_delinquent,
    tot_enq,
    CC_utilization,
    PL_utilization,
    Total_TL,
    Unsecured_TL
FROM dbo.vw_POWERBI_LOAN_RISK
WHERE Credit_Score < 600
   OR Tot_Missed_Pmnt > 2
   OR num_times_delinquent > 2
   OR CC_utilization > 0.75
   OR PL_utilization > 0.75
   OR tot_enq > 10
ORDER BY Credit_Score ASC, Tot_Missed_Pmnt DESC;
GO

SELECT TOP 10 *
FROM dbo.vw_POWERBI_LOAN_RISK;
GO