Quant Analysis Platform
Overview
The Quant Analysis Platform is a web-based application designed to empower investors, financial analysts, data analysts, and quantitative traders with tools for comprehensive financial analysis, data visualization, and automated report generation. By leveraging large language models (LLMs) for news sentiment analysis and trend predictions, alongside financial data from external APIs, the platform delivers actionable insights for data-driven investment decisions. This README provides an overview of the project, its architecture, setup instructions, testing framework, and development guidelines to ensure a smooth handover to new developers.
Table of Contents

Project Purpose
Key Features
System Architecture
Technology Stack
Folder Structure
Setup Instructions
Prerequisites
Local Development Environment
Database Setup
Running the Application


Testing Framework
Test Coverage
Running Tests


Utility Scripts
Implementation Roadmap
Database Schema
API Endpoints
Scheduled Tasks
Frontend Functionality
Development Guidelines
Future Considerations
Contact

Project Purpose
The Quant Analysis Platform aims to provide:

Investors: Automated insights and visualizations for informed investment decisions.
Financial Analysts: Tools for in-depth analysis, prompt refinement, and report review.
System Administrators: User management and security controls.
Data Analysts/Researchers: Access to raw market data for modeling.
Quantitative Traders: Backtesting and strategy simulation capabilities.

The platform integrates external financial data (e.g., via yfinance, NewsAPI) and LLMs (e.g., Google Gemini, Perplexity) to generate reports, visualize trends, and provide actionable recommendations.
Key Features

Automated Investment Analysis Reports: Generate reports with LLM-driven news sentiment analysis and financial metrics.
Data Visualization: Display stock price, volume, and advanced charts (e.g., trendlines, LLM predictions).
User Management and Security: Role-based access (users, analysts, admins) with 2FA planned.
LLM Prompt Management: Analysts can create, version, and refine LLM prompts for analysis.
Report Review and Feedback: Analysts can review and optimize generated reports.
Market Data Access and Download: Export raw data in CSV format.
Backtesting and Strategy Simulation: Tools for testing trading strategies (future scope).
Financial Data Ingestion: Ingest and update financial data for individual or all companies.
Graph Data Retrieval: Fetch time-based financial data for visualization (daily, weekly, monthly, yearly, max).
News Sentiment Analysis: Analyze company and industry news using LLMs (Gemini, Perplexity).
Scheduled Data Updates: Daily financial data and news updates via APScheduler.
Interactive Dashboard: Filterable and paginated financial data display with industry and date filters.
Company Details Page: Detailed company information, financial data, and time-based stock charts.
Comprehensive Testing: Unit and integration tests for API endpoints, database operations, data services, news sentiment analysis, database views, and scheduled tasks.

System Architecture
The platform follows a microservices architecture with a clear separation of concerns:

Frontend (Bootstrap): Responsive UI for user interaction, developed in Visual Studio Code.
API Layer (API Gateway): Routes requests, handles authentication, and rate limiting.
Backend (Python Flask): Handles business logic, data processing, and LLM integration. Services include:
User Management
Data Acquisition & Storage
LLM Integration
Report Generation
Visualization
Alerting
Backtesting & Simulation
Data Download
Feedback & Review


Database (MySQL): Stores user data, financial data, news, reports, prompts, and feedback.
External Systems:
LLM APIs (e.g., Google Gemini, Perplexity) for sentiment analysis and predictions.
Financial Data APIs (e.g., yfinance, NewsAPI) for market and news data.
Notification Services (Email, SMS) for alerts.



Data Flow

Users interact with the Bootstrap frontend (dashboard.html, company_details.html).
Frontend sends API requests via the API Gateway to the Flask backend.
Backend processes requests, retrieves/stores data in MySQL, and interacts with external APIs/LLMs.
Processed data (e.g., reports, charts) is returned to the frontend for display.

Architecture Diagram
graph TD
    subgraph Quant Analysis Platform
        A[User (Investor, Analyst, Admin)] --> B(Frontend (Bootstrap))
        B --> C(API Layer)
        C --> D(Backend (Python Flask))
        D --> E(External System)
    end
    subgraph Frontend (Bootstrap)
        B1[Dashboard (dashboard.html)]
        B2[Company Details (company_details.html)]
    end
    subgraph API Layer
        C1[API Gateway]
    end
    subgraph Backend (Python Flask)
        D1[Python Flask Backend]
        D2[User Management Service]
        D3[Data Acquisition & Storage Service]
        D4[LLM Integration Service]
        D5[Report Generation Service]
        D6[Visualization Service]
        D7[Alerting Service]
        D8[Backtesting & Simulation Service]
        D9[Data Download Service]
        D10[Feedback & Review Service]
        D11[MySQL Database]
    end
    subgraph External System
        E1[LLM API (Google Gemini, Perplexity)]
        E2[Notification Services (Email, SMS)]
        E3[External Data Sources (yfinance, NewsAPI)]
    end

Technology Stack

Backend: Python Flask for API development.
Frontend: Bootstrap for responsive UI, jQuery for DOM manipulation, Chart.js for visualizations.
Database: MySQL for structured data storage (SQLite for testing).
ORM: SQLAlchemy for database interactions.
LLM Integration: Google Gemini, Perplexity for sentiment analysis and predictions.
Data Visualization: Chart.js for stock price and volume charts, Matplotlib/Seaborn/Plotly (backend, planned).
External APIs: yfinance for financial data, NewsAPI for industry news.
Scheduler: APScheduler for scheduled data updates.
Testing: unittest, pytest for unit and integration tests, unittest.mock for mocking.
Development Environment: Visual Studio Code.
Frontend Libraries:
Flatpickr for date pickers.
Select2 for dropdowns (industry filters).


Deployment: Planned for cloud (e.g., AWS, Azure) using Render.com for hosting.

Folder Structure
The project follows a modular structure for maintainability:
quant-analysis-platform/
├── backend/
│   ├── db/
│   │   ├── tables/           # SQL scripts for table creation
│   │   ├── views/            # SQL scripts for views
│   │   └── stored_procedures/ # SQL scripts for stored procedures
│   ├── models/               # SQLAlchemy models (e.g., user_model.py, data_model.py)
│   ├── routes/               # API route definitions (e.g., data_routes.py, prompt_routes.py)
│   ├── services/             # Business logic (e.g., data_service.py, llm_service.py)
│   ├── tests/                # Unit and integration tests
│   │   ├── test_api_endpoints.py
│   │   ├── test_db_connection.py
│   │   ├── test_database.py
│   │   ├── test_dashboard_api.py
│   │   ├── test_app.py
│   │   ├── test_news_retrieval.py
│   │   ├── test_data_service_sentiment.py
│   │   ├── test_data_service.py
│   │   ├── test_views.py
│   │   ├── test_tasks.py
│   ├── config.py             # Configuration (e.g., DATABASE_URL)
│   ├── database.py           # SQLAlchemy setup
│   ├── app.py                # Flask application setup
│   ├── api.py                # API endpoints
│   ├── tasks.py              # Scheduled tasks
│   ├── conftest.py           # Pytest configuration for testing
│   └── __init__.py           # Package initialization
├── frontend/
│   ├── static/
│   │   ├── css/             # Custom CSS (style.css)
│   │   └── js/              # JavaScript (dashboard.js, company_details.js)
│   └── templates/
│       ├── user/            # User-facing templates (dashboard.html, company_details.html)
│       └── staff/           # Analyst/admin templates (e.g., prompt_management.html)
├── scripts/
│   ├── setup_folders.py     # Script to create folder structure
│   └── check_data.py        # Utility script to check yfinance data
├── requirements.txt          # Python dependencies
└── README.md                # Project documentation

File Naming Conventions

Backend Models: *_model.py (e.g., user_model.py).
Backend Services: *_service.py (e.g., data_service.py).
Backend Routes: *_routes.py (e.g., data_routes.py).
SQL Scripts: table_*.sql, view_*.sql, sp_*.sql.
Frontend Templates: Role-based subfolders (e.g., user/, staff/).
Frontend JavaScript: Descriptive names (e.g., dashboard.js, company_details.js).
Test Files: test_*.py (e.g., test_api_endpoints.py).
Versioned Documents: HLD_DocV0.2.md, DLD_DocV0.2.md.

Setup Instructions
Prerequisites

Operating System: Windows (or compatible).
Software:
Python 3.9+
MySQL 8.0+
Visual Studio Code
Git


API Keys:
Financial data API (e.g., yfinance for testing).
NewsAPI key for industry news.
LLM API keys (e.g., Google Gemini, Perplexity).


Environment Variables:
DATABASE_URL: MySQL connection string (optional, defaults to config.py).
SECRET_KEY: Flask secret key.
GOOGLE_API_KEY: For Google Gemini LLM.
PERPLEXITY_API_KEY: For Perplexity LLM.
NEWS_API_KEY: For NewsAPI.
TEST_DATABASE_URL: SQLite in-memory database for testing (e.g., sqlite:///:memory:).



Local Development Environment

Clone the Repository:
git clone https://github.com/your-repo/quant-analysis-platform.git
cd quant-analysis-platform


Create Folder Structure:Run the provided script to set up the folder hierarchy:
python scripts/setup_folders.py


Install Dependencies:Create a virtual environment and install Python packages:
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt


Configure Environment:Create a backend/config.py with necessary configurations:
DATABASE_URL = "mysql+mysqlconnector://root:mySQL2025%21@localhost/fypquantanalysisplatform"
TEST_DATABASE_URL = "sqlite:///:memory:"

Set environment variables (e.g., in .env or shell):
export SECRET_KEY="your_default_secret_key"
export GOOGLE_API_KEY="your-google-api-key"
export PERPLEXITY_API_KEY="your-perplexity-api-key"
export NEWS_API_KEY="your-newsapi-key"



Database Setup

Install MySQL:

Download and install MySQL from mysql.com.
Configure with a root user and password.


Create Database:
CREATE DATABASE fypquantanalysisplatform;


Run Table Scripts:Execute SQL scripts from backend/db/tables/ to create tables based on the models:
mysql -u root -p fypquantanalysisplatform < backend/db/tables/users.sql
mysql -u root -p fypquantanalysisplatform < backend/db/tables/companies.sql
# Repeat for other tables (financial_data, news, reports, alerts, feedback, prompt_versions)

Example users.sql:
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


Run View Scripts:Execute scripts from backend/db/views/:
mysql -u root -p fypquantanalysisplatform < backend/db/views/weekly_financial_data.sql


Run Stored Procedures (if any):
mysql -u root -p fypquantanalysisplatform < backend/db/stored_procedures/report_generation.sql



Running the Application

Start the Backend:
cd backend
python app.py

The Flask app (app.py) initializes the application, registers blueprints (user_routes, data_routes, graph_routes, api, etc.), and starts APScheduler for daily tasks.

Serve the Frontend:

Ensure dashboard.html and company_details.html are in frontend/templates/user/.
Ensure dashboard.js and company_details.js are in frontend/static/js/.
Access the app at http://localhost:5000 (or configured port).


Deploy to Render.com (Optional):

Create a Render.com account.
Push the repo to GitHub.
Configure a new web service on Render, linking to the GitHub repo.
Set environment variables (DATABASE_URL, SECRET_KEY, GOOGLE_API_KEY, PERPLEXITY_API_KEY, NEWS_API_KEY).
Deploy with a command like gunicorn -w 4 -b 0.0.0.0:8000 app:app.



Testing Framework
The platform includes a comprehensive testing suite using unittest and pytest to ensure reliability of backend services, API endpoints, database operations, LLM integrations, database views, and scheduled tasks.
Test Coverage
The test files in backend/tests/ cover the following areas:

API Endpoints (test_api_endpoints.py, test_dashboard_api.py):
Tests for /api/companies/<company_id>/financials (daily, weekly, monthly, yearly) and /api/news.
Verifies response status codes, data structure, and content.
Uses Flask's test client and SQLite in-memory database for isolation.


Database Operations (test_db_connection.py, test_database.py, test_app.py):
Tests database connectivity and CRUD operations for companies, financial data, and news.
Validates creation, retrieval, and deletion of records using SQLAlchemy.
Uses pytest fixtures for database setup and teardown.


Data Service (test_data_service.py):
Tests financial data fetching (fetch_financial_data), storage (store_financial_data), and update checks (needs_financial_data_update).
Mocks yfinance responses to simulate successful, empty, and error scenarios.
Verifies data integrity (e.g., OHLCV, EPS, revenue) in the database.


News Retrieval (test_news_retrieval.py):
Tests daily_news_update function for fetching and storing news.
Validates duplicate prevention and handling of empty news data.
Mocks yfinance news responses.


News Sentiment Analysis (test_data_service_sentiment.py):
Tests analyze_news_sentiment for Perplexity and Gemini LLMs.
Verifies sentiment classification (Positive, Negative, Neutral, Mixed) for various news scenarios.
Mocks LLM API responses to test success, error, and empty cases.


Database Views (test_views.py):
Tests the weekly_financial_data view to ensure correct aggregation of financial data (e.g., average open, close, total volume).
Uses test data inserted into the database to verify view output.


Scheduled Tasks (test_tasks.py):
Tests daily_financial_data_update and daily_news_update functions.
Verifies behavior on weekdays (6:00 AM SGT) and weekends (no updates).
Mocks database sessions, company data, and external API calls to ensure correct task execution.


Pytest Configuration (conftest.py):
Defines fixtures for Flask app, SQLAlchemy engine, and database session.
Configures SQLite in-memory database for testing.



Running Tests

Install Test Dependencies:Ensure pytest, flask-testing, and unittest-mock are installed:
pip install pytest flask-testing unittest-mock


Run All Tests:Execute tests from the project root:
pytest backend/tests/

Or run specific test files:
pytest backend/tests/test_views.py


Run Unit Tests with unittest:For files using unittest (e.g., test_views.py, test_tasks.py):
python -m unittest backend/tests/test_views.py


Debugging Tests:

Enable verbose output:pytest -v backend/tests/


Use logging in test files (e.g., logging.info in test_data_service.py) for debugging.


Test Database Setup:

Tests use SQLite in-memory database (sqlite:///:memory:) for isolation, configured in conftest.py.
conftest.py provides fixtures (app, engine, db) for consistent test setup.



Utility Scripts

Check yfinance Data (scripts/check_data.py):
Purpose: Manually verifies if yfinance can fetch historical OHLCV data for given tickers and periods.
Usage:python scripts/check_data.py


Features:
Checks data for specified tickers (e.g., GOOGL, AMZN) over periods (e.g., 5y).
Supports custom date ranges.
Outputs data availability and sample rows.


Example Output:Successfully fetched historical OHLCV data for GOOGL for the period '5y':
... [data table]
Data spans from 2020-05-06 to 2025-05-06





Implementation Roadmap
The development is prioritized as follows (updated based on new files):

Data Acquisition and Storage (Priority 1, Mostly Implemented):

Implemented data_service.py for fetching/storing financial data (yfinance) and news (yfinance, NewsAPI).
Defined SQLAlchemy models in data_model.py, user_model.py, report_model.py, feedback_model.py, alert_model.py, prompt_model.py.
Created endpoints for data ingestion (/api/data/ingest/<ticker>, /api/data/ingest/all).
Implemented scheduled tasks (tasks.py) for daily financial data and news updates.
Tested data fetching, storage, update logic (test_data_service.py), and scheduled tasks (test_tasks.py).
Next: Enhance error handling for API rate limits, add more data providers.


LLM Integration and Analysis (Priority 2, Partially Implemented):

Implemented llm_service.py for news sentiment analysis using Google Gemini and Perplexity.
Implemented prompt_model.py and prompt_routes.py for LLM prompt management.
Endpoints for creating, retrieving, updating, and deleting prompt versions (/prompts, /prompts/<prompt_version_id>, etc.).
Tested sentiment analysis for various scenarios (test_data_service_sentiment.py).
Next: Implement trend prediction logic, test LLM response quality, integrate sentiment analysis in frontend.


Report Generation and Feedback (Priority 3, Partially Implemented):

Defined report_model.py and feedback_model.py for report and feedback storage.
Next: Implement report_service.py and feedback_service.py, create API endpoints, develop staff review pages.


Data Visualization and Download (Priority 4, Partially Implemented):

Implemented graph_routes.py for fetching time-based financial data (/api/graph/company/<company_id>/<timeframe>).
Implemented dashboard.js and company_details.js for frontend visualization using Chart.js.
Tested financial data endpoints (test_dashboard_api.py) and database views (test_views.py).
Next: Develop visualization_service.py for chart generation, implement download_service.py for CSV exports, enhance frontend charts.


Alerting and Backtesting (Priority 5, Partially Implemented):

Defined alert_model.py for alert storage.
Next: Implement alerting_service.py and backtesting_service.py, test notifications and simulations.


User and Prompt Management (Priority 6, Mostly Implemented):

Implemented user_model.py for user management.
Prompt management implemented via prompt_routes.py.
Next: Develop user_service.py for role-based access, create prompt management UI.



Database Schema
The MySQL database includes the following core tables (based on provided models):

users (user_model.py):

user_id (INT, PK, AUTO_INCREMENT)
username (VARCHAR(255), UNIQUE, NOT NULL)
email (VARCHAR(255), UNIQUE, NOT NULL)
password_hash (VARCHAR(255), NOT NULL)
role (VARCHAR(50), DEFAULT 'user')
created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
updated_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP, ON UPDATE)


companies (data_model.py):

company_id (INT, PK, AUTO_INCREMENT)
company_name (VARCHAR(255), NOT NULL)
ticker_symbol (VARCHAR(20), UNIQUE, NOT NULL)
exchange (VARCHAR(50))
industry (VARCHAR(255))
created_at (DATETIME, DEFAULT NOW())
updated_at (DATETIME, DEFAULT NOW(), ON UPDATE)


financial_data (data_model.py):

data_id (INT, PK, AUTO_INCREMENT)
company_id (INT, FK to companies.company_id, NOT NULL)
date (DATE, NOT NULL)
open, high, low, close (NUMERIC(10,2))
volume (BIGINT)
roi, eps, pe_ratio (NUMERIC(10,4))
revenue, cash_flow (NUMERIC(15,2))
debt_to_equity (NUMERIC(10,4))
created_at, updated_at (DATETIME)


news (data_model.py):

news_id (INT, PK, AUTO_INCREMENT)
company_id (INT, FK to companies.company_id, NOT NULL)
title (VARCHAR(255))
link (VARCHAR(500))
published_date (DATETIME)
summary (TEXT)
created_at, updated_at (DATETIME)


reports (report_model.py):

report_id (INT, PK, AUTO_INCREMENT)
company_id (INT, FK to companies.company_id, NOT NULL)
user_id (INT, FK to users.user_id, NOT NULL)
report_date (DATETIME)
content (VARCHAR(1000))
created_at, updated_at (DATETIME)


alerts (alert_model.py):

alert_id (INT, PK, AUTO_INCREMENT)
company_id (INT, FK to companies.company_id, NOT NULL)
alert_type (VARCHAR(50))
message (VARCHAR(255))
triggered_at, created_at, updated_at (DATETIME)


feedback (feedback_model.py):

feedback_id (INT, PK, AUTO_INCREMENT)
report_id (INT, FK to reports.report_id, NOT NULL)
user_id (INT, FK to users.user_id, NOT NULL)
feedback_text (TEXT, NOT NULL)
created_at, updated_at (DATETIME)


prompt_versions (prompt_model.py):

prompt_version_id (INT, PK, AUTO_INCREMENT)
prompt_id (INT, NOT NULL, INDEX)
user_id (INT, FK to users.user_id, NOT NULL)
version (INT, NOT NULL)
operative (BOOLEAN, DEFAULT True)
original_prompt, prompt_text (TEXT, NOT NULL)
created_at, updated_at (DATETIME)



Views

weekly_financial_data, monthly_financial_data, yearly_financial_data: Aggregate financial data by time period.
avg_company_metrics: Average metrics per company.
latest_company_financial_data: Latest financial data per company.
report_details, feedback_details: Join tables for report and feedback details.

API Endpoints
Key endpoints:

API Routes (api.py):

GET /api/data/dashboard/latest: Retrieve latest financial data for all companies (for dashboard).
GET /api/company/: Retrieve company details, financial data, news, and placeholders for trend predictions and sentiment analysis.
GET /api/company//stock_data?timeframe={1w|1m|1y|all}: Fetch stock data by timeframe (weekly, monthly, yearly, all).
GET /api/company//financial_data: Retrieve latest financial data for a company.
GET /api/company//news: Fetch company and industry news.


Data Routes (data_routes.py):

POST /api/data/ingest/: Ingest financial data for a specific ticker.
POST /api/data/ingest/all: Trigger financial data update for all companies.
GET /api/data/dashboard/latest: Retrieve all financial data for all companies.
GET /api/data/companies//financials?period={daily|weekly|monthly|yearly}: Get financial data for a company by period.
GET /api/data/news: Fetch news for a selected company (based on session).


Graph Routes (graph_routes.py):

GET /api/graph/company//: Fetch financial data (close, volume) for a company by timeframe (weekly, monthly, yearly, max).


Prompt Routes (prompt_routes.py):

POST /prompts: Create a new prompt version.
GET /prompts/: Retrieve a specific prompt version.
GET /prompts/prompt_id/: Get all versions for a prompt ID.
GET /prompts/operative: Get all operative prompt versions.
PUT /prompts/: Update a prompt version.
DELETE /prompts/: Delete a prompt version.


Planned Endpoints:

GET /premium_visualizations/{ticker}/advanced_price: Advanced price chart (premium).
GET /news_analysis/{ticker}: Detailed news analysis report (premium).
POST /export/financials/{ticker}: Export financial data to CSV.
Endpoints for report generation, feedback, and backtesting.



Scheduled Tasks
The platform uses APScheduler (app.py, __init__.py, tasks.py) to automate data updates:

Daily News Update:

Schedule: 6:00 AM SGT, Monday–Friday.
Task: daily_news_update fetches and stores company and industry news using yfinance and NewsAPI.
Implementation: tasks.py, triggered via APScheduler in app.py.
Tested: test_news_retrieval.py, test_tasks.py.


Daily Financial Data Update:

Schedule: 6:00 AM SGT, Monday–Friday.
Task: daily_financial_data_update fetches and stores the latest financial data for all companies.
Implementation: tasks.py, triggered via APScheduler in __init__.py.
Tested: test_data_service.py, test_tasks.py.


Batched Financial Data Update:

Schedule: 2:43 PM SGT, Monday–Friday (example from app.py).
Task: update_all_financial_data updates financial data in batches with delays to avoid API rate limits.
Implementation: tasks.py, triggered via APScheduler in app.py.



Frontend Functionality
The frontend is implemented using Bootstrap, jQuery, Chart.js, Flatpickr, and Select2, with key pages described below:
Dashboard (dashboard.html, dashboard.js)

Purpose: Displays a filterable and paginated table of financial data for all companies.
Features:
Data Ingestion: Users can input a ticker symbol to ingest financial data via /api/data/ingest/<ticker>.
Data Display: Fetches latest financial data (/api/data/dashboard/latest) and displays in a table with columns for company ticker, date, open, high, low, close, and volume.
Filtering: Supports search by company name or ticker, industry filtering via checkboxes, and date range filtering using Flatpickr.
Pagination: Configurable rows per page (10, 25, 50, 100, 200) with dynamic pagination controls.
Refresh: Button to refresh the table data.
Responsive Design: Uses Bootstrap for layout, with collapsible filter container.


JavaScript Logic (dashboard.js):
Initializes Flatpickr for date pickers and Select2 for industry dropdown (though currently using checkboxes).
Handles data fetching, filtering, and pagination dynamically.
Updates the UI based on user interactions (search, filter changes, page navigation).



Company Details (company_details.html, company_details.js)

Purpose: Displays detailed information for a specific company, including financial data, stock charts, news, and sentiment analysis.
Features:
Company Information: Displays company name, ticker, exchange, and industry via /api/company/<ticker>.
Financial Data: Shows latest financial metrics (e.g., close, open, volume, market cap) in a two-column table via /api/company/<company_id>/financial_data.
Stock Charts: Displays price (line chart) and volume (bar chart) for weekly, monthly, yearly, or max timeframes via /api/graph/company/<company_id>/<timeframe>, using Chart.js.
News and Sentiment: Placeholder sections for news summary, sentiment analysis, top news, and similar companies (to be implemented).
Timeframe Selection: Tabbed interface for selecting chart timeframes (weekly, monthly, yearly, max).
Responsive Design: Bootstrap-based layout with centered financial data table and styled sections.


JavaScript Logic (company_details.js):
Fetches company details and financial data using jQuery AJAX.
Renders dynamic charts with Chart.js, destroying previous charts to prevent memory leaks.
Formats financial data (e.g., market cap in millions/billions/trillions) for readability.
Handles timeframe tab switching and URL parameter parsing for ticker.



Development Guidelines

Agile Methodology: Use iterative development with CI/CD (planned).
Testing:
Write unit tests for backend services (backend/tests/).
Test frontend JavaScript (dashboard.js, company_details.js) with tools like Jest.
Test API endpoints with Postman or curl.
Validate LLM responses, database views, and scheduled tasks.
Use pytest fixtures (conftest.py) for consistent test setup.


Version Control:
Use Git with descriptive commit messages.
Maintain versioned documents (e.g., HLD_DocV0.2.md).


Security:
Implement 2FA and data encryption (future).
Secure API keys in environment variables.
Sanitize user inputs in dashboard.js (e.g., ticker input).


LLM-Driven Development:
Use LLM prompts for code snippets, best practices, and optimization.
Store and version prompts in prompt_versions table.


Logging:
Use Python’s logging module for backend (data_service.py, llm_service.py, tasks.py).
Use console.log with [DEBUG] or [ERROR] prefixes in frontend JavaScript for debugging.
Enable debug logging in tests (e.g., logging.basicConfig(level=logging.DEBUG) in test_data_service.py).


Documentation:
Update README with major changes.
Maintain API docs and design documents.
Comment JavaScript functions and test cases for clarity.



Future Considerations

Implement news and sentiment analysis sections in company_details.html using /api/company/<ticker>/news.
Integrate additional financial data providers (e.g., Finnhub, EODHD).
Implement advanced LLM capabilities for trend predictions and report generation.
Develop mobile app and customizable dashboards.
Enhance A/B testing for LLM prompts.
Add real-time data and webhook support.
Complete implementation of report generation, feedback, visualization, and backtesting services.
Optimize scheduled tasks for scalability and rate limit handling.
Enhance frontend with advanced charting options (e.g., Plotly) and export functionality.
Expand test coverage for frontend JavaScript and edge cases.

Contact
For questions or support, contact the project maintainer at [your-email@example.com] or open an issue on the GitHub repository.

Generated on May 06, 2025
