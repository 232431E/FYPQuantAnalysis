# Financial Analysis Platform API - Version 1.0.0

**Title**: Financial Analysis Platform API
**Version**: 1.0.0
**Date**: May 29, 2025 (Updated)
**Description**: API for accessing comprehensive financial data, AI-powered news analysis, interactive graph data, and administrative functions for prompt management.

## 1. Servers

**URL**: `http://localhost:8000` (Replace with your actual server URL)
**Description**: Local development server

## 2. Paths 
## 2.1. (Core Functionality - Completed/Implemented)
### 2.1.1. `/companies/{ticker}/financials` (GET)

**Summary**: Get historical financial data for a company.
**Description**: Retrieves financial data for a given stock ticker by fetching from the database and augmenting with real-time Yahoo Finance data. This endpoint is supported by `api.py`'s `get_company_financial_data(company_id)` which "Fetches financial data for a given company\_id from the database and augments it with real-time Yahoo Finance data (market cap, earnings date, dividends, etc.)."

**Parameters**:

  * `ticker` (path, string, **required**): The stock ticker symbol (e.g., `AAPL`).

**Responses**:

  * **200 OK**:
      * **Description**: Successful retrieval of financial data. The data returned will include historical OHLCV, market cap, earnings date, and dividends.
      * **Content** (`application/json`):
          * **Schema** (array of objects):
              * **items** (object):
                  * **properties**:
                      * `data_id` (integer)
                      * `company_id` (integer)
                      * `date` (string, format: date)
                      * `open` (number, format: float)
                      * `high` (number, format: float)
                      * `low` (number, format: float)
                      * `close` (number, format: float)
                      * `volume` (integer)
                      * `roi` (number, format: float)
                      * `eps` (number, format: float)
                      * `pe_ratio` (number, format: float)
                      * `revenue` (integer, format: int64)
                      * `debt_to_equity` (number, format: float)
                      * `cash_flow` (integer, format: int64)
                      * `created_at` (string, format: date-time)
                      * `updated_at` (string, format: date-time)
  * **404 Not Found**:
      * **Description**: Company not found or no financial data available.
  * **500 Internal Server Error**:
      * **Description**: Internal server error.

### 2.1.2 `/data/companies` (GET)

**Summary**: Get a list of all companies.
**Description**: Retrieves a paginated list of all companies stored in the database, with optional search and filtering capabilities.
**Source File**: backend/routes/data_routes.py
**Parameters**:

* `page` (query, integer, optional): Page number for pagination (default: 1).
* `per_page` (query, integer, optional): Number of companies per page (default: 10).
* `search` (query, string, optional): Search term for company name or ticker symbol.
* `industry` (query, string, optional): Filter by industry.

**Responses**:

* **200 OK**:
    * **Description**: Successful retrieval of the list of companies.
    * **Content** (`application/json`):
        * **Schema**:
            ```json
            {
              "companies": [
                {
                  "id": 1,
                  "name": "Company A",
                  "ticker": "CMA",
                  "exchange": "NASDAQ",
                  "industry": "Technology",
                  "created_at": "YYYY-MM-DDTHH:MM:SS",
                  "updated_at": "YYYY-MM-DDTHH:MM:SS"
                }
              ],
              "total_pages": 5,
              "current_page": 1,
              "total_companies": 50
            }
            ```

### 2.1.3. `/data/company/<int:company_id>` (GET)

**Summary**: Get details of a specific company.
**Description**: Retrieves detailed information for a single company based on its ID.
**Source File**: backend/routes/data_routes.py
**Parameters**:

* `company_id` (path, integer, **required**): The ID of the company.

**Responses**:

* **200 OK**:
    * **Description**: Successful retrieval of company details.
    * **Content** (`application/json`):
        * **Schema**:
            ```json
            {
              "company": {
                "id": 1,
                "name": "Company A",
                "ticker": "CMA",
                "exchange": "NASDAQ",
                "industry": "Technology",
                "created_at": "YYYY-MM-DDTHH:MM:SS",
                "updated_at": "YYYY-MM-DDTHH:MM:SS"
              },
              "company_news": [],
              "industry_news": []
            }
            ```
* **404 Not Found**:
    * **Description**: Company not found.

### 2.1.4. `/data/financials/<int:company_id>/<string:period>` (GET)

**Summary**: Get aggregated financial data for a company by period.
**Description**: Retrieves aggregated financial data (e.g., daily, weekly, monthly, yearly averages) for a given company ID.
**Source File**: backend/routes/data_routes.py
**Backend Service**: `data_service.py` provides functions like `get_daily_financial_data`, `get_weekly_financial_data`, `get_monthly_financial_data`, `get_yearly_financial_data`.
**Parameters**:

* `company_id` (path, integer, **required**): The ID of the company.
* `period` (path, string, **required**): The aggregation period (e.g., daily, weekly, monthly, yearly).

**Responses**:

* **200 OK**:
    * **Description**: Successful retrieval of aggregated financial data.
    * **Content** (`application/json`):
        * **Schema (example for daily)**:
            ```json
            [
              {
                "date": "YYYY-MM-DD",
                "open": 0.00,
                "high": 0.00,
                "low": 0.00,
                "close": 0.00,
                "volume": 0
              }
            ]
            ```
        * **Schema (example for monthly)**:
            ```json
            [
              {
                "month": "YYYY-MM",
                "avg_open": 0.00,
                "avg_close": 0.00,
                "total_volume": 0
              }
            ]
            ```
        * **Schema (example for yearly)**:
            ```json
            [
              {
                "year": "YYYY",
                "avg_open": 0.00,
                "avg_close": 0.00,
                "total_volume": 0
              }
            ]
            ```
* **400 Bad Request**:
    * **Description**: Invalid period specified.

### 2.1.5. `/graph/{company_id}/{timeframe}` (GET)

**Summary**: Get historical stock price and volume data for graphing a company.
**Description**: Retrieves historical close price and volume data for a given company and specified timeframe (weekly, monthly, yearly, max). This data is intended for frontend charting. This endpoint is directly supported by `graph_routes.py`'s `get_company_graph_data(company_id, timeframe)` and its helper `Workspace_graph_data`.

**Parameters**:

  * `company_id` (path, integer, **required**): The ID of the company.
  * `timeframe` (path, string, **required**): The desired timeframe for the data (e.g., `weekly`, `monthly`, `yearly`, `max`).

**Responses**:

  * **200 OK**:
      * **Description**: Successful retrieval of graph data.
      * **Content** (`application/json`):
          * **Schema** (object):
              * **properties**:
                  * `close_prices` (array of number)
                  * `volumes` (array of integer)
                  * `dates` (array of string, format: date)
  * **404 Not Found**:
      * **Description**: Company not found or no data for the specified timeframe.
  * **500 Internal Server Error**:
      * **Description**: Internal server error.

### 2.1.6. `/api/llm/sentiment/<int:company_id>` (GET)

**Summary**: Get a detailed news sentiment analysis report for a company based on a collection of recent news.
**Description**: Retrieves a comprehensive report on news sentiment, market outlook, key offerings, and significant financial dates for a given company. This analysis is performed using the Google Gemini API, specifically by taking a collection of the top 5-10 recent news articles from the database for the given company and generating an overall summary and sentiment report. This is a core feature, directly supported by `llm_routes.py`'s `get_company_news_sentiment(company_id)` which orchestrates the call to `llm_service.py`'s `analyze_news_sentiment_gemini`.

**Parameters**:

  * `company_id` (path, integer, **required**): The ID of the company.

**Responses**:

  * **200 OK**:
      * **Description**: Successful retrieval of the news analysis report.
      * **Content** (`application/json`):
          * **Schema** (object):
              * **properties**:
                  * `report` (object):
                      * `overall_news_summary` (string): A concise summary of the key news trends and events. HTML tags are used for emphasis.
                      * `brief_overall_sentiment` (string): A brief sentiment (e.g., "Positive", "Negative", "Mixed", "Neutral") accompanied by a confidence score out of 100 (e.g., "Mixed (Score: 60/100)"). Briefly explains the score.
                      * `reasons_for_sentiment` (string): A detailed explanation of why the overall sentiment is as it is, explicitly mentioning positive, negative, and neutral factors (including financial reports, political/geopolitical factors, environmental, and company structure/human factors) from the news that contribute to this sentiment. HTML tags are used for emphasis.
                      * `market_outlook` (string): Describes the potential near-term market outlook for this company based on the news, identifying key drivers. HTML tags are used for emphasis.
                      * `detailed_explanation` (string): Elaborates on the "Market Outlook," providing specific financial predictions, important financial news, and other relevant details that explain why the market outlook is as stated. HTML tags are used for emphasis.
                      * `key_offerings` (array of strings): A list of the company's best-selling or most significant products, services, and/or subsidiaries.
                      * `financial_dates` (array of objects): An array of objects, each representing a key financial event.
                          * **items** (object):
                              * **properties**:
                                  * `date` (string): The date of the event (e.g., "2025-05-15" or "Q3 2024").
                                  * `event` (string): A brief description of the event (e.g., "Q4 Earnings Call", "Investor Day", "Regulatory Decision on Merger").
                                  * `impact` (string): A short explanation of its potential or actual impact on market outlook and sentiment.
  * **404 Not Found**:
      * **Description**: Company not found or no news available for analysis.
  * **500 Internal Server Error**:
      * **Description**: Internal server error.

## 2.2 Analyst Specific Endpoints - To Be Implemented [already created]

### 2.2.1. `/prompts` (GET)

**Summary**: Get all LLM prompts (Analyst).
**Description**: Retrieves a list of all stored LLM prompts, as supported by the prompt management functions in `database.py`. Requires analyst role for access.

**Security**:

  * `BearerAuth`: `[]` (Placeholder for actual authentication)

**Responses**:

  * **200 OK**:
      * **Description**: Successful retrieval of prompts.
      * **Content** (`application/json`):
          * **Schema** (array of objects):
              * **items** (object):
                  * **properties**:
                      * `prompt_id` (integer)
                      * `name` (string)
                      * `description` (string)
                      * `created_by` (integer)
                      * `created_at` (string, format: date-time)
                      * `updated_at` (string, format: date-time)
  * **403 Forbidden**:
      * **Description**: Analyst role required.
  * **500 Internal Server Error**:
      * **Description**: Internal server error.

### 2.2.2. `/prompts` (POST)

**Summary**: Create a new LLM prompt (Analyst).
**Description**: Creates a new LLM prompt, utilizing `create_` functions in `database.py` for prompt entities. Requires analyst role.

**Security**:

  * `BearerAuth`: `[]` (Placeholder for actual authentication)

**Request Body** (`application/json`, **required**):

  * **Schema** (object):
      * **properties**:
          * `name` (string)
          * `description` (string)
      * **required**:
          * `name`
          * `description`

**Responses**:

  * **201 Created**:
      * **Description**: Successful creation of the prompt.
      * **Content** (`application/json`):
          * **Schema** (object):
              * **properties**:
                  * `prompt_id` (integer)
                  * `name` (string)
                  * `description` (string)
                  * `created_by` (integer)
                  * `created_at` (string, format: date-time)
                  * `updated_at` (string, format: date-time)
  * **400 Bad Request**:
      * **Description**: Invalid request body.
  * **403 Forbidden**:
      * **Description**: Analyst role required.
  * **500 Internal Server Error**:
      * **Description**: Internal server error.

### 2.2.3. `/prompts/{prompt_id}/versions` (GET)

**Summary**: Get all versions of a specific LLM prompt (Analyst).
**Description**: Retrieves all versions of the LLM prompt with the given ID, managed through `database.py` functions for prompt versions. Requires analyst role.

**Security**:

  * `BearerAuth`: `[]` (Placeholder for actual authentication)

**Parameters**:

  * `prompt_id` (path, integer, **required**): The ID of the prompt.

**Responses**:

  * **200 OK**:
      * **Description**: Successful retrieval of prompt versions.
      * **Content** (`application/json`):
          * **Schema** (array of objects):
              * **items** (object):
                  * **properties**:
                      * `prompt_version_id` (integer)
                      * `prompt_id` (integer)
                      * `user_id` (integer)
                      * `version` (integer)
                      * `operative` (boolean)
                      * `original_prompt` (string)
                      * `prompt_text` (string)
                      * `created_at` (string, format: date-time)
                      * `updated_at` (string, format: date-time)
  * **403 Forbidden**:
      * **Description**: Analyst role required.
  * **404 Not Found**:
      * **Description**: Prompt not found.
  * **500 Internal Server Error**:
      * **Description**: Internal server error.

### 2.2.4. `/prompts/{prompt_id}/versions` (POST)

**Summary**: Create a new version for a specific LLM prompt (Analyst).
**Description**: Creates a new version for the LLM prompt with the given ID, using `create_` functions in `database.py` for prompt versions. Requires analyst role.

**Security**:

  * `BearerAuth`: `[]` (Placeholder for actual authentication)

**Parameters**:

  * `prompt_id` (path, integer, **required**): The ID of the prompt.

**Request Body** (`application/json`, **required**):

  * **Schema** (object):
      * **properties**:
          * `original_prompt` (string)
          * `prompt_text` (string)
      * **required**:
          * `original_prompt`
          * `prompt_text`

**Responses**:

  * **201 Created**:
      * **Description**: Successful creation of the prompt version.
      * **Content** (`application/json`):
          * **Schema** (object):
              * **properties**:
                  * `prompt_version_id` (integer)
                  * `prompt_id` (integer)
                  * `user_id` (integer)
                  * `version` (integer)
                  * `operative` (boolean)
                  * `original_prompt` (string)
                  * `prompt_text` (string)
                  * `created_at` (string, format: date-time)
                  * `updated_at` (string, format: date-time)
  * **400 Bad Request**:
      * **Description**: Invalid request body.
  * **403 Forbidden**:
      * **Description**: Analyst role required.
  * **404 Not Found**:
      * **Description**: Prompt not found.
  * **500 Internal Server Error**:
      * **Description**: Internal server error.

### 2.2.5. `/prompts/versions/{prompt_version_id}/activate` (PATCH)

**Summary**: Set a specific prompt version as active (Analyst).
**Description**: Sets the prompt version with the given ID as the active version for its prompt, utilizing update functions in `database.py` to modify the `operative` status of a prompt version. Requires analyst role.

**Security**:

  * `BearerAuth`: `[]` (Placeholder for actual authentication)

**Parameters**:

  * `prompt_version_id` (path, integer, **required**): The ID of the prompt version to activate.

**Responses**:

  * **200 OK**:
      * **Description**: Successful activation of the prompt version.
      * **Content** (`application/json`):
          * **Schema** (object):
              * **properties**:
                  * `prompt_version_id` (integer)
                  * `prompt_id` (integer)
                  * `user_id` (integer)
                  * `version` (integer)
                  * `operative` (boolean)
                  * `original_prompt` (string)
                  * `prompt_text` (string)
                  * `created_at` (string, format: date-time)
                  * `updated_at` (string, format: date-time)
  * **403 Forbidden**:
      * **Description**: Analyst role required.
  * **404 Not Found**:
      * **Description**: Prompt version not found.
  * **500 Internal Server Error**:
      * **Description**: Internal server error.

## 2.3 To be Implemented
### 2.3.1 `/export/financials/{ticker}` (POST)

**Summary**: Export basic financial data to CSV for a company.
**Description**: Exports the historical financial data for a given ticker to a CSV file, which is returned as a download. This functionality would leverage financial data retrieval capabilities (e.g., via `data_routes.py`'s `get_financial_data`) and `pandas` for CSV generation.

**Parameters**:

  * `ticker` (path, string, **required**): The stock ticker symbol.

**Responses**:

  * **200 OK**:
      * **Description**: Successful export of financial data.
      * **Content** (`text/csv`):
          * **Schema** (string)
  * **404 Not Found**:
      * **Description**: Company not found or no financial data available.
  * **500 Internal Server Error**:
      * **Description**: Internal server error.

## 3. Core Database Models

The following SQLAlchemy models define the database schema:

### 3.1. User Model

**Description**: Represents user accounts.
**Source File**: backend/models/user_model.py
**Table Name**: `users`
**Columns**:
* `user_id` (INT, PRIMARY KEY, AUTO_INCREMENT)
* `username` (VARCHAR(255), UNIQUE, NOT NULL)
* `email` (VARCHAR(255), UNIQUE, NOT NULL)
* `password_hash` (VARCHAR(255),1 NOT NULL)
* `role` (VARCHAR(50), default='user')
* `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
* `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP2 ON UPDATE CURRENT_TIMESTAMP)
**Relationships**:
* `reports`: One-to-many with Report
* `feedbacks`: One-to-many with Feedback
* `prompt_versions`: One-to-many with PromptVersion

### 3.2. Company Model

**Description**: Represents companies for which financial data is tracked.
**Source File**: backend/models/data_model.py
**Table Name**: `companies`
**Columns**:
* `company_id` (INT, PRIMARY KEY, AUTO_INCREMENT)
* `company_name` (VARCHAR(255), NOT NULL)
* `ticker_symbol` (VARCHAR(20), UNIQUE, NOT NULL)
* `exchange` (VARCHAR(50))
* `industry` (VARCHAR(255))
* `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
* `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
**Relationships**:
* `financial_data`: One-to-many with FinancialData
* `reports`: One-to-many with Report
* `alerts`: One-to-many with Alert
* `news_items`: One-to-many with News

### 3.3. FinancialData Model

**Description**: Stores historical financial data for companies.
**Source File**: backend/models/data_model.py
**Table Name**: `financial_data`
**Columns**:
* `data_id` (INT, PRIMARY KEY, AUTO_INCREMENT)
* `company_id` (INT, FOREIGN KEY to companies.company_id, NOT NULL)
* `date` (DATE, NOT NULL)
* `open` (DECIMAL(10, 2))
* `high` (DECIMAL(10, 2))
* `low` (DECIMAL(10, 2))
* `close` (DECIMAL(10, 2))
* `volume` (BIGINT)
* `roi` (DECIMAL(10, 4))
* `eps` (DECIMAL(10, 4))
* `pe_ratio` (DECIMAL(10, 4))
* `revenue` (DECIMAL(15, 2))
* `debt_to_equity` (DECIMAL(10, 4))
* `cash_flow` (DECIMAL(15, 2))
* `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
* `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
**Relationships**:
* `company`: Many-to-one with Company

### 3.4. News Model

**Description**: Stores news articles related to companies.
**Source File**: backend/models/data_model.py
**Table Name**: `news`
**Columns**:
* `news_id` (INT, PRIMARY KEY, AUTO_INCREMENT)
* `company_id` (INT, FOREIGN KEY to companies.company_id, NOT NULL)
* `title` (VARCHAR(255), NOT NULL)
* `summary` (TEXT)
* `url` (VARCHAR(500))
* `published_at` (DATETIME, NOT NULL)
* `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
* `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
**Relationships**:
* `company`: Many-to-one with Company

### 3.5. Report Model

**Description**: Stores generated investment analysis reports.
**Source File**: backend/models/report_model.py
**Table Name**: `reports`
**Columns**:
* `report_id` (INT, PRIMARY KEY, AUTO_INCREMENT)
* `company_id` (INT, FOREIGN KEY to companies.company_id, NOT NULL)
* `user_id` (INT, FOREIGN KEY to users.user_id, NOT NULL)
* `report_date` (DATETIME)
* `content` (VARCHAR(1000))
* `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
* `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
**Relationships**:
* `company`: Many-to-one with Company
* `user`: Many-to-one with User
* `feedbacks`: One-to-many with Feedback

### 3.6. Alert Model

**Description**: Stores triggered alerts for companies.
**Source File**: backend/models/alert_model.py
**Table Name**: `alerts`
**Columns**:
* `alert_id` (INT, PRIMARY KEY, AUTO_INCREMENT)
* `company_id` (INT, FOREIGN KEY to companies.company_id, NOT NULL)
* `alert_type` (VARCHAR(50))
* `message` (VARCHAR(255))
* `triggered_at` (DATETIME, DEFAULT CURRENT_TIMESTAMP)
* `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
* `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP3 ON UPDATE CURRENT_TIMESTAMP)
**Relationships**:
* `company`: Many-to-one with Company

### 3.7. Feedback Model

**Description**: Stores user feedback on generated reports.
**Source File**: backend/models/feedback_model.py
**Table Name**: `feedback`
**Columns**:
* `feedback_id` (INT, PRIMARY KEY, AUTO_INCREMENT)
* `report_id` (INT, FOREIGN KEY to reports.report_id, NOT NULL)
* `user_id` (INT, FOREIGN KEY to users.user_id, NOT NULL)
* `feedback_text` (TEXT, NOT NULL)
* `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
* `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
**Relationships**:
* `report`: Many-to-one with Report
* `user`: Many-to-one with User

### 3.8. PromptVersion Model

**Description**: Manages versions of LLM prompts used for analysis.
**Source File**: backend/models/prompt_model.py
**Table Name**: `prompt_versions`
**Columns**:
* `prompt_version_id` (INT, PRIMARY KEY, AUTO_INCREMENT)
* `prompt_id` (INT, NOT NULL, INDEX)
* `user_id` (INT, FOREIGN KEY to users.user_id, NOT NULL)
* `version` (INT, NOT NULL)
* `operative` (BOOLEAN, DEFAULT TRUE)
* `original_prompt` (TEXT, NOT NULL)
* `prompt_text` (TEXT, NOT NULL)
* `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
* `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
**Relationships**:
* `user`: Many-to-one with User

## 4. Key Services

* **Data Acquisition & Processing**: `data_service.py` handles fetching historical financial data from Yahoo Finance and news from various sources (e.g., Guardian API). It also includes logic for saving this data to the database and checking for data freshness.
* **LLM Integration**: `llm_service.py` integrates with Google Gemini API for news summarization and sentiment analysis. It also includes a placeholder for Perplexity AI integration.
* **Database Management**: `database.py` manages database sessions and interactions, including functions for retrieving companies.
* **Scheduled Background Tasks**: Daily news and financial data updates are automated via `tasks.py` and `APScheduler`.



## 6. Software and API Dependencies
This section details the Python packages and external APIs used in the project, along with their installation commands and versions.
### 5.1. External APIs

  * **Google Gemini API**:
      * **Provider**: Google
      * **Models Used**: `gemini-2.0-flash-lite` (used for sentiment analysis in `llm_service.py` and `llm_routes.py`). `gemini-pro` may also be used for more complex prompt adherence.
      * **Description**: A powerful large language model used for sophisticated news sentiment analysis, market outlook generation, and identification of key company offerings and financial dates, primarily through the `analyze_news_sentiment_gemini` function, which processes a collection of recent news articles.
      * **Public API Link**: [Google Gemini API Documentation](https://ai.google.dev/docs/gemini_api_overview)
  * **Yahoo Finance**:
      * **Provider**: Yahoo
      * **Access Method**: Accessed indirectly via the `yfinance` Python library.
      * **Description**: Provides historical stock data (OHLCV, fundamentals), company information, and company-specific news, integral to functions like `Workspace_financial_data` and `Workspace_latest_news` in `data_service.py`.
      * **Public API Link**: While `yfinance` uses Yahoo Finance's public web scraping, there isn't a formal public API documentation link in the same way as Google Gemini.
  * **The Guardian API**:
      * **Provider**: The Guardian
      * **Description**: Used to fetch broader industry-specific news articles, as indicated by its mention in `Workspace_latest_news` in `data_service.py`.
      * **Public API Link**: [The Guardian Open Platform API](https://open-platform.theguardian.com/documentation/)
  * **Perplexity API (Planned/Placeholder)**:
      * **Provider**: Perplexity AI
      * **Description**: Mentioned as `analyze_news_sentiment_perplexity` in `llm_service.py`, but explicitly stated as "not updated yet & not in use". This indicates a **planned future integration** for alternative LLM-based sentiment analysis.
      * **Public API Link**: [Perplexity AI API Documentation](https://www.google.com/search?q=https://www.perplexity.ai/api)


## 7. File and Function Breakdown

### **`api.py`**

**Purpose**: Serves as a central blueprint for various API endpoints, particularly for retrieving company financial data.
**Key Functions (Completed/Implemented)**:

  * `format_market_cap(market_cap)`: Formats market capitalization into a human-readable string (e.g., T, B, M).
  * `get_company_financial_data(company_id)`: Fetches financial data for a given `company_id` from the database and augments it with real-time Yahoo Finance data (market cap, earnings date, dividends, etc.).

### **`app.py`**

**Purpose**: The main Flask application entry point. It sets up the Flask app, registers blueprints, initializes the database, configures CORS, schedules background tasks, and defines core routes.
**Key Functions (Completed/Implemented)**:

  * `create_app(testing, start_scheduler)`: Initializes and configures the Flask application.
  * `index()`: Redirects to the user dashboard.
  * `company_details()`: Renders the `company_details.html` page.
  * `company_detail_page(ticker)`: Renders the `company_details.html` page with a specific ticker.
  * `get_company_news(ticker)`: Fetches recent company and industry news for a given ticker, used by the frontend.

### **`config.py`**

**Purpose**: Stores configuration variables, primarily the database connection URL.
**Key Variables (Completed/Implemented)**:

  * `DATABASE_URL`: Defines the SQLAlchemy database connection string.

### **`database.py`**

**Purpose**: Manages database connections and provides CRUD (Create, Read, Update, Delete) operations for various models (Company, FinancialData, News, User, Prompt, PromptVersion, etc.). It ensures session management and proper transaction handling.
**Key Functions (Completed/Implemented)**:

  * `get_engine(app)`: Returns the SQLAlchemy engine.
  * `get_session_local(app)`: Returns a configured SQLAlchemy session factory.
  * `get_db()`: Provides a database session for request contexts.
  * `init_db(app)`: Initializes the database schema based on defined models.
  * `get_all_companies(db)`: Retrieves all companies.
  * `get_company_by_ticker(db, ticker)`: Retrieves a company by its ticker symbol.
  * `create_company(db, company_name, ticker_symbol, industry, exchange)`: Adds a new company.
  * *Numerous `get_`, `create_`, `update_`, `delete_` functions*: For `FinancialData`, `News`, `User`, `Prompt`, `PromptVersion`, etc., indicating full CRUD support for these models.

### **`tasks.py`**

**Purpose**: Defines background tasks that are scheduled to run periodically, such as daily news updates and daily financial data updates.
**Key Functions (Completed/Implemented)**:

  * `daily_news_update(app)`: Fetches and stores the latest news for all companies at a scheduled time.
  * `update_all_financial_data(app)`: Fetches and stores the latest financial data for all companies at a scheduled time.
  * `update_financial_data_for_company(db, company)`: Helper function to update financial data for a single company, used by `update_all_financial_data`.

### **`data_routes.py`**

**Purpose**: Defines API routes (Blueprint) related to fetching and managing financial data.
**Key Functions (Completed/Implemented)**:

  * `needs_update(db, company_id, threshold_hours)`: Checks if a company's financial data needs updating based on a timestamp.
  * `get_financial_data(period)`: Retrieves financial data for a selected company based on a specified period (daily, weekly, monthly, yearly).
  * `get_company_news()`: Retrieves stored news articles for a selected company.
    **Key Functions (Planned Priorities/Missing Content)**:
  * `ingest_data()`: (Placeholder/initial data ingestion, likely for testing or one-time setup). **This function is explicitly described as a placeholder, suggesting it's not a fully fleshed-out, active part of the API's operational data flow.**

### **`graph_routes.py`**

**Purpose**: Defines API routes (Blueprint) for retrieving data necessary to generate stock price and volume charts based on different timeframes.
**Key Functions (Completed/Implemented)**:

  * `Workspace_graph_data(db, company_id, timeframe)`: Fetches historical close price and volume data for a given company and timeframe (weekly, monthly, yearly, max).
  * `get_company_graph_data(company_id, timeframe)`: Endpoint to return the fetched graph data.

### **`llm_routes.py`**

**Purpose**: Defines API routes (Blueprint) specifically for interacting with LLM services, primarily for news sentiment analysis.
**Key Functions (Completed/Implemented)**:

  * `not_found(error)`: Custom error handler for 404 Not Found within this blueprint.
  * `get_company_news_sentiment(company_id)`: The core endpoint that retrieves news, constructs a detailed prompt, calls the LLM service (Gemini), and returns a comprehensive sentiment report, including market outlook, key offerings, and financial dates.

### **`data_service.py`**

**Purpose**: Contains business logic for fetching, storing, and processing financial data and news from external sources (yfinance, The Guardian API).
**Key Functions (Completed/Implemented)**:

  * `Workspace_financial_data(ticker, period, start, end, ...)`: Fetches historical OHLCV data from Yahoo Finance.
  * `store_financial_data(db, ticker, ...)`: Stores fetched financial data into the database.
  * `Workspace_historical_fundamentals(ticker)`: Fetches key fundamental data points.
  * `Workspace_latest_news(query, industry, exchange, ...)`: Fetches news from Yahoo Finance (for company) and The Guardian (for industry).
  * `store_news_articles(db, news_data, company_id)`: Stores fetched news articles into the database.
  * `get_stored_news(db, company_id, limit)`: Retrieves news articles from the database.
    **Key Functions (Planned Priorities/Missing Content)**:
  * `predict_financial_trends(financial_data)`: (Placeholder) Analyzes financial data to predict trends. **Explicitly stated as a placeholder, indicating planned but not implemented functionality. This is a high-value future feature for predictive analytics.**
  * `get_similar_companies(industry)`: (Placeholder) Provides a list of similar companies. **Explicitly stated as a placeholder, indicating planned but not implemented functionality. This would enhance comparative analysis.**

### **`llm_service.py`**

**Purpose**: Encapsulates the logic for interacting with various Large Language Models (LLMs), currently Google Gemini, to perform news sentiment analysis. It handles API calls, response parsing, and error handling for LLM interactions.
**Key Functions (Completed/Implemented)**:

  * `analyze_news_sentiment(news_articles, llm_provider, prompt, llm_model)`: A high-level function that dispatches to specific LLM providers (e.g., Gemini, Perplexity).
  * `analyze_news_sentiment_gemini(news_articles, prompt, llm_model)`: Specifically interacts with the Google Gemini API to analyze news sentiment, taking a custom prompt and processing a collection of news articles (e.g., top 5-10) to return a structured JSON response with detailed sentiment, market outlook, and financial dates.
    **Key Functions (Planned Priorities/Missing Content)**:
  * `analyze_news_sentiment_perplexity(news_articles, llm_model)`: (Placeholder/Not in use) Function for Perplexity API integration. **Explicitly noted as "not updated yet & not in use," confirming it's a planned integration but not yet active. This is a planned expansion for alternative LLM providers.**

-----

### **Summary of Priorities and Missing Content (Based on Actual File Content and Clarifications)**:

**Completed Priorities (Based on Described Functions in Files)**:

  * **Core Financial Data Retrieval**: The `/companies/{ticker}/financials` endpoint is fully supported, including real-time Yahoo Finance integration via `api.py`.
  * **Graph Data Retrieval**: The `/graph/{company_id}/{timeframe}` endpoint for fetching historical price and volume data for charting is fully supported by `graph_routes.py`. **This correctly replaces and confirms the absence of generic "visualization" endpoints.**
  * **Detailed LLM News Sentiment Analysis**: The `/api/llm/sentiment/<int:company_id>` endpoint is a robust, completed feature. It performs a **comprehensive overall sentiment analysis based on a collection of recent news articles** (e.g., top 5-10) using Google Gemini, as clarified.
  * **Data Export**: Exporting financial data to CSV (`/export/financials/{ticker}`) is covered.
  * **Analyst Prompt Management**: The full suite of prompt management endpoints (`/prompts`, `/prompts/{prompt_id}/versions`, `/prompts/versions/{prompt_version_id}/activate`) for CRUD and activation is well-defined and supported by `database.py`.
  * **Scheduled Background Tasks**: Daily news and financial data updates are automated via `tasks.py` and `APScheduler`.

## 8. Planned Priorities  
* **Predictive Financial Trends**: The `predict_financial_trends` function in `data_service.py` is a key placeholder. Its implementation would greatly enhance the platform's analytical capabilities by offering forward-looking insights.
* **Similar Companies Identification**: The `get_similar_companies` function in `data_service.py` is also a placeholder, indicating a planned feature for comparative analysis.
* **Perplexity AI API Integration**: The `analyze_news_sentiment_perplexity` function in `llm_service.py` is noted as "not updated yet & not in use," confirming a planned integration to diversify LLM providers for news sentiment analysis.

If you have any further updates or questions, feel free to ask!