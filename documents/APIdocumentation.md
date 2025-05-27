Financial Analysis Platform API - Version 1.0.0 
Title: Financial Analysis Platform API 
Version: 1.0.0
Date: May 23, 2025 (Updated)
Description: API for accessing comprehensive financial data, AI-powered news analysis, interactive visualizations, and administrative functions for prompt management.
1. Servers
URL: http://localhost:8000 (Replace with your actual server URL)
Description: Local development server
2. Paths
2.1. /companies/{ticker}/financials (GET)
Summary: Get historical financial data for a company.
Description: Retrieves the last 20 historical financial data points for a given stock ticker.
Parameters:
ticker (path, string, required): The stock ticker symbol (e.g., AAPL).
Responses:
200 OK:
Description: Successful retrieval of financial data.
Content (application/json):
Schema (array of objects):
items (object):
properties:
data_id (integer)
company_id (integer)
date (string, format: date)
open (number, format: float)
high (number, format: float)
low (number, format: float)
close (number, format: float)
volume (integer)
roi (number, format: float)
eps (number, format: float)
pe_ratio (number, format: float)
revenue (integer, format: int64)
debt_to_equity (number, format: float)
cash_flow (integer, format: int64)
created_at (string, format: date-time)
updated_at (string, format: date-time)
404 Not Found:
Description: Company not found or no financial data available.
500 Internal Server Error:
Description: Internal server error.
2.2. /companies/{ticker}/news (GET)
Summary: Get recent news articles for a company with sentiment analysis.
Description: Retrieves recent news articles for a given stock ticker and includes the sentiment analysis of each article's title.
Parameters:
ticker (path, string, required): The stock ticker symbol (e.g., GOOGL).
Responses:
200 OK:
Description: Successful retrieval of news with sentiment.
Content (application/json):
Schema (array of objects):
items (object):
properties:
title (string)
link (string, format: url)
publisher (string)
sentiment (string, enum: [positive, negative, neutral])
404 Not Found:
Description: Company not found or no news available.
500 Internal Server Error:
Description: Internal server error.
2.3. /visualizations/{ticker}/basic_price (GET)
Summary: Get a basic stock price chart for a company.
Description: Generates and returns a base64 encoded PNG image of the historical stock price chart for a given ticker.
Parameters:
ticker (path, string, required): The stock ticker symbol.
Responses:
200 OK:
Description: Successful generation of the price chart.
Content (application/json):
Schema (object):
properties:
image_data (string): Base64 encoded PNG image data.
404 Not Found:
Description: Company not found or no data for chart generation.
500 Internal Server Error:
Description: Internal server error.
2.4. /visualizations/{ticker}/basic_volume (GET)
Summary: Get a basic trading volume chart for a company.
Description: Generates and returns a base64 encoded PNG image of the historical trading volume chart for a given ticker.
Parameters:
ticker (path, string, required): The stock ticker symbol.
Responses:
200 OK:
Description: Successful generation of the volume chart.
Content (application/json):
Schema (object):
properties:
image_data (string): Base64 encoded PNG image data.
404 Not Found:
Description: Company not found or no data for chart generation.
500 Internal Server Error:
Description: Internal server error.
2.5. /premium_visualizations/{ticker}/advanced_price (GET)
Summary: Get an advanced stock price chart with trendline for a company (Premium).
Description: Generates and returns a base64 encoded PNG image of the historical stock price chart with a calculated trendline for a given ticker. Requires premium access.
Parameters:
ticker (path, string, required): The stock ticker symbol.
Responses:
200 OK:
Description: Successful generation of the advanced price chart.
Content (application/json):
Schema (object):
properties:
image_data (string): Base64 encoded PNG image data.
404 Not Found:
Description: Company not found or no data for chart generation.
403 Forbidden:
Description: Premium access required.
500 Internal Server Error:
Description: Internal server error.
2.6. /premium_visualizations/{ticker}/llm_forecast (GET)
Summary: Get a stock price chart with LLM-based trend annotations for a company (Premium).
Description: Generates and returns a base64 encoded PNG image of the historical stock price chart annotated with trend information identified by an LLM. Requires premium access.
Parameters:
ticker (path, string, required): The stock ticker symbol.
Responses:
200 OK:
Description: Successful generation of the LLM forecast chart.
Content (application/json):
Schema (object):
properties:
image_data (string): Base64 encoded PNG image data.
404 Not Found:
Description: Company not found or no data for chart generation.
403 Forbidden:
Description: Premium access required.
500 Internal Server Error:
Description: Internal server error.
2.7. /premium_visualizations/{ticker}/llm_analysis (GET)
Summary: Get raw LLM analysis of financial trends for a company (Premium).
Description: Retrieves and returns the raw textual analysis of financial trends for a given ticker as analyzed by an LLM. Requires premium access.
Parameters:
ticker (path, string, required): The stock ticker symbol.
Responses:
200 OK:
Description: Successful retrieval of LLM analysis.
Content (application/json):
Schema (object):
properties:
analysis (string)
404 Not Found:
Description: Company not found or no data for analysis.
403 Forbidden:
Description: Premium access required.
500 Internal Server Error:
Description: Internal server error.
2.8. /api/llm/sentiment/<int:company_id> (GET)
Summary: Get a detailed news sentiment analysis report for a company.
Description: Retrieves a comprehensive report on news sentiment, market outlook, key offerings, and significant financial dates for a given company, analyzed using Google Gemini API. This endpoint combines various aspects of company analysis for a holistic view.
Parameters:
company_id (path, integer, required): The ID of the company.
Responses:
200 OK:
Description: Successful retrieval of the news analysis report.
Content (application/json):
Schema (object):
properties:
report (object):
overall_news_summary (string): A concise summary of the key news trends and events. HTML tags are used for emphasis.
brief_overall_sentiment (string): A brief sentiment (e.g., "Positive", "Negative", "Mixed", "Neutral") accompanied by a confidence score out of 100 (e.g., "Mixed (Score: 60/100)"). Briefly explains the score.
reasons_for_sentiment (string): A detailed explanation of why the overall sentiment is as it is, explicitly mentioning positive, negative, and neutral factors (including financial reports, political/geopolitical factors, environmental, and company structure/human factors) from the news that contribute to this sentiment. HTML tags are used for emphasis.
market_outlook (string): Describes the potential near-term market outlook for this company based on the news, identifying key drivers. HTML tags are used for emphasis.
detailed_explanation (string): Elaborates on the "Market Outlook," providing specific financial predictions, important financial news, and other relevant details that explain why the market outlook is as stated. HTML tags are used for emphasis.
key_offerings (array of strings): A list of the company's best-selling or most significant products, services, and/or subsidiaries.
financial_dates (array of objects): An array of objects, each representing a key financial event.
items (object):
properties:
date (string): The date of the event (e.g., "2025-05-15" or "Q3 2024").
event (string): A brief description of the event (e.g., "Q4 Earnings Call", "Investor Day", "Regulatory Decision on Merger").
impact (string): A short explanation of its potential or actual impact on market outlook and sentiment.
404 Not Found:
Description: Company not found or no news available for analysis.
500 Internal Server Error:
Description: Internal server error.
2.9. /export/financials/{ticker} (POST)
Summary: Export basic financial data to CSV for a company.
Description: Exports the historical financial data for a given ticker to a CSV file, which is returned as a download.
Parameters:
ticker (path, string, required): The stock ticker symbol.
Responses:
200 OK:
Description: Successful export of financial data.
Content (text/csv):
Schema (string)
404 Not Found:
Description: Company not found or no financial data available.
500 Internal Server Error:
Description: Internal server error.
3. Analyst Specific Endpoints
3.1. /prompts (GET)
Summary: Get all LLM prompts (Analyst).
Description: Retrieves a list of all stored LLM prompts. Requires analyst role.
Security:
BearerAuth: [] (Placeholder for actual authentication)
Responses:
200 OK:
Description: Successful retrieval of prompts.
Content (application/json):
Schema (array of objects):
items (object):
properties:
prompt_id (integer)
name (string)
description (string)
created_by (integer)
created_at (string, format: date-time)
updated_at (string, format: date-time)
403 Forbidden:
Description: Analyst role required.
500 Internal Server Error:
Description: Internal server error.
3.2. /prompts (POST)
Summary: Create a new LLM prompt (Analyst).
Description: Creates a new LLM prompt. Requires analyst role.
Security:
BearerAuth: [] (Placeholder for actual authentication)
Request Body (application/json, required):
Schema (object):
properties:
name (string)
description (string)
required:
name
description
Responses:
201 Created:
Description: Successful creation of the prompt.
Content (application/json):
Schema (object):
properties:
prompt_id (integer)
name (string)
description (string)
created_by (integer)
created_at (string, format: date-time)
updated_at (string, format: date-time)
400 Bad Request:
Description: Invalid request body.
403 Forbidden:
Description: Analyst role required.
500 Internal Server Error:
Description: Internal server error.
3.3. /prompts/{prompt_id}/versions (GET)
Summary: Get all versions of a specific LLM prompt (Analyst).
Description: Retrieves all versions of the LLM prompt with the given ID. Requires analyst role.
Security:
BearerAuth: [] (Placeholder for actual authentication)
Parameters:
prompt_id (path, integer, required): The ID of the prompt.
Responses:
200 OK:
Description: Successful retrieval of prompt versions.
Content (application/json):
Schema (array of objects):
items (object):
properties:
prompt_version_id (integer)
prompt_id (integer)
user_id (integer)
version (integer)
operative (boolean)
original_prompt (string)
prompt_text (string)
created_at (string, format: date-time)
updated_at (string, format: date-time)
403 Forbidden:
Description: Analyst role required.
404 Not Found:
Description: Prompt not found.
500 Internal Server Error:
Description: Internal server error.
3.4. /prompts/{prompt_id}/versions (POST)
Summary: Create a new version for a specific LLM prompt (Analyst).
Description: Creates a new version for the LLM prompt with the given ID. Requires analyst role.
Security:
BearerAuth: [] (Placeholder for actual authentication)
Parameters:
prompt_id (path, integer, required): The ID of the prompt.
Request Body (application/json, required):
Schema (object):
properties:
original_prompt (string)
prompt_text (string)
required:
original_prompt
prompt_text
Responses:
201 Created:
Description: Successful creation of the prompt version.
Content (application/json):
Schema (object):
properties:
prompt_version_id (integer)
prompt_id (integer)
user_id (integer)
version (integer)
operative (boolean)
original_prompt (string)
prompt_text (string)
created_at (string, format: date-time)
updated_at (string, format: date-time)
400 Bad Request:
Description: Invalid request body.
403 Forbidden:
Description: Analyst role required.
404 Not Found:
Description: Prompt not found.
500 Internal Server Error:
Description: Internal server error.
3.5. /prompts/versions/{prompt_version_id}/activate (PATCH)
Summary: Set a specific prompt version as active (Analyst).
Description: Sets the prompt version with the given ID as the active version for its prompt. Requires analyst role.
Security:
BearerAuth: [] (Placeholder for actual authentication)
Parameters:
prompt_version_id (path, integer, required): The ID of the prompt version to activate.
Responses:
200 OK:
Description: Successful activation of the prompt version.
Content (application/json):
Schema (object):
properties:
prompt_version_id (integer)
prompt_id (integer)
user_id (integer)
version (integer)
operative (boolean)
original_prompt (string)
prompt_text (string)
created_at (string, format: date-time)
updated_at (string, format: date-time)
403 Forbidden:
Description: Analyst role required.
404 Not Found:
Description: Prompt version not found.
500 Internal Server Error:
Description: Internal server error.
4. Components
4.1. Security Schemes - BearerAuth
Type: http
Scheme: bearer
BearerFormat: JWT
Description: Placeholder for actual authentication (e.g., JWT).

5. Software and API Dependencies
This section details the Python packages and external APIs used in the project, along with their installation commands and versions.
5.1. Python Packages
To set up the project environment, ensure you have Python 3.9+ installed. Then, navigate to your project directory and run the following commands:
Bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies from requirements.txt
pip install -r requirements.txt


Below is a list of key Python packages used:
Flask: Flask==2.3.3 (Web framework for building the API)
SQLAlchemy: SQLAlchemy==2.0.25 (ORM for database interaction)
psycopg2-binary: psycopg2-binary==2.9.9 (PostgreSQL adapter for SQLAlchemy, if using PostgreSQL. Note: The config.py shows MySQL, so this might vary based on your actual DB. For MySQL, it would be mysql-connector-python or PyMySQL.)
yfinance: yfinance==0.2.38 (Used for fetching financial data and news from Yahoo Finance)
requests: requests==2.31.0 (HTTP library for making API requests)
google-generativeai: google-generativeai==0.6.0 (Official Google client library for Gemini API)
python-dotenv: python-dotenv==1.0.1 (For loading environment variables from a .env file)
APScheduler: APScheduler==3.10.4 (For scheduling background tasks like daily news updates)
pytz: pytz==2023.3.post1 (For timezone calculations, especially for scheduled tasks)
pandas: pandas==2.1.4 (Used for data manipulation, particularly in data services and potentially for charts)
matplotlib: matplotlib==3.8.2 (Used for generating charts)
scipy: scipy==1.11.4 (Potentially used for statistical analysis like trendlines in advanced charts)
Flask-Cors: Flask-Cors==4.0.0 (For handling Cross-Origin Resource Sharing)
Werkzeug: Werkzeug==2.3.7 (WSGI utility library, dependency of Flask)
5.2. External APIs
Google Gemini API:
Provider: Google
Models Used: gemini-2.0-flash-lite (used for sentiment analysis in llm_service.py and llm_routes.py). gemini-pro may also be used for more complex prompt adherence.
Description: A powerful large language model used for sophisticated news sentiment analysis, market outlook generation, and identification of key company offerings and financial dates.
Public API Link: Google Gemini API Documentation
Yahoo Finance:
Provider: Yahoo
Access Method: Accessed indirectly via the yfinance Python library.
Description: Provides historical stock data (OHLCV, fundamentals), company information, and company-specific news.
Public API Link: While yfinance uses Yahoo Finance's public web scraping, there isn't a formal public API documentation link in the same way as Google Gemini.
The Guardian API:
Provider: The Guardian
Description: Used to fetch broader industry-specific news articles.
Public API Link: The Guardian Open Platform API
Perplexity API (Planned/Placeholder):
Provider: Perplexity AI
Description: Mentioned in llm_service.py as analyze_news_sentiment_perplexity but currently noted as "not updated yet & not in use". Indicates potential future integration for alternative LLM-based sentiment analysis.
Public API Link: Perplexity AI API Documentation
6. File and Function Breakdown
This section details the purpose of each key file and the primary functions contained within them.
api.py


Purpose: Serves as a central blueprint for various API endpoints, particularly for retrieving company financial data from the database and potentially external sources like Yahoo Finance. It also includes utility functions for formatting.
Key Functions:
format_market_cap(market_cap): Formats market capitalization into a human-readable string (e.g., T, B, M).
get_company_financial_data(company_id): Fetches financial data for a given company_id from the database and augments it with real-time Yahoo Finance data (market cap, earnings date, dividends, etc.).
app.py


Purpose: The main Flask application entry point. It sets up the Flask app, registers blueprints, initializes the database, configures CORS, schedules background tasks (like daily news and financial data updates), and defines core routes (e.g., /company_details.html).
Key Functions:
create_app(testing, start_scheduler): Initializes and configures the Flask application.
index(): Redirects to the user dashboard.
company_details(): Renders the company_details.html page.
company_detail_page(ticker): Renders the company_details.html page with a specific ticker.
get_company_news(ticker): Fetches recent company and industry news for a given ticker, used by the frontend.
config.py


Purpose: Stores configuration variables, primarily the database connection URL.
Key Variables:
DATABASE_URL: Defines the SQLAlchemy database connection string.
database.py


Purpose: Manages database connections and provides CRUD (Create, Read, Update, Delete) operations for various models (Company, FinancialData, News, User, Prompt, PromptVersion, etc.). It ensures session management and proper transaction handling.
Key Functions:
get_engine(app): Returns the SQLAlchemy engine.
get_session_local(app): Returns a configured SQLAlchemy session factory.
get_db(): Provides a database session for request contexts.
init_db(app): Initializes the database schema based on defined models.
get_all_companies(db): Retrieves all companies.
get_company_by_ticker(db, ticker): Retrieves a company by its ticker symbol.
create_company(db, company_name, ticker_symbol, industry, exchange): Adds a new company.
Numerous get_, create_, update_, delete_ functions for FinancialData, News, User, Prompt, PromptVersion, etc.
tasks.py


Purpose: Defines background tasks that are scheduled to run periodically, such as daily news updates and daily financial data updates.
Key Functions:
daily_news_update(app): Fetches and stores the latest news for all companies at a scheduled time.
update_all_financial_data(app): Fetches and stores the latest financial data for all companies at a scheduled time.
update_financial_data_for_company(db, company): Helper function to update financial data for a single company, used by update_all_financial_data.
data_routes.py


Purpose: Defines API routes (Blueprint) related to fetching and managing financial data, including historical data, and potentially news (though some news routes are in app.py).
Key Functions:
needs_update(db, company_id, threshold_hours): Checks if a company's financial data needs updating based on a timestamp.
ingest_data(): (Placeholder/initial data ingestion, likely for testing or one-time setup).
get_financial_data(period): Retrieves financial data for a selected company based on a specified period (daily, weekly, monthly, yearly).
get_company_news(): Retrieves stored news articles for a selected company.
graph_routes.py


Purpose: Defines API routes (Blueprint) for retrieving data necessary to generate stock price and volume charts based on different timeframes.
Key Functions:
Workspace_graph_data(db, company_id, timeframe): Fetches historical close price and volume data for a given company and timeframe (weekly, monthly, yearly, max).
get_company_graph_data(company_id, timeframe): Endpoint to return the fetched graph data.
llm_routes.py


Purpose: Defines API routes (Blueprint) specifically for interacting with LLM services, primarily for news sentiment analysis.
Key Functions:
not_found(error): Custom error handler for 404 Not Found within this blueprint.
get_company_news_sentiment(company_id): The core endpoint that retrieves news, constructs a detailed prompt, calls the LLM service (Gemini), and returns a comprehensive sentiment report, including market outlook, key offerings, and financial dates.
data_service.py


Purpose: Contains business logic for fetching, storing, and processing financial data and news from external sources (yfinance, The Guardian API).
Key Functions:
Workspace_financial_data(ticker, period, start, end, ...): Fetches historical OHLCV data from Yahoo Finance.
store_financial_data(db, ticker, ...): Stores fetched financial data into the database.
Workspace_historical_fundamentals(ticker): Fetches key fundamental data points.
Workspace_latest_news(query, industry, exchange, ...): Fetches news from Yahoo Finance (for company) and The Guardian (for industry).
store_news_articles(db, news_data, company_id): Stores fetched news articles into the database.
get_stored_news(db, company_id, limit): Retrieves news articles from the database.
predict_financial_trends(financial_data): (Placeholder) Analyzes financial data to predict trends.
get_similar_companies(industry): (Placeholder) Provides a list of similar companies.
llm_service.py


Purpose: Encapsulates the logic for interacting with various Large Language Models (LLMs), currently Google Gemini, to perform news sentiment analysis. It handles API calls, response parsing, and error handling for LLM interactions.
Key Functions:
analyze_news_sentiment(news_articles, llm_provider, prompt, llm_model): A high-level function that dispatches to specific LLM providers (e.g., Gemini, Perplexity).
analyze_news_sentiment_gemini(news_articles, prompt, llm_model): Specifically interacts with the Google Gemini API to analyze news sentiment, taking a custom prompt and returning a structured JSON response with detailed sentiment, market outlook, and financial dates.
analyze_news_sentiment_perplexity(news_articles, llm_model): (Placeholder/Not in use) Function for Perplexity API integration.
_infer_sentiment(text): A helper function to infer a brief sentiment (Positive, Negative, Mixed, Neutral) from a given text.