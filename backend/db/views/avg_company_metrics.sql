CREATE VIEW avg_company_metrics AS
SELECT
    company_id,
    AVG(roi) AS avg_roi,
    AVG(eps) AS avg_eps,
    AVG(pe_ratio) AS avg_pe_ratio,
    AVG(revenue) AS avg_revenue,
    AVG(debt_to_equity) AS avg_debt_to_equity,
    AVG(cash_flow) AS avg_cash_flow
FROM financial_data
GROUP BY company_id;