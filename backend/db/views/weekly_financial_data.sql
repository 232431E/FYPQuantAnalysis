CREATE VIEW weekly_financial_data AS
SELECT
    company_id,
    DATE_FORMAT(date, '%Y-%u') AS week,
    AVG(open) AS avg_open,
    AVG(high) AS avg_high,
    AVG(low) AS avg_low,
    AVG(close) AS avg_close,
    SUM(volume) AS total_volume,
    AVG(roi) AS avg_roi
FROM financial_data
GROUP BY company_id, week;