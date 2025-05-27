Implementation Guide

Table of Contents
1.  Prerequisites
Software Requirements
External API Keys
2.  Repository Setup
Cloning the Repository (Recommended)
Connecting Existing Local Files to GitHub
3.  Implementation Roadmap (Prioritized)
Priority 1: Data Acquisition and Storage (Detailed)
Priority 2: LLM Integration and Analysis (Detailed)
Priority 3: Report Generation and Feedback (Detailed)
Priority 4: Data Visualization and Download
Priority 5: Alerting and Backtesting
Priority 6: User and Prompt Management
4.  Backend Setup
Environment Configuration
Database Setup
Installing Dependencies
Running the Backend
5.  Frontend Setup
Setting up the Frontend Environment
Running the Frontend
6.  External API Integration
LLM API
Financial Data APIs
Notification Services (for Alerting)
7.  Database Schema
Overview of Tables
SQL Scripts
8.  Running Tests
Backend Tests
Frontend Tests (if applicable)
9.  Deployment (Optional)
Deployment Strategies
10. Contributing
11. License

1. Prerequisites

Before you begin, ensure you have the following software installed on your system:

Python: Version 3.11.3 or higher. You can download it from [python.org](https://www.python.org/downloads/).
pip: Python package installer (should come with Python 3.11.3).
MySQL: Version [Specify Minimum Required Version]. You can download it from [MySQL Downloads](https://dev.mysql.com/downloads/).
Node.js and npm (for frontend): Version [Specify Minimum Required Version]. You can download them from [nodejs.org](https://nodejs.org/).
Git: Version [Specify Minimum Required Version]. You can download it from [git-scm.com](https://git-scm.com/downloads).
ORM: Install SqlAlchemy ORM (for MySQL)

External API Keys

You will need to obtain API keys for the following external services:
LLM Provider: (e.g., Gemini, Perplexity). Sign up on their platform and obtain your API key.
Financial Data API(s): (Specify which APIs are intended to be used, e.g., yahoo finance (yfinance), Alpha Vantage, IEX Cloud). Sign up and obtain the necessary API keys.
Notification Service (for Alerting): (e.g., Twilio for SMS, SendGrid for email). Sign up and obtain the required credentials/API keys.

2. Repository Setup (NEEDS TO BE FILLED UP)


3. Implementation Roadmap (Prioritized)
Priority 1: Data Acquisition and Storage (Detailed)
Goal: Implement the foundation for acquiring and storing financial data in the MySQL database, including basic aggregation views.

Detailed Implementation Steps:
1.  Database Table Creation (backend/db/tables/\.sql):
     Task 1.3: Create the following SQL files in the `backend/db/tables/` directory:
`users.sql`: Define the schema for the `users` table (as specified in the "MySQL Database Tables and Columns" section).
`companies.sql`: Define the schema for the `companies` table.
`financial_data.sql`: Define the schema for the `financial_data` table, ensuring the `company_id` foreign key constraint referencing `companies.company_id` is included.
Execute these SQL scripts against your MySQL database using the `mysql` command-line tool or a database client.

2.  Data Model Implementation (backend/models/data_model.py):
Create the `backend/models/data_model.py` file.
Define Python classes that represent the `Company` and `FinancialData` entities. If you plan to use an ORM like SQLAlchemy, define these as SQLAlchemy models. Otherwise, you can start with simple classes to hold data. Ensure the attributes of these classes map to the columns defined in your SQL table schemas.

3.  Database Operations (backend/database.py):
Implement `backend/database.py` to handle the connection to your MySQL database. This might involve using a library like `mysql.connector` or an ORM.
 Task 1.4: Implement basic CRUD (Create, Read, Update, Delete) functions for the `Company` and `FinancialData` models. These functions will interact with your MySQL database to store and retrieve data.

4.  Data Ingestion Scripts/Functions (backend/services/data_service.py - Task 1.1):
Create the `backend/services/data_service.py` file.
Implement functions to fetch financial data from a chosen external API (e.g., Alpha Vantage, using the `requests` library).
Focus on fetching data for a specific company (based on its ticker symbol).
Handle API authentication (using your API key).
Parse the JSON or CSV response from the API to extract relevant financial data points (open, high, low, close, volume, and potentially others you need for initial views like ROI, EPS).

5.  Data Validation and Cleaning Routines (backend/services/data_service.py - Task 1.2):
Within `data_service.py`, implement functions to validate the fetched data:
Check for missing values.
Ensure data types are correct.
Implement basic cleaning steps if necessary (e.g., converting string representations of numbers to numerical types).

6.  Data Storage Implementation (backend/services/data_service.py - Task 1.4 continued):
Integrate the data fetching and validation functions with the database operations. After fetching and cleaning data for a company, use the CRUD functions from `backend/database.py` to store this data in the `companies` and `financial_data` tables. You'll likely need to first check if the company exists in the `companies` table and add it if not.

7.  Data Aggregation and Latest Data Views (backend/db/views/\.sql - Tasks 1.5 & 1.6):
     Create the following SQL view scripts in `backend/db/views/`:
`weekly_financial_data.sql`: Create a view that aggregates `financial_data` into weekly summaries (e.g., average closing price for each week).
`monthly_financial_data.sql`: Create a view for monthly summaries.
`yearly_financial_data.sql`: Create a view for yearly summaries.
`avg_company_metrics.sql`: Create a view that calculates average metrics (e.g., average ROI, EPS, P/E ratio) for each company over a certain period (e.g., the last year or all available data).
`latest_company_financial_data.sql`: Create a view that retrieves the most recent financial data record for each company.
Execute these SQL view creation scripts against your MySQL database.

8.  Testing (Task 1.7):
Write Python scripts (e.g., in a `tests/` directory in the backend, or simple scripts run manually) to:
         Call the data ingestion functions for a test ticker symbol.
Verify that the data is successfully stored in the `companies` and `financial_data` tables by querying the database.
Query the `weekly_financial_data`, `monthly_financial_data`, `yearly_financial_data`, `avg_company_metrics`, and `latest_company_financial_data` views to ensure they return the expected aggregated and latest data. Check for data integrity and consistency.

Priority 2: LLM Integration and Analysis (Detailed)
Goal: Implement the integration with a chosen LLM API for generating basic analysis based on a simple prompt.

Detailed Implementation Steps:
1.  LLM API Setup (backend/services/llm_service.py - Task 2.1):
     Install the Python library for your chosen LLM provider (e.g., `openai` for OpenAI).
     In `backend/services/llm_service.py`, implement functions to:
Authenticate with the LLM API using your API key (retrieve it from environment variables).
Handle potential API connection errors.

2.  Prompt Sending and Response Receiving (backend/services/llm_service.py - Task 2.2):
Develop a function in `llm_service.py` that takes a prompt string as input and sends it to the LLM API.
Implement logic to receive and return the LLM's response.

3.  Basic Prompt Engineering and Management (backend/services/llm_service.py & backend/db/tables/prompts.sql - Tasks 2.3 & 2.5 & 2.6):
Task 2.5: Create the `backend/db/tables/prompts.sql` file with columns like `prompt_id`, `prompt_name`, `prompt_text`, `version`, and `operative`. Execute this script.
Task 2.3 (Initial): For initial testing, you can start with a simple, hardcoded prompt within your LLM service function (e.g., "Analyze the recent stock performance of [company_ticker]"). Later, you will integrate with the `prompts` table.
Task 2.6 (Basic): Implement basic functions in `llm_service.py` to:
Store a new prompt in the `prompts` table.
 Retrieve a prompt by `prompt_name` (for now, you can assume a single active version per name).

4.  LLM Response Parsing (backend/services/llm_service.py - Task 2.4):
Implement a function to parse the text response received from the LLM. Initially, you can focus on extracting the main analysis text. More sophisticated parsing can be added later.

5.  Testing LLM Prompt Response Quality (Task 2.7):
     Write a Python script to:
Retrieve a test prompt (either hardcoded or from the `prompts` table). 
Use the LLM service to send the prompt and get a response for a specific company (you'll need to fetch some basic company data or use a placeholder in the prompt).
Manually evaluate the quality and relevance of the LLM's response.

Priority 3: Report Generation and Feedback (Detailed)
Goal: Implement basic report generation combining database data and LLM analysis, along with a mechanism for user feedback.

Detailed Implementation Steps:
1.  Report and Feedback Table Creation (backend/db/tables/\.sql - Task 3.4):
Create the `backend/db/tables/reports.sql` file with columns like `report_id`, `company_id`, `user_id`, `report_content`, and `report_format`. Include foreign key constraints for `company_id` and `user_id`.
Create the `backend/db/tables/feedback.sql` file with columns like `feedback_id`, `report_id`, `user_id`, and `feedback_text`. Include foreign key constraints for `report_id` and `user_id`.
Execute these SQL scripts.

2.  Report and Feedback Data Model Implementation (backend/models/report_model.py):
Create `backend/models/report_model.py` and define Python classes (or ORM models) for `Report` and `Feedback` that map to the respective database tables.

3.  Report Service Implementation (backend/services/report_service.py - Tasks 3.1, 3.2, 3.3):
Task 3.1: Implement functions to retrieve company data and potentially aggregated financial data from the database (using `backend/database.py` and your data models).
Task 3.2: Create a function to orchestrate report generation:
Retrieve the relevant company data.
Retrieve a suitable prompt from the `prompts` table.
Use `llm_service.py` to get an analysis based on the data and the prompt.
Task 3.3: Format the retrieved data and the LLM response into a basic report content (e.g., a formatted string or a simple dictionary).

4.  Feedback Service Implementation (backend/services/feedback_service.py):
Implement functions to store user feedback in the `feedback` table using `backend/database.py` and the `Feedback` model.

5.  Report and Feedback Views (backend/db/views/\.sql - Task 3.5):
Create `backend/db/views/report_details.sql` to provide a view with detailed information about reports (including company name, user, creation date).
Create `backend/db/views/feedback_details.sql` to provide a view with details about feedback (including report details, user).
Execute these view creation scripts.

6.  API Endpoints (backend/routes/report_routes.py & feedback_routes.py - Task 3.6):
In `backend/routes/report_routes.py`, create a Flask route (e.g., `/reports/generate/<ticker_symbol>`) that:
Takes a company ticker symbol as input.
Calls the report generation function in `report_service.py`.
Returns the generated report (initially, as a JSON response).
In `backend/routes/feedback_routes.py`, create a Flask route (e.g., `/feedback/submit`) that:
Accepts feedback data (report ID, user ID, feedback text) via a POST request.
Calls the feedback storage function in `feedback_service.py`.
Returns a success or error response.

7.  Basic Staff Page for Review (frontend/templates/staff/report_review.html - Task 3.7):
Create a simple HTML page in `frontend/templates/staff/report_review.html`. For now, you can manually create a basic table to display a list of "dummy" reports with their associated prompts. You will integrate this with backend data retrieval later.

8.  Testing (Task 3.8):
Use a tool like `curl` or Postman to:
Call the report generation API endpoint with a valid ticker symbol and verify that you receive a report (check the format and content).
Send a POST request to the feedback submission endpoint with sample feedback data and verify that it is successfully stored in the `feedback` table.

By following these detailed steps for the first three priorities, you will establish the core data handling, LLM integration, and basic reporting functionalities of your Quant Analysis Platform. Remember to commit your code frequently to your GitHub repository as you progress through these steps.