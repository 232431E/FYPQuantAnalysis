-- backend/db/tables/prompts.sql
CREATE TABLE IF NOT EXISTS prompt_versions (
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
