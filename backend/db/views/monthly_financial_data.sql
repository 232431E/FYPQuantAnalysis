CREATE VIEW monthly_financial_data AS
SELECT
    company_id,
    DATE_FORMAT(date, '%Y-%m') AS month,
    AVG(open) AS avg_open,
    AVG(high) AS avg_high,
    AVG(low) AS avg_low,
    AVG(close) AS avg_close,
    SUM(volume) AS total_volume,
    AVG(roi) AS avg_roi
FROM financial_data
GROUP BY company_id, month;