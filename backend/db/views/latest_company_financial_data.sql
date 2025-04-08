CREATE VIEW latest_company_financial_data AS
SELECT fd.*
FROM financial_data fd
INNER JOIN (
    SELECT company_id, MAX(date) as max_date
    FROM financial_data
    GROUP BY company_id
) latest_dates ON fd.company_id = latest_dates.company_id AND fd.date = latest_dates.max_date;