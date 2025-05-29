Implementation Guide
Table of Contents
1. Prerequisites
     - Interpreters
     - Libraries to Install
          - Python Libraries (Backend)
          - Frontend Libraries (JavaScript/CSS Frameworks)
     - External API Keys
2. Repository Setup
3. Implementation Roadmap (Prioritized)
     - Priority 1: Data Acquisition and Storage (Completed)
     - Priority 2: News Sentiment Analysis Integration (Completed)
     - Priority 3: Graph and Basic Financial Trend Visualization (Completed)
     - Priority 4: User Authentication and Authorization
     - Priority 5: Automated Alerting System
     - Priority 6: Comprehensive Report Generation & Management
     - Priority 7: Prompt Management and Versioning
     - Priority 8: Feedback and Refinement Loop
     - Priority 9: Advanced Data Visualization and Customization
     - Priority 10: Backtesting and Strategy Simulation
4. Backend Setup
     - Environment Configuration
     - Database Setup
     - Installing Dependencies
     - Running the Backend
5. Frontend Setup
     - Setting up the Frontend Environment
     - Running the Frontend
6. External API Integration
     - Yahoo Finance API (via yfinance library)
     - The Guardian API
     - Google Generative AI (Gemini API)
     - Perplexity AI API
7. Database Schema
8. Running Tests
     - Backend Tests
     - Frontend Tests (if applicable)
9. Deployment (Optional)
10. Contributing
11. License

1. Prerequisites
Before you begin, ensure you have the following software installed on your system:

I. Interpreters
The core languages and their interpreters used in this project are:

Python: The backend is primarily built with Python.
Recommended Version: Python 3.11.3
JavaScript: Used for dynamic content and interactivity on the frontend.
HTML/CSS: For structuring and styling the web pages.

II. Libraries to Install
This section lists the necessary libraries for both the backend (Python) and frontend (JavaScript/CSS), along with instructions for installing them.

A. Python Libraries (Backend)
These libraries are crucial for the backend functionality, including data retrieval, database interactions, LLM integrations, and task scheduling.

For VSCode Terminal / pip install:
You can install all required Python libraries by navigating to your backend directory (where requirements.txt is located, if applicable) in the VSCode integrated terminal and running:

pip install -r requirements.txt

Alternatively, you can install them individually using pip:

annotated-types (Version: 0.7.0)
APScheduler (Version: 3.11.0)
beautifulsoup4 (Version: 4.13.3)
blinker (Version: 1.6.2)
cachetools (Version: 5.5.2)
certifi (Version: 2025.1.31)
cffi (Version: 1.17.1)
charset-normalizer (Version: 3.4.1)
click (Version: 8.1.7)
colorama (Version: 0.4.6)
cryptography (Version: 44.0.2)
curl_cffi (Version: 0.10.0)
Flask (Version: 2.3.3)
flask-cors (Version: 5.0.1)
Flask-Login (Version: 0.6.2)
Flask-SQLAlchemy (Version: 3.0.5)
frozendict (Version: 2.4.6)
google-ai-generativelanguage (Version: 0.6.15)
google-api-core (Version: 2.24.2)
google-api-python-client (Version: 2.164.0)
google-auth (Version: 2.38.0)
google-auth-httplib2 (Version: 0.2.0)
google-generativeai (Version: 0.8.4)
googleapis-common-protos (Version: 1.69.1)
greenlet (Version: 2.0.2)
grpcio (Version: 1.71.0)
grpcio-status (Version: 1.71.0)
httplib2 (Version: 0.22.0)
idna (Version: 3.10)
itsdangerous (Version: 2.1.2)
Jinja2 (Version: 3.1.2)
MarkupSafe (Version: 2.1.3)
multitasking (Version: 0.0.11)
mysql-connector (Version: 2.2.9)
numpy (Version: 2.2.4)
pandas (Version: 2.2.3)
peewee (Version: 3.17.9)
platformdirs (Version: 4.3.7)
proto-plus (Version: 1.26.1)
protobuf (Version: 5.29.3)
pyasn1 (Version: 0.6.1)
pyasn1_modules (Version: 0.4.1)
pycparser (Version: 2.22)
pydantic (Version: 2.10.6)
pydantic_core (Version: 2.27.2)
PyMySQL (Version: 1.1.1)
pyparsing (Version: 3.2.1)
python-dateutil (Version: 2.9.0.post0)
python-dotenv (Version: 1.1.0)
pytz (Version: 2025.2)
requests (Version: 2.32.3)
rsa (Version: 4.9)
setuptools (Version: 65.5.0)
six (Version: 1.17.0)
soupsieve (Version: 2.6)
SQLAlchemy (Version: 2.0.20)
tqdm (Version: 4.67.1)
typing_extensions (Version: 4.12.2)
tzdata (Version: 2025.2)
tzlocal (Version: 5.3.1)
uritemplate (Version: 4.1.1)
urllib3 (Version: 2.3.0)
websockets (Version: 15.0.1)
Werkzeug (Version: 2.3.7)
yfinance (Version: 0.2.61)

B. Frontend Libraries (JavaScript/CSS Frameworks)
These are typically included via CDN links in your HTML files, so no explicit npm install or similar commands are needed unless you decide to manage them locally.

Bootstrap (CSS Framework):
Used for responsive design and UI components.
Location: Integrated via CDN in frontend/templates/user/company_details.html and frontend/templates/dashboard.html.

jQuery (JavaScript Library):
Used for DOM manipulation and AJAX calls.
Location: Integrated via CDN in frontend/templates/user/company_details.html and frontend/templates/dashboard.html.

Chart.js (JavaScript Charting Library):
Used for rendering interactive financial data graphs.
Location: Integrated via CDN in frontend/templates/user/company_details.html.

Flatpickr (JavaScript Date Picker):
For user-friendly date selections.
Location: Integrated via CDN in frontend/templates/dashboard.html.

Select2 (jQuery Plugin):
Enhances select boxes for better user experience.
Location: Integrated via CDN in frontend/templates/dashboard.html.

Popper.js (JavaScript Positioning Engine):
A dependency for Bootstrap's interactive components.
Location: Integrated via CDN in frontend/templates/user/company_details.html and frontend/templates/dashboard.html.

External API Keys
You will need to obtain API keys for the following external services:

Yahoo Finance API (via yfinance library):
Purpose: Retrieval of news, historical financial data (OHLCV), market capitalization, dividends, and other company-specific financial metrics.
Location: Integrated into backend/services/data_service.py and backend/api.py using the yfinance Python library. This is an unofficial wrapper for Yahoo Finance, so it doesn't require a direct API key for Yahoo Finance itself.

The Guardian API:
Purpose: Retrieval of industry-specific news articles.
Endpoint: https://content.guardianapis.com/search
API Key Location: The guardian_api_key is hardcoded as "ce66226f-693d-42a5-9023-3b003666df2a" in the code. It is highly recommended to move this API key to an environment variable (e.g., in backend/.env) for security and best practices, similar to how other API keys are handled.

Google Generative AI (Gemini API):
Purpose: Performing news summary and sentiment analysis reports.
Model Used: gemini-2.0-flash-lite.
API Key Location: The GOOGLE_API_KEY is retrieved from environment variables using os.getenv("GOOGLE_API_KEY"). A hardcoded example present for demonstration purposes; this should be replaced with a secure key in your .env file.

Perplexity AI API:
Purpose: Although mentioned in llm_service.py as a potential LLM provider, it is explicitly noted as "not updated yet & not in use".
API Key Location: Expected to be retrieved from an environment variable PERPLEXITY_API_KEY.

2. Repository Setup
This section outlines how to set up your project with a Git repository, specifically using GitHub.

Cloning the Repository (Recommended)
If you are starting with an existing GitHub repository for this project, follow these steps:

Install Git: Ensure Git is installed on your system. You can download it from git-scm.com.

Open Terminal/Command Prompt: Navigate to the directory where you want to clone the project.

Clone the Repository: Use the git clone command followed by the repository's URL.

     git clone https://github.com/your-username/QuantAnalysisPlatform.git

Replace your-username/QuantAnalysisPlatform.git with the actual URL of your GitHub repository.

Navigate into the Project Directory:

     cd QuantAnalysisPlatform

Connecting Existing Local Files to GitHub
If you have the project files locally and want to push them to a new GitHub repository:

Create a New GitHub Repository:

Go to GitHub and log in.

Click the "+" sign in the top right corner and select "New repository".

Give your repository a name (e.g., QuantAnalysisPlatform), an optional description, and choose whether it's public or private. Do NOT initialize the repository with a README, .gitignore, or license if you already have these files locally, as this can cause conflicts.

Click "Create repository".

Initialize Local Git Repository:

Open your terminal or command prompt.

Navigate to the root directory of your local project (QuantAnalysisPlatform/).

Initialize a new Git repository:

     git init

Add Files to Staging:

     Add all your project files to the staging area. It's recommended to add all files at once, then use .gitignore to exclude unnecessary files (like .env, __pycache__, etc.).

     git add .

Commit the Files:

     Commit the staged files with a descriptive message:

     git commit -m "Initial commit of Quant Analysis Platform"

Connect to GitHub Repository:

Add the remote origin to your local repository. Replace your-username and QuantAnalysisPlatform with your actual GitHub username and repository name.

git remote add origin https://github.com/your-username/QuantAnalysisPlatform.git

Push to GitHub:

Push your local commits to the GitHub repository. The -u flag sets the upstream branch, so future git push commands will be simpler.

git push -u origin main

If your default branch name is master instead of main, use git push -u origin master.

3. Implementation Roadmap (Prioritized)
Priority 1: Data Acquisition and Storage (Completed)
Description: This foundational priority establishes the essential data storage for the platform, encompassing the core tables (companies, financial_data, news, reports, alerts, prompt_versions, feedback). It also focuses on the initial data acquisition mechanism for financial and historical data specifically from yfinance. A basic UI on the investor dashboard will be developed to verify the retrieval and display of this financial data.

Tasks:
     1.1 Detailed Definition of Core Data Models:
     Goal: Precisely define the SQLAlchemy models for the core data tables.

     Actual Codes/Functions/Files:
          backend/models/user_model.py: Defines the User table for user authentication, roles, and timestamps.

          backend/models/data_model.py: Defines Company, FinancialData, and News tables, including relationships and financial metrics like open, high, low, close, volume, roi, eps, pe_ratio, revenue, debt_to_equity, cash_flow.

          backend/models/alert_model.py: Defines the Alert table to store triggered alerts related to companies.

          backend/models/report_model.py: Defines the Report table to store generated analysis reports, linked to companies and users.

          backend/models/prompt_model.py: Defines PromptVersion for managing and versioning LLM prompts, linked to users.

          backend/models/feedback_model.py: Defines the Feedback table for user feedback on reports, linked to reports and users.

          Database Schema (from datatables.md): Confirms the exact SQL schema for users, companies, financial_data, news, reports, alerts, prompt_versions, feedback tables and their respective columns and relationships, including views like latest_financial_data, report_details, and feedback_details.

     1.2 Database Initialization and Management:
     Goal: Set up database connection and session management.

     Actual Codes/Functions/Files:
          backend/config.py: Defines DATABASE_URL for MySQL connection (mysql+mysqlconnector://root:mySQL2025!@localhost/fypquantanalysisplatform).

          backend/database.py: Contains get_engine, get_session_local, init_db, get_db, get_all_companies, get_company_by_ticker functions for database setup, session handling, and basic company retrieval. Uses SQLAlchemy for ORM.

          backend/app.py: create_app function initializes the database using init_db and registers blueprints.

     1.3 Financial Data Ingestion from External APIs:
     Goal: Implement robust data fetching from yfinance and storage into the database.

     Actual Codes/Functions/Files:
          backend/services/data_service.py:
               fetch_financial_data(ticker: str, period: str, start: Optional[date], end: Optional[date], retries: int, delay: float, db: Session, company_id: int): Fetches historical OHLCV data from yfinance with retry logic. It handles different periods (daily, weekly, monthly, yearly, max).

               store_financial_data(db: Session, ticker: str, company_id: int, period: str): Stores fetched financial data into the financial_data table, ensuring data freshness using needs_update logic.

               get_monthly_financial_data(db: Session, company_id: int): Aggregates financial data monthly.

               get_yearly_financial_data(db: Session, company_id: int): Aggregates financial data yearly.

          backend/api.py:
               /api/company/<int:company_id>/financial_data (GET): Retrieves financial data from the database. It also integrates with yfinance to fetch real-time data like average_volume, market_cap, beta, earnings_date, forward_dividend, dividend_yield, ex_dividend_date, target_mean_price for the given company ticker if not found in DB.

               /api/ingest-financial-data (POST): Endpoint to trigger financial data ingestion for a given ticker, calling store_financial_data.

          backend/routes/data_routes.py:
               needs_update(db: Session, company_id: int, threshold_hours: int = 24): Checks if financial data needs updating based on the most recent entry.

               /api/data/financial_data/<period> (GET): Retrieves financial data (daily, weekly, monthly, yearly) from the database.

          backend/tasks.py:
               daily_financial_data_update(app: Flask): A scheduled task to update financial data for all companies daily. It uses update_financial_data_for_company.

               update_financial_data_for_company(db: Session, company): Fetches and stores the latest financial data for a specific company.

          Software/APIs: yfinance Python library for fetching financial data.

     1.4 Basic UI for Data Verification:
     Goal: Display fetched financial data on the dashboard and company details page.

     Actual Codes/Functions/Files:
          frontend/templates/user/dashboard.html: Contains tables (financialDataTableBody) and pagination controls to display company financial data.

          frontend/static/js/dashboard.js:
               fetchFinancialData(): Fetches all financial data for display on the dashboard.

               displayData(filteredData, page): Renders financial data in the table with pagination and filtering.

               companySearchInput, industryFilterDropdown, dateFromInput, dateToInput, applyFiltersButton: Implement search and filtering functionalities.

          frontend/templates/user/company_details.html: Displays company-specific financial data.

          frontend/static/js/company_details.js:
               fetchCompanyDetails(ticker): Fetches general company details and triggers financial data loading.

               fetchLatestFinancialData(companyId): Fetches the latest financial data for the current company.

Priority 2: News Sentiment Analysis Integration (Completed)
Description: Integrate news fetching capabilities and leverage an LLM (Gemini) for sentiment analysis of financial news. This will provide actionable insights for investment analysis reports.

Tasks:

     2.1 News Data Acquisition and Storage:
     Goal: Fetch relevant news articles and store them in the database.

     Actual Codes/Functions/Files:
          backend/services/data_service.py:
               fetch_latest_news(query: str, industry: Optional[str], exchange: Optional[str], company_name: Optional[str]): Fetches news from external sources (implied by requests import) for a given query, industry, and exchange.

               store_news_articles(db: Session, news_data: List[Dict], company_id: int): Stores news articles into the news table.

          backend/models/data_model.py: Defines the News table with news_id, company_id, title, summary, url, published_date, source.

          backend/app.py:
          /api/company/<ticker>/news (GET): Route to fetch company-specific and industry news.

          backend/routes/data_routes.py:
          /api/data/news (GET): Route to get company news from the database.

          backend/tasks.py:
          daily_news_update(app: Flask): A scheduled task to update news for all companies daily.

     2.2 LLM Integration for Sentiment Analysis:
     Goal: Use Gemini LLM to analyze the sentiment of news articles.

     Actual Codes/Functions/Files:
          backend/services/llm_service.py:
               analyze_news_sentiment_gemini(news_articles: List[Dict[str, Any]], prompt: Optional[str], llm_model: str = 'gemini-2.0-flash-lite'): Function to send news articles to the Gemini API for sentiment analysis and report generation. It uses the google.generativeai library.

               analyze_news_sentiment(news_articles: List[Dict[str, Any]], llm_provider: str, prompt: Optional[str], llm_model: str): A wrapper function to select the LLM provider (currently supports Gemini).

          backend/routes/llm_routes.py:
               /api/llm/sentiment/<int:company_id> (GET): Endpoint to trigger news sentiment analysis for a specific company using Gemini. It retrieves news articles and calls analyze_news_sentiment_gemini.

          Software/APIs: Google Generative AI API (specifically gemini-2.0-flash-lite model). Environment variable GOOGLE_API_KEY is used.

     2.3 Integration with Report Generation:
     Goal: Incorporate sentiment analysis results into investment analysis reports.

     Actual Codes/Functions/Files:
          backend/routes/llm_routes.py: The get_company_news_sentiment function constructs a report_data dictionary including overall_news_summary, sentiment_analysis, paragraph_section, company_name, and ticker_symbol. This report data is then returned and presumably used by the frontend or another service for display/storage in the reports table.

          backend/models/report_model.py: The Report model has a content field for storing the report details.

     2.4 Basic UI for News and Sentiment Display:
     Goal: Display news articles and their sentiment analysis results on the company details page.

     Actual Codes/Functions/Files:
          frontend/templates/user/company_details.html: Includes a "News & Sentiment Analysis" tab (newsSentimentTabContent) to display news and the LLM-generated report.

          frontend/static/js/company_details.js:
               displayTopNews(companyNews, industryNews): Renders company and industry news articles.

               updateLLMReport(companyId): Calls the /api/llm/sentiment/<companyId> endpoint and displays the generated LLM report.

     Priority 3: Graph and Basic Financial Trend Visualization (Completed)
     Description: Enable visualization of historical financial data (OHLCV) through interactive graphs, allowing users to select different timeframes.

     Tasks:

     3.1 Historical Data Retrieval for Graphing:
     Goal: Efficiently retrieve historical OHLCV data from the database for charting.

     Actual Codes/Functions/Files:
          backend/routes/graph_routes.py:
               fetch_graph_data(db: Session, company_id: int, timeframe: str): Queries the financial_data table to retrieve date, close, and volume based on the specified timeframe (weekly, monthly, yearly, max).

               /api/graph/company/<int:company_id>/<string:timeframe> (GET): Exposes an API endpoint to fetch graph data for a given company and timeframe.

          backend/models/data_model.py: The FinancialData model stores date, open, high, low, close, volume.

     3.2 Graphing Library Integration:
     Goal: Utilize a frontend charting library to render interactive financial graphs.

     Actual Codes/Functions/Files:
          frontend/templates/user/company_details.html: Imports Chart.js (https://cdn.jsdelivr.net/npm/chart.js). Contains canvas elements for charts (e.g., weeklyChart, monthlyChart).

          frontend/static/js/company_details.js:
          createOrUpdateChart(chartId, data, labels, chartType): Function to dynamically create or update Chart.js instances with fetched data, handling line and bar charts.

     3.3 Basic UI for Graph Display:
     Goal: Provide a user interface on the company details page to view graphs for different timeframes.

     Actual Codes/Functions/Files:
          frontend/templates/user/company_details.html: Includes tab buttons (tab-button) to switch between weekly, monthly, yearly, and max timeframes. Each timeframe has a corresponding chart-container.

          frontend/static/js/company_details.js:
          fetchGraphData(companyId, timeframe): Fetches data for the selected timeframe and then calls createOrUpdateChart.

          Event listeners for tab buttons trigger fetchGraphData for the selected timeframe.

Priority 4: User Authentication and Authorization
Description: Implement a secure user authentication system (registration, login, logout) and role-based authorization (User, Analyst, Admin).

Planned Functions/Files/APIs/Software:

Backend:
backend/models/user_model.py: Already defines User model with username, email, password_hash, and role.

backend/routes/user_routes.py (New/Update):
     @user_routes_bp.route('/register', methods=['POST']):
          Explanation: Handles new user registration. It will receive username, email, and password from the frontend. It will hash the password using werkzeug.security.generate_password_hash before storing it in the database.

          Test Cases (backend/tests/test_user_routes.py - New):
               Test successful registration with valid data.
               Test registration with an existing username or email (should fail with appropriate error).
               Test registration with invalid input (e.g., missing fields).

     @user_routes_bp.route('/login', methods=['POST']):
          Explanation: Handles user login. It will receive username (or email) and password. It will verify the password against the stored hash using werkzeug.security.check_password_hash and, if successful, establish a user session (e.g., using Flask's session object or generating a JWT token) and return user details, including role.

          Test Cases (backend/tests/test_user_routes.py - New):

               Test successful login with correct credentials.
               Test login with incorrect password.
               Test login with non-existent username/email.
               Test session creation and verification.

     @user_routes_bp.route('/logout', methods=['POST']):
          Explanation: Handles user logout. It will clear the user's session data, effectively logging them out.

          Test Cases (backend/tests/test_user_routes.py - New):
               Test successful logout and session termination.

     @user_routes_bp.route('/dashboard'):
          Explanation: This route will typically redirect to the user's main dashboard page after successful login. It will likely require authentication to access.

          Test Cases (backend/tests/test_user_routes.py - New):
               Test authenticated access to dashboard.
               Test unauthenticated access to dashboard (should redirect to login).

     @user_routes_bp.route('/profile', methods=['GET', 'PUT']):
          Explanation: GET will retrieve the authenticated user's profile information. PUT will allow the user to update their profile (e.g., email, password). Password updates will involve re-hashing.

          Test Cases (backend/tests/test_user_routes.py - New):
               Test retrieving profile of authenticated user.
               Test updating email/username for authenticated user.
               Test updating password for authenticated user.
               Test unauthorized access to profile (should fail).

backend/services/user_service.py (New):
     Explanation: This module will encapsulate the business logic for user management, interacting directly with the database models.

     create_user(db: Session, username: str, email: str, password: str, role: str = 'user') -> User: Hashes password and adds new user to DB.

     verify_password(plain_password: str, hashed_password: str) -> bool: Verifies a plain password against a hashed password.

     get_user_by_email(db: Session, email: str) -> User: Retrieves a user by their email address.

     get_user_by_username(db: Session, username: str) -> User: Retrieves a user by their username.

     update_user_profile(db: Session, user_id: int, new_data: Dict) -> User: Updates user details.

     Test Cases (backend/tests/test_user_service.py - New):
          Test create_user functionality (correct hashing, DB insertion).
          Test verify_password with correct and incorrect passwords.
          Test retrieval functions (get_user_by_email, get_user_by_username).
          Test update_user_profile for various fields.

backend/auth.py (New):
     Explanation: This module will provide utility functions for authentication and authorization. It will likely include:

     generate_password_hash and check_password_hash (from werkzeug.security).

     Functions for session management (e.g., login_user, logout_user, current_user decorators/functions if using Flask-Login, or custom JWT handling).

     role_required decorator/function for authorization checks (@role_required('analyst')).

     Test Cases (backend/tests/test_auth.py - New):
          Test password hashing and verification.
          Test role_required decorator functionality (e.g., ensuring access is granted only to authorized roles).
          Test session management logic (e.g., setting/clearing user ID in session).

Frontend:
     frontend/templates/auth/register.html (New):
          Explanation: A standard HTML form for user registration, including fields for username, email, and password.

     frontend/templates/auth/login.html (New):
          Explanation: A standard HTML form for user login, with fields for username/email and password.

     frontend/static/js/auth.js (New):
          Explanation: JavaScript functions to handle the submission of login and registration forms, make AJAX calls to the backend API endpoints (/api/auth/register, /api/auth/login), process responses, and manage client-side session (e.g., storing user data in localStorage or sessionStorage if using tokens, or redirecting upon successful login/logout).

     frontend/templates/base.html (Update):
          Explanation: Update the base template to conditionally display "Login" and "Register" links when the user is not authenticated, and "Logout" and "Profile" links when authenticated. This will involve checking for user session/token presence in the frontend.

Software/APIs: Flask-Login (or similar for session management), werkzeug.security for password hashing.

Priority 5: Automated Alerting System
Description: Develop a system to set up and trigger alerts based on predefined financial conditions (e.g., stock price reaching a threshold, significant volume changes).

Planned Functions/Files/APIs/Software:

Backend:
backend/models/alert_model.py: Already defines Alert table with company_id, alert_type, message, triggered_at, created_at, updated_at.
     Explanation: This model needs to be extended to include user_id (who set the alert), condition_type (e.g., 'price_above', 'volume_change'), condition_value (e.g., 150.00, 20%), is_active (boolean to enable/disable alerts), and last_checked_at.

backend/routes/alert_routes.py (New/Update):
     @alert_routes_bp.route('/alerts', methods=['POST']):
          Explanation: Allows an authenticated user to create a new alert rule. It will receive company_id, alert_type, condition_type, condition_value. The backend will validate the input and store the alert rule in the database.

          Test Cases (backend/tests/test_alert_routes.py - New):
               Test creating a new alert rule successfully.
               Test creating an alert rule with invalid company_id or condition_value.
               Test creating an alert rule as an unauthenticated user (should fail).

     @alert_routes_bp.route('/alerts', methods=['GET']):
          Explanation: Retrieves active and/or triggered alerts for the authenticated user or for a specific company if provided.

          Test Cases (backend/tests/test_alert_routes.py - New):
          Test retrieving all active alerts for the logged-in user.
          Test retrieving triggered alerts for a specific company.
          Test retrieving alerts as an unauthenticated user (should fail).

     @alert_routes_bp.route('/alerts/<int:alert_id>', methods=['DELETE']):
          Explanation: Allows an authenticated user to delete one of their alert rules.

          Test Cases (backend/tests/test_alert_routes.py - New):
               Test deleting an existing alert successfully.
               Test deleting an alert that doesn't belong to the user.
               Test deleting a non-existent alert.
               Test deleting an alert as an unauthenticated user (should fail).

backend/services/alerting_service.py (New):
     Explanation: This module will contain the core logic for managing and checking alerts.

     create_alert_rule(db: Session, user_id: int, company_id: int, alert_type: str, condition_type: str, condition_value: float) -> Alert: Saves a new alert rule to the database.

     check_and_trigger_alerts(app: Flask):
          Explanation: This function will be scheduled to run periodically. It will fetch all active alert rules, retrieve the latest financial data for the associated companies, evaluate if any conditions are met, and if so, update the alert status (e.g., set triggered_at and is_active = False or send a notification).

          Test Cases (backend/tests/test_alerting_service.py - New):
               Test create_alert_rule with various valid inputs.
               Test check_and_trigger_alerts with mock financial data to simulate triggering (e.g., price crossing a threshold).
               Test that alerts are correctly marked as triggered and not re-triggered within a certain period.
               Test handling of edge cases (e.g., no financial data for a company).

backend/tasks.py (Update):
     hourly_alert_check(app: Flask): A new scheduled task that calls alerting_service.check_and_trigger_alerts(app).
          Explanation: This function will be added to the BackgroundScheduler in backend/app.py to run at a defined interval (e.g., every hour).

Frontend:
     frontend/templates/user/alerts.html (New):
          Explanation: A user interface page for managing and viewing their alerts. This page will likely include:
          - A form to create new alert rules (company, alert type, condition, value).
          - A table displaying active alerts, with options to view details or delete.
          - A section to view triggered alerts.

     frontend/static/js/user/alerts.js (New):
          Explanation: JavaScript to interact with the alert API endpoints. It will handle form submissions for creating alerts, making AJAX calls to fetch and display alerts, and handling delete actions.

     frontend/templates/base.html (Update):
          Explanation: Add a link to the "Alerts" page in the navigation bar. Potentially display a small notification badge if there are new triggered alerts.

Priority 6: Comprehensive Report Generation & Management
Description: Enhance report generation to include more diverse financial data, historical analysis, and allow users to manage (view, save, delete) generated reports. Integrate prompt versioning.

Planned Functions/Files/APIs/Software:

Backend:
backend/models/report_model.py: Already defines Report model with company_id, user_id, report_date, content.
     Explanation: This model should be extended to include prompt_version_id (ForeignKey to PromptVersion.prompt_version_id) to explicitly link which prompt version was used for report generation.

backend/routes/report_routes.py (New/Update):
     @report_routes_bp.route('/reports', methods=['POST']):
          Explanation: Endpoint to trigger the generation and saving of a new report. It will receive company_id and potentially prompt_version_id (or infer the operative one). This will orchestrate calls to data_service for financial/news data and llm_service for analysis.

          Test Cases (backend/tests/test_report_routes.py - New):
               Test successful report generation and saving.
               Test generating a report for a non-existent company.
               Test generating a report as an unauthenticated user (should fail).
               Test generating a report using a specific prompt_version_id.

     @report_routes_bp.route('/reports/<int:report_id>', methods=['GET']):
          Explanation: Retrieves a specific report by its report_id.

          Test Cases (backend/tests/test_report_routes.py - New):
               Test retrieving an existing report.
               Test retrieving a report that doesn't belong to the user (if authorization is implemented).
               Test retrieving a non-existent report (should return 404).

     @report_routes_bp.route('/reports', methods=['GET']):
          Explanation: Retrieves a list of all reports generated by the authenticated user.

          Test Cases (backend/tests/test_report_routes.py - New):
               Test retrieving all reports for an authenticated user.
               Test retrieving reports as an unauthenticated user (should fail).

     @report_routes_bp.route('/reports/<int:report_id>', methods=['DELETE']):
          Explanation: Deletes a specific report by its report_id.

          Test Cases (backend/tests/test_report_routes.py - New):
               Test deleting an existing report successfully.
               Test deleting a report that doesn't belong to the user.
               Test deleting a non-existent report.

backend/services/reporting_service.py (New):
     Explanation: This module will contain the complex logic for generating reports.

     generate_detailed_report(db: Session, company_id: int, user_id: int, prompt_version_id: Optional[int] = None) -> Report:
          Explanation: This is the core function. It will:
          - Fetch company data (from Company table).
          - Fetch recent financial data (from FinancialData table).
          - Fetch relevant news articles (using data_service.fetch_latest_news).
          - Retrieve the appropriate LLM prompt: if prompt_version_id is provided, fetch that specific version; otherwise, fetch the latest operative prompt from the PromptVersion table for report generation.
          - Call llm_service.analyze_news_sentiment_gemini (or a more general LLM analysis function) with the fetched news articles and the selected prompt.
          - Format the LLM's response and other data into a comprehensive report content.
          - Call save_report to persist the report.

          Test Cases (backend/tests/test_reporting_service.py - New):
               Test generate_detailed_report with mock data for company, financial data, and news.
               Test that the correct operative prompt is used when prompt_version_id is not specified.
               Test that a specific prompt_version_id is used when provided.
          - Verify the structure and content of the generated report.

     save_report(db: Session, report_data: Dict) -> Report: Persists the generated report data to the reports table.
     Test Cases (backend/tests/test_reporting_service.py - New):
          Test successful saving of a report to the database.

backend/services/llm_service.py (Update):
     Explanation: Modify analyze_news_sentiment_gemini or introduce a new function (e.g., generate_analysis_from_prompt) that takes the prompt_text directly (fetched from the PromptVersion table by reporting_service) rather than using an hardcoded or default prompt. This ensures prompt versioning is fully integrated.

     get_prompt_text(db: Session, prompt_version_id: int) -> str: A helper function (can be in llm_service or prompt_service) to retrieve the prompt text from the PromptVersion table.

Frontend:
     frontend/templates/user/reports.html (New):
          Explanation: A page to display a list of all reports generated by the user. Each report entry should have a link to view the detailed report and an option to delete it.

     frontend/static/js/user/reports.js (New):
          Explanation: JavaScript to fetch the list of reports, render them, handle clicks to view detailed reports, and manage deletion. It will also contain the logic for triggering new report generation via API call.

     frontend/templates/user/company_details.html (Update):
          Explanation: Add a "Generate Report" button (or similar) that, when clicked, triggers the /api/reports POST endpoint to generate a new report for the currently viewed company. This button might also have an option to select a specific prompt version if the user has that privilege.

Priority 7: Prompt Management and Versioning
Description: Enable financial analysts to manage and refine LLM prompts, including creating new versions, setting operative versions, and tracking changes to ensure reproducibility and performance optimization.

Planned Functions/Files/APIs/Software:

Backend:

backend/models/prompt_model.py: Already defines PromptVersion with prompt_version_id, prompt_id, user_id, version, operative, original_prompt, prompt_text.
     Explanation: The prompt_id should be a unique identifier for a conceptual prompt (e.g., "News Sentiment Analysis Prompt"), and version tracks iterations for that conceptual prompt. operative indicates the currently active version.

backend/routes/prompt_routes.py (New):
     @prompt_routes_bp.route('/prompts', methods=['POST']):
          Explanation: Allows an analyst to create a new conceptual prompt (which will also create its first version). Receives original_prompt (a name/identifier for the prompt) and prompt_text.

          Test Cases (backend/tests/test_prompt_routes.py - New):
               Test creating a new prompt successfully (as an analyst).
               Test creating a prompt as a non-analyst (should fail with authorization error).
               Test creating a prompt with missing data.

     @prompt_routes_bp.route('/prompts', methods=['GET']):
          Explanation: Retrieves a list of all conceptual prompts (e.g., distinct prompt_ids) and their latest operative version. This is useful for users to pick a prompt to use for analysis.

          Test Cases (backend/tests/test_prompt_routes.py - New):
               Test retrieving operative prompts (accessible to all authenticated users).
               Test that only operative versions are returned by default.

     @prompt_routes_bp.route('/prompts/<int:prompt_id>/versions', methods=['POST']):
          Explanation: Allows an analyst to create a new version for an existing conceptual prompt. It will take the prompt_id and the new prompt_text. It will automatically increment the version number based on the latest existing version for that prompt_id. It can also set this new version as operative if specified.

          Test Cases (backend/tests/test_prompt_routes.py - New):
               Test creating a new version for an existing prompt (as an analyst).
               Test that the version number increments correctly.
               Test setting the new version as operative.

     @prompt_routes_bp.route('/prompts/<int:prompt_id>/versions', methods=['GET']):
          Explanation: Retrieves all historical versions for a specific prompt_id.

          Test Cases (backend/tests/test_prompt_routes.py - New):
               Test retrieving all versions of a specific prompt (as an analyst).
               Test that only analysts can access all versions.

     @prompt_routes_bp.route('/prompts/versions/<int:prompt_version_id>/activate', methods=['PATCH']):
          Explanation: Allows an analyst to set a specific prompt_version_id as the operative one for its prompt_id. This will set operative = True for the selected version and operative = False for all other versions associated with the same prompt_id.

          Test Cases (backend/tests/test_prompt_routes.py - New):
               Test successfully activating a prompt version (as an analyst).
               Test that only one version is operative for a given prompt_id after activation.
               Test attempting to activate a non-existent version.
               Test activating a prompt as a non-analyst (should fail).

backend/database.py (Update):
     Explanation: Add wrapper functions for CRUD operations on PromptVersion objects.

     create_prompt_version(db: Session, user_id: int, original_prompt: str, prompt_text: str, prompt_id: Optional[int] = None, set_operative: bool = True) -> PromptVersion: Creates a new prompt entry or a new version for an existing prompt.

     get_prompt_version(db: Session, prompt_version_id: int) -> PromptVersion: Retrieves a specific prompt version by ID.

     get_prompt_versions_by_prompt_id(db: Session, prompt_id: int, skip: int = 0, limit: int = 100) -> List[PromptVersion]: Retrieves all versions for a given conceptual prompt.

     get_operative_prompts(db: Session) -> List[PromptVersion]: Retrieves all currently operative prompt versions.

     set_operative_prompt_version(db: Session, prompt_version_id: int) -> PromptVersion: Sets a specific version as operative and deactivates others.

     delete_prompt_version(db: Session, prompt_version_id: int): Deletes a specific prompt version.

backend/services/prompt_service.py (New):
     Explanation: This module will contain the business logic for prompt management, interacting with database.py functions. It will handle the incrementing of versions, ensuring uniqueness, and managing the operative flag logic.

     create_new_prompt(db, user_id, original_prompt, prompt_text) -> PromptVersion: Creates initial prompt.

     add_new_prompt_version(db, prompt_id, user_id, prompt_text, set_as_operative=False) -> PromptVersion: Creates a new version for an existing prompt.

     activate_prompt_version(db, prompt_version_id) -> PromptVersion: Sets a specific version as operative.

     get_all_operative_prompts(db) -> List[PromptVersion]: Retrieves currently active prompts.

     get_all_versions_of_prompt(db, prompt_id) -> List[PromptVersion]: Retrieves all versions.

     delete_prompt(db, prompt_version_id): Deletes a prompt version.

     Test Cases (backend/tests/test_prompt_service.py - New):
          Test CRUD operations on prompts and prompt versions (create, retrieve, update, delete).
          Test the logic for incrementing version numbers correctly.
          Test the activate_prompt_version function to ensure that only one version for a given prompt_id is operative at any time.

backend/services/llm_service.py (Update):
     Explanation: Modify analyze_news_sentiment_gemini or other LLM interaction functions to accept prompt_text directly as a parameter. The reporting_service (P6) or prompt_routes (P7) will be responsible for fetching the correct prompt_text from the PromptVersion table based on the desired prompt_version_id or the currently operative version.

Frontend:
     frontend/templates/staff/prompt_management.html (New):
          Explanation: A UI page dedicated to analysts for managing prompts. It will likely include:
          - A list of existing conceptual prompts.
          - For each prompt, the ability to view all its versions.
          - A form to create a new prompt version.
          - Buttons/toggles to set a specific version as operative.
          This UI will be restricted to users with the 'analyst' role using frontend and backend authorization.

     frontend/static/js/staff/prompt_management.js (New):
          Explanation: JavaScript to interact with backend/routes/prompt_routes.py API endpoints. It will handle:
          - Fetching and displaying lists of prompts and their versions.
          - Form submissions for creating new prompts/versions.
          - Click handlers for activating prompt versions.
          - Error handling and feedback for API calls.

Priority 8: Feedback and Refinement Loop
Description: Implement a mechanism for users to provide feedback on LLM-generated reports, allowing analysts to review and use this feedback to refine prompts and improve LLM performance.

Planned Functions/Files/APIs/Software:

Backend:

backend/models/feedback_model.py: Already defines Feedback model with report_id, user_id, feedback_text, created_at, updated_at.
     Explanation: Consider adding fields like rating (e.g., 1-5 stars) and category (e.g., 'Accuracy', 'Clarity', 'Relevance') to provide more structured feedback.

backend/routes/feedback_routes.py (New):
     @feedback_routes_bp.route('/feedback', methods=['POST']):
          Explanation: Endpoint for users to submit feedback for a specific report. It will receive report_id, feedback_text, and possibly rating or category.

          Test Cases (backend/tests/test_feedback_routes.py - New):
               Test successful submission of feedback (as authenticated user).
               Test submitting feedback for a non-existent report.
               Test submitting feedback as an unauthenticated user (should fail).
               Test submitting feedback with invalid data.

     @feedback_routes_bp.route('/feedback', methods=['GET']):
          Explanation: Retrieves all feedback entries. This endpoint should be protected and only accessible by 'analyst' or 'admin' roles. It might allow filtering by report_id or user_id.

          Test Cases (backend/tests/test_feedback_routes.py - New):
               Test retrieving all feedback as an analyst.
               Test retrieving feedback for a specific report.
               Test retrieving feedback as a non-analyst (should fail with authorization error).

backend/services/feedback_service.py (New):
     Explanation: Contains the business logic for handling feedback.

     submit_feedback(db: Session, report_id: int, user_id: int, feedback_text: str, rating: Optional[int] = None, category: Optional[str] = None) -> Feedback: Stores the feedback in the database.

     get_all_feedback(db: Session, report_id: Optional[int] = None) -> List[Feedback]: Retrieves feedback entries, with optional filtering.

     Test Cases (backend/tests/test_feedback_service.py - New):
          Test submit_feedback with various valid inputs.
          Test get_all_feedback and its filtering capabilities.

Frontend:
     frontend/templates/user/report_detail.html (Update):
          Explanation: On the detailed report view page, add a section or a button that allows the user to provide feedback. This could be a simple text area or a modal dialog with rating options.

     frontend/static/js/user/reports.js (Update):
          Explanation: Add functionality to handle the feedback submission form/button. This will involve making AJAX calls to the /api/feedback POST endpoint.

     frontend/templates/staff/feedback_review.html (New):
          Explanation: A dedicated UI page for analysts to review submitted feedback. This page will likely display feedback in a table, showing report_id, user_id, feedback_text, rating, etc. It should allow analysts to filter, sort, and potentially link back to the original report and the prompt version used for that report.

     frontend/static/js/staff/feedback_review.js (New):
          Explanation: JavaScript to fetch and display feedback data from the backend/routes/feedback_routes.py GET endpoint. It will handle filtering and sorting, and potentially provide links to other relevant pages (e.g., detailed report, prompt management).

Priority 9: Advanced Data Visualization and Customization
Description: Extend existing data visualization capabilities to include more complex chart types, comparative analysis, and user-customizable dashboard elements.

Planned Functions/Files/APIs/Software:

Backend:
backend/routes/data_routes.py (Update):
     Explanation: Add more specific data retrieval endpoints tailored for advanced visualizations.

     @data_routes_bp.route('/industry_performance/<string:industry_name>', methods=['GET']): Endpoint to fetch aggregated financial data for an entire industry for comparative analysis.

     @data_routes_bp.route('/company_comparison/<list:tickers>', methods=['GET']): Endpoint to fetch financial data for multiple companies to enable side-by-side comparison charts.

     @data_routes_bp.route('/sector_trends', methods=['GET']): Endpoint to provide data for sector-level trend analysis.

     Test Cases (backend/tests/test_data_routes.py - Update/New):
          Test data retrieval for industry performance.
          Test data retrieval for multiple company comparisons.
          Test data retrieval for sector trends.

backend/services/data_service.py (Update):
     Explanation: Add functions to preprocess data specifically for these advanced visualizations.

     get_industry_performance_data(db: Session, industry_name: str, timeframe: str) -> List[Dict]: Aggregates and returns performance data for a given industry.

     get_comparative_financial_data(db: Session, company_ids: List[int], timeframe: str) -> Dict[str, List[Dict]]: Fetches and formats data for multiple companies for comparison.

     calculate_correlation_matrix(db: Session, company_ids: List[int], metric: str, start_date: date, end_date: date) -> Dict: Calculates correlation between specified financial metrics for selected companies.

     Test Cases (backend/tests/test_data_service.py - Update/New):
          Test get_industry_performance_data for correct aggregation.
          Test get_comparative_financial_data for accurate data retrieval and formatting.
          Test calculate_correlation_matrix for correct calculation with mock data.

Frontend:
     frontend/templates/user/dashboard.html (Update):
          Explanation: Introduce customizable widgets or sections on the dashboard. Users could potentially add/remove widgets to view different charts (e.g., industry performance, sector trends). This might involve a simple drag-and-drop interface or a configuration panel.

     frontend/templates/user/company_details.html (Update):
          Explanation: Implement new, more complex chart types.
          - Candlestick Charts: For detailed OHLCV visualization.
          - Correlation Matrices: To show relationships between different financial metrics or companies.
          - Comparative Line Charts: To compare performance of multiple companies.
          - Heatmaps: For quick visual identification of trends.

     frontend/static/js/dashboard.js, company_details.js (Update):
          Explanation: Implement new Chart.js functionalities to support the new chart types. This will involve parsing the data received from the new backend API endpoints and rendering them appropriately. If Chart.js limitations are met, consider integrating other visualization libraries like Plotly.js or D3.js.
          - renderCandlestickChart(canvasId, data): Function to render candlestick charts.
          - renderCorrelationMatrix(canvasId, data): Function to render correlation heatmaps.
          - renderComparativeChart(canvasId, data): Function to render comparative line charts.
          Software/APIs: Potentially integrate more advanced charting libraries (e.g., Plotly.js, D3.js) if Chart.js limitations are met.

Priority 10: Backtesting and Strategy Simulation
Description: Develop a module that allows quantitative traders and financial analysts to define trading strategies and backtest them against historical financial data to evaluate their performance.

Planned Functions/Files/APIs/Software:

Backend:
backend/models/backtest_model.py (New):
     Explanation: Defines models to store backtesting configurations and results.

     BacktestResult Table: result_id, user_id, strategy_name, start_date, end_date, initial_capital, final_capital, roi, sharpe_ratio, max_drawdown, trade_log (JSON/Text), equity_curve (JSON/Text), created_at.

     Strategy Table (Optional, for reusable strategies): strategy_id, user_id, strategy_name, rules_json (JSON/Text for defining entry/exit rules, indicators), description.

backend/routes/backtesting_routes.py (New):
@backtesting_routes_bp.route('/backtest', methods=['POST']):
     Explanation: Endpoint to initiate a backtesting simulation. It will receive parameters such as strategy_rules (JSON), company_id (or ticker), start_date, end_date, initial_capital. This endpoint will call backtesting_service.run_backtest.

     Test Cases (backend/tests/test_backtesting_routes.py - New):
          Test initiating a backtest with valid parameters.
          Test initiating a backtest with invalid strategy rules or date ranges.
          Test initiating a backtest as an unauthenticated user (should fail).

@backtesting_routes_bp.route('/backtest/results/<int:session_id>', methods=['GET']):
     Explanation: Retrieves the detailed results of a specific backtesting run.

     Test Cases (backend/tests/test_backtesting_routes.py - New):
          Test retrieving existing backtest results.
          Test retrieving results that don't belong to the user.
          Test retrieving non-existent results.

@backtesting_routes_bp.route('/backtest/history', methods=['GET']):
     Explanation: Retrieves a list of all backtesting runs for the authenticated user.

     Test Cases (backend/tests/test_backtesting_routes.py - New):
          Test retrieving backtest history for authenticated user.

backend/services/backtesting_service.py (New):
     Explanation: Contains the core logic for executing backtests and calculating performance metrics. This will be the most complex backend service.

     run_backtest(db: Session, user_id: int, company_id: int, strategy_rules: Dict, start_date: date, end_date: date, initial_capital: float) -> BacktestResult:
          Explanation:
          - Fetch historical FinancialData for the specified company and date range.
          - Parse strategy_rules to define entry and exit conditions (e.g., "Buy when RSI < 30", "Sell when price > 1.05 * entry_price").
          - Simulate trades day-by-day (or chosen interval) based on the rules and historical data.
          - Maintain portfolio state (cash, holdings).
          - Record each trade.
          - Calculate equity_curve (portfolio value over time).
          - Call calculate_performance_metrics.
          - Save the BacktestResult to the database.

          Test Cases (backend/tests/test_backtesting_service.py - New):
               Test run_backtest with simple, predefined rules and mock historical data to verify correct trade execution and portfolio value calculation.
               Test various strategy rule types (e.g., simple moving average crossover, volume-based).
               Test handling of insufficient capital scenarios.

     calculate_performance_metrics(equity_curve: List[float], trade_log: List[Dict]) -> Dict:
          Explanation: Calculates key metrics such as:
          - Return on Investment (ROI)
          - Sharpe Ratio (requires risk-free rate, possibly external input or assumption)
          - Maximum Drawdown
          - Number of trades, win rate, etc.

          Test Cases (backend/tests/test_backtesting_service.py - New):
               Test calculate_performance_metrics with various mock equity_curve and trade_log data to ensure correct calculation of ROI, Sharpe Ratio, drawdown.

Software/APIs: Python libraries for quantitative analysis (e.g., Pandas, NumPy for data manipulation; backtrader, zipline for comprehensive backtesting frameworks, or a custom implementation). The initial implementation might be custom for simplicity.

Frontend:
     frontend/templates/user/backtesting.html (New):
          Explanation: A UI for the backtesting module. It will likely include:
          - A form to define trading strategies (e.g., input fields for indicators, thresholds, entry/exit rules).
          - Date pickers for selecting the historical data range
          - Input for initial capital.
          - A "Run Backtest" button.
          - Sections to display backtesting results (performance metrics, trade log).
          - A chart to visualize the equity_curve.

     frontend/static/js/user/backtesting.js (New):
          Explanation: JavaScript to interact with the backtesting API endpoints. It will handle:
          - Form submission for strategy definition.
          - Making AJAX calls to /api/backtest to initiate simulations.
          - Fetching and rendering backtesting results.
          - Using Chart.js (or another library) to visualize the equity_curve and other relevant charts.

4. Backend Setup
Environment Configuration
Ensure your .env file in the backend/ directory is correctly configured with your actual database URL and API keys:

DATABASE_URL="mysql+mysqlconnector://root:YOUR_MYSQL_PASSWORD@localhost/fypquantanalysisplatform"
GOOGLE_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
NEWS_API_KEY="YOUR_NEWS_API_KEY_IF_APPLICABLE" # For Guardian or other news APIs
# PERPLEXITY_API_KEY="YOUR_PERPLEXITY_API_KEY" # If you enable Perplexity

Database Setup
Install MySQL: Ensure MySQL is installed and running on your system.

Create Database: Create the database named fypquantanalysisplatform (or whatever you configure in DATABASE_URL).

CREATE DATABASE fypquantanalysisplatform;

Execute SQL Scripts: Navigate to backend/db/tables/ and execute the .sql files to create the necessary tables:
     mysql -u root -p fypquantanalysisplatform < users.sql
     mysql -u root -p fypquantanalysisplatform < companies.sql
     mysql -u root -p fypquantanalysisplatform < financial_data.sql
     mysql -u root -p fypquantanalysisplatform < news.sql
     mysql -u root -p fypquantanalysisplatform < alerts.sql
     mysql -u root -p fypquantanalysisplatform < reports.sql
     mysql -u root -p fypquantanalysisplatform < feedback.sql
     mysql -u root -p fypquantanalysisplatform < prompts.sql
     # And any other new tables as per the detailed design (e.g., backtest_model.py)

Then, navigate to backend/db/views/ and execute the .sql files to create the database views:
     mysql -u root -p fypquantanalysisplatform < latest_company_financial_data.sql
     mysql -u root -p fypquantanalysisplatform < monthly_financial_data.sql
     mysql -u root -p fypquantanalysisplatform < weekly_financial_data.sql
     mysql -u root -p fypquantanalysisplatform < yearly_financial_data.sql
     mysql -u root -p fypquantanalysisplatform < avg_company_metrics.sql
     mysql -u root -p fypquantanalysisplatform < report_details.sql
     mysql -u root -p fypquantanalysisplatform < feedback_details.sql

Installing Dependencies
Navigate to your backend/ directory and install the Python dependencies:
     pip install -r requirements.txt

Running the Backend
To run the Flask backend, navigate to the backend/ directory and execute app.py:
     python app.py

This will start the Flask development server, typically on http://127.0.0.1:5000/.

5. Frontend Setup
Setting up the Frontend Environment
The frontend primarily uses HTML, CSS, and JavaScript with CDN-linked libraries. No specific build tools like Webpack or Node.js are strictly required for the current setup, as libraries are loaded via CDN.

Running the Frontend
The frontend HTML files are served by the Flask backend. Once the backend is running, you can access the frontend by navigating to the appropriate URLs in your web browser (e.g., http://127.0.0.1:5000/user/dashboard or http://127.0.0.1:5000/company_details.html).

6. External API Integration
Yahoo Finance API (via yfinance library)
     Purpose: Retrieval of news, historical financial data (OHLCV), market capitalization, dividends, and other company-specific financial metrics.
     Location: Integrated into backend/services/data_service.py and backend/api.py using the yfinance Python library. This is an unofficial wrapper for Yahoo Finance, so it doesn't require a direct API key for Yahoo Finance itself.

The Guardian API
     Purpose: Retrieval of industry-specific news articles.
     Endpoint: https://content.guardianapis.com/search
     API Key Location: The guardian_api_key is hardcoded as "ce66226f-693d-42a5-9023-3b003666df2a" in the code. It is highly recommended to move this API key to an environment variable (e.g., in backend/.env) for security and best practices, similar to how other API keys are handled.

Google Generative AI (Gemini API)
     Purpose: Performing news summary and sentiment analysis reports.
     Model Used: gemini-2.0-flash-lite.
     API Key Location: The GOOGLE_API_KEY is retrieved from environment variables using os.getenv("GOOGLE_API_KEY"). A hardcoded example AIzaSyAqNKqCXp366ThEy09XpAywQcpvKmqIPtk is also present for demonstration purposes; this should be replaced with a secure key in your .env file.

Perplexity AI API
     Purpose: Although mentioned in llm_service.py as a potential LLM provider, it is explicitly noted as "not updated yet & not in use".
     API Key Location: Expected to be retrieved from an environment variable PERPLEXITY_API_KEY.

7. Database Schema
Refer to the backend/models/ directory for the SQLAlchemy model definitions (user_model.py, data_model.py, alert_model.py, feedback_model.py, prompt_model.py, report_model.py, backtest_model.py).

The detailed SQL schema for tables and views can be found in backend/db/tables/ and backend/db/views/ respectively, and are also documented in datatables.md.

8. Running Tests
Backend Tests
To run the backend tests, navigate to the backend/ directory and use pytest.
     pytest

Specific test files for each service and route have been outlined in the "Implementation Roadmap" section. Ensure these are created and populated with test cases as development progresses.

Frontend Tests (if applicable)
(Currently, no explicit frontend testing framework is set up. This section would be updated if unit/integration tests for JavaScript components are implemented.)

9. Deployment (Optional)
(This section would contain details on deployment strategies, e.g., using Gunicorn/Nginx, Docker, cloud platforms like AWS, Google Cloud, or Azure.)

10. Contributing
(This section would contain guidelines for contributing to the project, coding standards, pull request process, etc.)

11. License
(This section would specify the project's license.)
