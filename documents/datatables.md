MySQL Database Tables and Columns

users Table (backend/models/user_model.py)
SQL
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- e.g., 'user', 'staff', 'admin'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);



companies Table (backend/models/data_model.py)
SQL
CREATE TABLE companies (
    company_id INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(255) NOT NULL,
    ticker_symbol VARCHAR(20) UNIQUE NOT NULL,
    exchange VARCHAR(50), -- e.g., 'NYSE', 'NASDAQ'
    industry VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);



financial_data Table (backend/models/data_model.py)
SQL
CREATE TABLE financial_data (
    data_id INT PRIMARY KEY AUTO_INCREMENT,
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



news Table (backend/models/data_model.py)
SQL
CREATE TABLE news (
    news_id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(255),
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);



prompt_versions Table (backend/models/prompt_model.py)
SQL
CREATE TABLE prompt_versions (
    prompt_version_id INT PRIMARY KEY AUTO_INCREMENT,
    prompt_id INT NOT NULL,
    user_id INT NOT NULL,
    version INT NOT NULL,
    operative BOOLEAN DEFAULT TRUE,
    original_prompt TEXT NOT NULL,
    prompt_text TEXT NOT NULL, -- Current prompt text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);



reports Table (backend/models/report_model.py)
SQL
CREATE TABLE reports (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    user_id INT NOT NULL,
    report_content TEXT,
    report_format VARCHAR(50), -- e.g., 'PDF', 'Word', 'CSV'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    prompt_version_id INT, -- Foreign key referencing prompt_versions table
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (prompt_version_id) REFERENCES prompt_versions(prompt_version_id)
);



alerts Table (backend/models/alert_model.py)
SQL
CREATE TABLE alerts (
    alert_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    company_id INT NOT NULL,
    metric VARCHAR(50) NOT NULL, -- e.g., 'EPS', 'ROI'
    threshold DECIMAL(10, 4) NOT NULL,
    conditions VARCHAR(10) NOT NULL, -- e.g., '>', '<', '='
    notification_channel VARCHAR(50) NOT NULL, -- e.g., 'email', 'sms'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);



feedback Table (backend/models/feedback_model.py)
SQL
CREATE TABLE feedback (
    feedback_id INT PRIMARY KEY AUTO_INCREMENT,
    report_id INT NOT NULL,
    user_id INT NOT NULL,
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(report_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);



Views
weekly_financial_data
SQL
CREATE VIEW weekly_financial_data AS
SELECT
    company_id,
    DATE_FORMAT(created_at, '%Y-%u') AS week,
    AVG(open) AS avg_open,
    AVG(high) AS avg_high,
    AVG(low) AS avg_low,
    AVG(close) AS avg_close,
    SUM(volume) AS total_volume
FROM financial_data
GROUP BY company_id, week;


monthly_financial_data
SQL
CREATE VIEW monthly_financial_data AS
SELECT
    company_id,
    DATE_FORMAT(created_at, '%Y-%m') AS month,
    AVG(open) AS avg_open,
    AVG(high) AS avg_high,
    AVG(low) AS avg_low,
    AVG(close) AS avg_close,
    SUM(volume) AS total_volume
FROM financial_data
GROUP BY company_id, month;


yearly_financial_data
SQL
CREATE VIEW yearly_financial_data AS
SELECT
    company_id,
    YEAR(created_at) AS year,
    AVG(open) AS avg_open,
    AVG(high) AS avg_high,
    AVG(low) AS avg_low,
    AVG(close) AS avg_close,
    SUM(volume) AS total_volume
FROM financial_data
GROUP BY company_id, year;


avg_company_metrics
SQL
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


latest_company_financial_data
SQL
CREATE VIEW latest_company_financial_data AS
SELECT
    data_id, -- Include data_id to make the view distinct per row if MAX(date) doesn't guarantee uniqueness for all columns
    company_id,
    date AS latest_date, -- Use 'date' directly for latest_date
    open,
    high,
    low,
    close,
    volume,
    roi,
    eps,
    pe_ratio,
    revenue,
    debt_to_equity,
    cash_flow
FROM financial_data
WHERE (company_id, date) IN (
    SELECT company_id, MAX(date)
    FROM financial_data
    GROUP BY company_id
);


report_details
SQL
CREATE VIEW report_details AS
SELECT
    r.report_id,
    r.company_id,
    c.company_name,
    r.user_id,
    u.username,
    r.report_content,
    r.report_format,
    r.created_at,
    r.updated_at,
    pv.prompt_id,
    pv.version AS prompt_version,
    pv.prompt_text AS prompt_used
FROM reports r
JOIN companies c ON r.company_id = c.company_id
JOIN users u ON r.user_id = u.user_id
LEFT JOIN prompt_versions pv ON r.prompt_version_id = pv.prompt_version_id;


feedback_details
SQL
CREATE VIEW feedback_details AS
SELECT
    f.feedback_id,
    f.report_id,
    r.company_id,
    c.company_name,
    f.user_id,
    u.username,
    f.feedback_text,
    f.created_at,
    f.updated_at,
    pv.prompt_id,
    pv.version AS prompt_version,
    pv.prompt_text AS prompt_used
FROM feedback f
JOIN reports r ON f.report_id = r.report_id
JOIN companies c ON r.company_id = c.company_id
JOIN users u on f.user_id = u.user_id
LEFT JOIN prompt_versions pv ON r.prompt_version_id = pv.prompt_version_id;