-- backend/db/tables/financial_data.sql
CREATE TABLE IF NOT EXISTS financial_data (
    data_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2),
    volume BIGINT,
    roi DECIMAL(10, 4),
    eps DECIMAL(10, 4),
    pe_ratio DECIMAL(10, 4),
    revenue DECIMAL(15, 2),
    debt_to_equity DECIMAL(10, 4),
    cash_flow DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);