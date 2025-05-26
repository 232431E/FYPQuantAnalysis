-- backend/db/tables/reports.sql
CREATE TABLE IF NOT EXISTS reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    user_id INT NOT NULL,
    report_content TEXT,
    report_format VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    prompt_version_id INT, -- Foreign key referencing prompt_versions table
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (prompt_version_id) REFERENCES prompt_versions(prompt_version_id)
);