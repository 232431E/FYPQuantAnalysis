-- backend/db/tables/prompts.sql
CREATE TABLE IF NOT EXISTS prompts (
    prompt_id INT AUTO_INCREMENT PRIMARY KEY,
    prompt_name VARCHAR(255) NOT NULL,
    prompt_text TEXT NOT NULL,
    version INT NOT NULL,
    operative BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (prompt_name, version) -- Ensure unique prompt versions
);