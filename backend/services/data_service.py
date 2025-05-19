# backend/services/data_service.py
from sqlalchemy import func
import yfinance as yf
from sqlalchemy.orm import Session
from backend import database
from backend.models import Company, FinancialData, News
from datetime import date, datetime, time, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
import pandas as pd
import os
import requests
import pytz

logging.basicConfig(level=logging.INFO)

def fetch_financial_data(ticker: str, period: str = None, start: Optional[date] = None, end: Optional[date] = None, retries: int = 3, delay: float = 5, db: Optional[Session] = None, company_id: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
    """Fetches historical OHLCV data from yfinance with retry and storage logic."""
    print(f"[DEBUG - fetch_financial_data] Called for ticker: {ticker}, DB Session: {db}, Company ID: {company_id}") # Add this line
    if db is None or company_id is None:
        logging.error(f"Database session or company_id not provided for {ticker}.")
        return None
    for attempt in range(retries):
        try:
            if period and not start and not end:
                data = yf.download(ticker, period=period)
            elif start and end and not period:
                data = yf.download(ticker, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
            else:
                logging.error(f"Invalid parameters for fetch_financial_data. Must provide either 'period' or both 'start' and 'end'.")
                return None

            if data.empty:
                logging.warning(f"No OHLCV data received from yfinance for {ticker} (period: {period}, start: {start}, end: {end})")
                return None
            financial_data_list = []
            for index, row in data.iterrows():
                try:
                    if isinstance(index, pd.Timestamp):
                        data_date = index.to_pydatetime().date()
                    else:
                        data_date = index

                    financial_data_list.append({
                        "date": data_date,
                        "open": row['Open'].item(),
                        "high": row['High'].item(),
                        "low": row['Low'].item(),
                        "close": row['Close'].item(),
                        "volume": row['Volume'].item()
                    })
                except (TypeError, ValueError) as e:
                    logging.error(f"Error converting OHLCV data for {ticker} on {index}: {e}")
                    continue
            store_fetched_financial_data(db, company_id, financial_data_list) # Store here
            return financial_data_list
        except requests.exceptions.RequestException as e:
            if "Too Many Requests" in str(e):
                wait_time = delay * (attempt + 1)  # Exponential backoff
                logging.warning(f"Rate limited by yfinance for {ticker}. Retrying in {wait_time:.2f} seconds (attempt {attempt + 1}/{retries}).")
                time.sleep(wait_time)
            elif "YFPricesMissingError" in str(e):
                logging.warning(f"No data found for {ticker}: {e}")
                return []
            else:
                logging.error(
                    f"Error fetching OHLCV data for {ticker} (period: {period}, start: {start}, end: {end}): {e}")
                return None
        except Exception as e:
            logging.error(
                f"Error fetching OHLCV data for {ticker} (period: {period}, start: {start}, end: {end}): {e}")
            return None
    logging.error(f"Failed to fetch OHLCV data for {ticker} after {retries} attempts.")
    return None

def store_fetched_financial_data(db: Session, company_id: int, data_list: List[Dict[str, Any]]):
    """Stores a list of fetched financial data points in the database."""
    added_count = 0
    for data_point in data_list:
        existing_record = (
            db.query(FinancialData)
            .filter(
                FinancialData.company_id == company_id,
                FinancialData.date == data_point['date'],
            )
            .first()
        )
        if not existing_record:
            try:
                financial_data = {
                    "company_id": company_id,
                    "date": data_point["date"],
                    "open": data_point["open"],
                    "high": data_point["high"],
                    "low": data_point["low"],
                    "close": data_point["close"],
                    "volume": data_point["volume"],
                    # Add other fields if needed
                }
                db.add(FinancialData(**financial_data))
                added_count += 1
            except Exception as e:
                logging.error(f"Error creating financial data for company {company_id} and date {data_point['date']}: {e}")
                db.rollback() # Rollback immediately on error for a single record
    if added_count > 0:
        try:
            db.flush() # Flush to batch inserts if needed
            db.commit()
            logging.info(f"Added {added_count} new financial records for company {company_id}.")
        except Exception as e:
            logging.error(f"Error committing financial data to the database: {e}")
            db.rollback()
    else:
        logging.info(f"No new financial records to add for company {company_id}.")

def fetch_historical_fundamentals(ticker: str, years: int = 5) -> Optional[Dict[date, Dict[str, Any]]]:
    """Fetches historical fundamental data (annual) from yfinance with enhanced key handling."""
    print(f"[DEBUG]-fetch_historical_fundamentals: >>> ENTERING FUNCTION <<< for {ticker}")
    print(f"[DEBUG]-fetch_historical_fundamentals: Fetching historical fundamentals for {ticker} for the last {years} years.")
    try:
        tk = yf.Ticker(ticker)
        historical_prices = tk.history(period=f"{years}y")
        #print(f"[DEBUG]-fetch_historical_fundamentals: Fetched Historical Prices:\n{historical_prices.head().to_string()}")
        #print(f"[DEBUG]-fetch_historical_fundamentals: Attributes of yf.Ticker('{ticker}'): {dir(tk)}")

        income_statement = tk.income_stmt
        balance_sheet = tk.balance_sheet
        cashflow = tk.cashflow

        #print(f"[DEBUG]-fetch_historical_fundamentals: Fetched Income Statement:\n{income_statement.head().to_string()}")
        #print(f"[DEBUG]-fetch_historical_fundamentals: Income Statement Index:\n{income_statement.index.to_list()}")
        #print(f"[DEBUG]-fetch_historical_fundamentals: Fetched Balance Sheet:\n{balance_sheet.head().to_string()}")
        #print(f"[DEBUG]-fetch_historical_fundamentals: Balance Sheet Index:\n{balance_sheet.index.to_list()}")
        #print(f"[DEBUG]-fetch_historical_fundamentals: Fetched Cash Flow:\n{cashflow.head().to_string()}")

        if income_statement.empty or balance_sheet.empty or cashflow.empty:
            print(f"[DEBUG]-fetch_historical_fundamentals: WARNING: Retrieved fundamental statements are empty for {ticker}.")
            return {}

        fundamental_data = {}
        num_years = min(years, len(income_statement.columns) if not income_statement.empty else 0)

        for i in range(num_years):
            try:
                col_is = income_statement.columns[i] if not income_statement.empty else None
                col_bs = balance_sheet.columns[i] if not balance_sheet.empty else None
                col_cf = cashflow.columns[i] if not cashflow.empty else None

                reporting_date = None
                if col_is is not None:
                    reporting_date = pd.to_datetime(col_is).date()

                if reporting_date:
                    fundamental_data[reporting_date] = {}

                    def get_value(df, keys, col):
                        if df is None or df.empty or col is None:
                            return None
                        for key in keys:
                            if key in df.index and col in df.columns and pd.notna(df.loc[key, col]):
                                return df.loc[key, col]
                        return None

                    eps_keys = ['BasicEPS', 'EPSBasic', 'DilutedEPS', 'EPSDiluted', 'Basic EPS', 'Diluted EPS']
                    eps = get_value(income_statement, eps_keys, col_is)
                    #print(f"[DEBUG]-fetch_historical_fundamentals - {reporting_date.year}: EPS from yfinance = {eps}")
                    fundamental_data[reporting_date]['eps'] = eps

                    revenue_keys = ['TotalRevenue', 'Revenue', 'NetSales', 'Total Revenue']
                    revenue = get_value(income_statement, revenue_keys, col_is)
                    #print(f"[DEBUG]-fetch_historical_fundamentals - {reporting_date.year}: Revenue from yfinance = {revenue}")
                    fundamental_data[reporting_date]['revenue'] = revenue

                    total_debt_keys = ['TotalDebt', 'Total Liabilities', 'Liabilities', 'Long Term Debt And Capital Lease Obligation', 'Long Term Debt', 'Current Debt']
                    total_debt = get_value(balance_sheet, total_debt_keys, col_bs)
                    #print(f"[DEBUG]-fetch_historical_fundamentals - {reporting_date.year}: Total Debt from yfinance = {total_debt}")
                    fundamental_data[reporting_date]['total_debt'] = total_debt

                    stockholders_equity_keys = ["Stockholders' Equity", 'StockholdersEquity', 'Total Stockholders Equity', 'Equity', 'Common Stock Equity']
                    stockholders_equity = get_value(balance_sheet, stockholders_equity_keys, col_bs)
                    #print(f"[DEBUG]-fetch_historical_fundamentals - {reporting_date.year}: Stockholders Equity from yfinance = {stockholders_equity}")
                    fundamental_data[reporting_date]['stockholders_equity'] = stockholders_equity

                    total_debt_val = fundamental_data[reporting_date].get('total_debt')
                    stockholders_equity_val = fundamental_data[reporting_date].get('stockholders_equity')
                    debt_to_equity = total_debt_val / stockholders_equity_val if stockholders_equity_val and total_debt_val is not None and stockholders_equity_val != 0 else None
                    #print(f"[DEBUG]-fetch_historical_fundamentals - {reporting_date.year}: Debt-to-Equity from yfinance = {debt_to_equity}")
                    fundamental_data[reporting_date]['debt_to_equity'] = debt_to_equity

                    cash_flow_keys = ['OperatingCashFlow', 'Operating Cash Flow', 'Net Cash from Operations']
                    cash_flow = get_value(cashflow, cash_flow_keys, col_cf)
                    #print(f"[DEBUG]-fetch_historical_fundamentals - {reporting_date.year}: Operating Cash Flow from yfinance = {cash_flow}")
                    fundamental_data[reporting_date]['cash_flow'] = cash_flow

                    net_income_keys = ['Net Income', 'NetIncome']
                    net_income = get_value(income_statement, net_income_keys, col_is)
                    #print(f"[DEBUG]-fetch_historical_fundamentals - {reporting_date.year}: Net Income from yfinance = {net_income}")

                    roi = net_income / stockholders_equity_val if stockholders_equity_val and net_income is not None and stockholders_equity_val != 0 else None
                    #print(f"[DEBUG]-fetch_historical_fundamentals - {reporting_date.year}: ROI from yfinance = {roi}")
                    fundamental_data[reporting_date]['roi'] = roi

                    # --- START OF PE RATIO CALCULATION ---
                    # Find a relevant stock price (e.g., price on or close to the reporting date)
                    try:
                        # Find the closing price on or the closest day to the reporting date
                        closest_price_date = min(historical_prices.index, key=lambda date: abs((pd.to_datetime(date).date() - reporting_date).days))
                        historical_price = historical_prices.loc[closest_price_date]['Close']
                        #print(f"[DEBUG]-fetch_historical_fundamentals - {reporting_date.year}: Historical Price on {closest_price_date.date()} = {historical_price}")
                        if eps is not None and historical_price is not None and eps != 0:
                            historical_pe_ratio = historical_price / eps
                            #print(f"[DEBUG]-fetch_historical_fundamentals - {reporting_date.year}: Calculated Historical PE Ratio = {historical_pe_ratio}")
                            fundamental_data[reporting_date]['pe_ratio'] = historical_pe_ratio
                        else:
                            fundamental_data[reporting_date]['pe_ratio'] = None
                            print(f"[DEBUG]-fetch_historical_fundamentals - {reporting_date.year}: Could not calculate Historical PE Ratio (EPS or Price is None or EPS is zero).")
                    except KeyError:
                        print(f"[DEBUG]-fetch_historical_fundamentals - {reporting_date.year}: No historical price found for or near {reporting_date}.")
                        fundamental_data[reporting_date]['pe_ratio'] = None
                    # --- END OF PE RATIO CALCULATION ---                    
            except IndexError as e:
                print(f"[DEBUG]-fetch_historical_fundamentals - INDEX ERROR: {e} while accessing column at index {i}")
                continue
            except Exception as e:
                print(f"[DEBUG]-fetch_historical_fundamentals - PROCESSING ERROR: {e}")
                continue

        print(f"[DEBUG]-fetch_historical_fundamentals: Returning fundamental data: {fundamental_data}")
        return fundamental_data
    except Exception as e:
        print(f"[DEBUG]-fetch_historical_fundamentals: ERROR fetching historical fundamental data for {ticker}: {e}")
        return {}     
def _store_historical_fundamentals(db: Session, company: Company, fundamental_data_map: Dict[date, Dict[str, Any]]):
    """Internal function to store historical fundamental data with detailed debugging."""
    print(f"[DEBUG]-store_historical_fundamentals: Internal function: Storing historical fundamentals for {company.ticker_symbol}")
    updated_fundamentals_count = 0
    for fund_date, fund_values in fundamental_data_map.items():
        print(f"[DEBUG]-store_historical_fundamentals: Processing data for year: {fund_date.year}, values: {fund_values}")
        db_records = db.query(FinancialData).filter(
            FinancialData.company_id == company.company_id,
            FinancialData.date == fund_date
        ).all()

        if not db_records:
            print(f"[DEBUG]-store_historical_fundamentals: WARNING: No exact OHLCV record found for {company.ticker_symbol} on {fund_date}. Attempting to find a record within +/- 30 days or same month.")
            # Try to find a record within +/- 30 days
            start_range = fund_date - timedelta(days=30)
            end_range = fund_date + timedelta(days=30)
            nearby_records = db.query(FinancialData).filter(
                FinancialData.company_id == company.company_id,
                FinancialData.date >= start_range,
                FinancialData.date <= end_range
            ).order_by(func.abs(func.datediff(FinancialData.date, fund_date))).all()

            best_match = None
            same_month_records = [rec for rec in nearby_records if rec.date.year == fund_date.year and rec.date.month == fund_date.month]

            if same_month_records:
                best_match = min(same_month_records, key=lambda rec: abs((rec.date - fund_date).days))
                print(f"[DEBUG]-store_historical_fundamentals: INFO: Found a match within the same month for {company.ticker_symbol} fundamental date {fund_date} on OHLCV date {best_match.date}.")
            elif nearby_records:
                best_match = nearby_records[0]
                print(f"[DEBUG]-store_historical_fundamentals: INFO: Found a nearby match (+/- 30 days) for {company.ticker_symbol} fundamental date {fund_date} on OHLCV date {best_match.date}.")

            if best_match:
                db_record = best_match
                if db_record:
                    print(f"[DEBUG]-store_historical_fundamentals: Attempting to update record with date: {db_record.date} based on fundamental date: {fund_date}")
                else:
                    print(f"[DEBUG]-store_historical_fundamentals: WARNING: Could not retrieve database record for best match on {best_match.date}.")
                    continue
            else:
                print(f"[DEBUG]-store_historical_fundamentals: WARNING: No nearby OHLCV record found for {company.ticker_symbol} fundamental date {fund_date}.")
                continue # Skip to the next fundamental data point
        else:
            db_record = db_records[0] # If exact match, use the first record (should ideally be only one)
            print(f"[DEBUG]-store_historical_fundamentals: INFO: Exact match found for fundamental date {fund_date} with OHLCV date {db_record.date}")

        if db_record:
            print(f"[DEBUG]-store_historical_fundamentals: Examining record with date: {db_record.date} before potential update.")
            print(f"[DEBUG]-store_historical_fundamentals - Before: EPS={db_record.eps}, Revenue={db_record.revenue}, DebtToEquity={db_record.debt_to_equity}, CashFlow={db_record.cash_flow}, ROI={db_record.roi}, PERatio={db_record.pe_ratio}")
            updated = False

            yfinance_eps = fund_values.get('eps')
            if yfinance_eps is not None and db_record.eps != yfinance_eps:
                #print(f"[DEBUG]-store_historical_fundamentals: Updating EPS for {db_record.date} with yfinance value: {yfinance_eps} (was {db_record.eps}).")
                db_record.eps = yfinance_eps
                updated = True
            elif yfinance_eps is not None and db_record.eps is None:
                #print(f"[DEBUG]-store_historical_fundamentals: Setting EPS for {db_record.date} with yfinance value: {yfinance_eps}.")
                db_record.eps = yfinance_eps
                updated = True
            else:
                print(f"[DEBUG]-store_historical_fundamentals: EPS from yfinance is None or matches database value.")

            yfinance_revenue = fund_values.get('revenue')
            if yfinance_revenue is not None and db_record.revenue != yfinance_revenue:
                #print(f"[DEBUG]-store_historical_fundamentals: Updating Revenue for {db_record.date} with yfinance value: {yfinance_revenue} (was {db_record.revenue}).")
                db_record.revenue = yfinance_revenue
                updated = True
            elif yfinance_revenue is not None and db_record.revenue is None:
                #print(f"[DEBUG]-store_historical_fundamentals: Setting Revenue for {db_record.date} with yfinance value: {yfinance_revenue}.")
                db_record.revenue = yfinance_revenue
                updated = True
            else:
                print(f"[DEBUG]-store_historical_fundamentals: Revenue from yfinance is None or matches database value.")

            yfinance_debt_to_equity = fund_values.get('debt_to_equity')
            if yfinance_debt_to_equity is not None and db_record.debt_to_equity != yfinance_debt_to_equity:
                #print(f"[DEBUG]-store_historical_fundamentals: Updating DebtToEquity for {db_record.date} with yfinance value: {yfinance_debt_to_equity} (was {db_record.debt_to_equity}).")
                db_record.debt_to_equity = yfinance_debt_to_equity
                updated = True
            elif yfinance_debt_to_equity is not None and db_record.debt_to_equity is None:
                #print(f"[DEBUG]-store_historical_fundamentals: Setting DebtToEquity for {db_record.date} with yfinance value: {yfinance_debt_to_equity}.")
                db_record.debt_to_equity = yfinance_debt_to_equity
                updated = True
            else:
                print(f"[DEBUG]-store_historical_fundamentals: DebtToEquity from yfinance is None or matches database value.")

            yfinance_cash_flow = fund_values.get('cash_flow')
            if yfinance_cash_flow is not None and db_record.cash_flow != yfinance_cash_flow:
                #print(f"[DEBUG]-store_historical_fundamentals: Updating CashFlow for {db_record.date} with yfinance value: {yfinance_cash_flow} (was {db_record.cash_flow}).")
                db_record.cash_flow = yfinance_cash_flow
                updated = True
            elif yfinance_cash_flow is not None and db_record.cash_flow is None:
                #print(f"[DEBUG]-store_historical_fundamentals: Setting CashFlow for {db_record.date} with yfinance value: {yfinance_cash_flow}.")
                db_record.cash_flow = yfinance_cash_flow
                updated = True
            else:
                print(f"[DEBUG]-store_historical_fundamentals: CashFlow from yfinance is None or matches database value.")

            yfinance_roi = fund_values.get('roi')
            if yfinance_roi is not None and db_record.roi != yfinance_roi:
                #print(f"[DEBUG]-store_historical_fundamentals: Updating ROI for {db_record.date} with yfinance value: {yfinance_roi} (was {db_record.roi}).")
                db_record.roi = yfinance_roi
                updated = True
            elif yfinance_roi is not None and db_record.roi is None:
                #print(f"[DEBUG]-store_historical_fundamentals: Setting ROI for {db_record.date} with yfinance value: {yfinance_roi}.")
                db_record.roi = yfinance_roi
                updated = True
            else:
                print(f"[DEBUG]-store_historical_fundamentals: ROI from yfinance is None or matches database value.")

            yfinance_pe_ratio = fund_values.get('pe_ratio')
            if yfinance_pe_ratio is not None and db_record.pe_ratio != yfinance_pe_ratio:
                #print(f"[DEBUG]-store_historical_fundamentals: Updating PERatio for {db_record.date} with yfinance value: {yfinance_pe_ratio} (was {db_record.pe_ratio}).")
                db_record.pe_ratio = yfinance_pe_ratio
                updated = True
            elif yfinance_pe_ratio is not None and db_record.pe_ratio is None:
                #print(f"[DEBUG]-store_historical_fundamentals: Setting PERatio for {db_record.date} with yfinance value: {yfinance_pe_ratio}.")
                db_record.pe_ratio = yfinance_pe_ratio
                updated = True
            else:
                print(f"[DEBUG]-store_historical_fundamentals: PERatio from yfinance is None or matches database value.")

            if updated:
                updated_fundamentals_count += 1
                print(f"[DEBUG]-store_historical_fundamentals: INFO: Updated fundamentals for {company.ticker_symbol} on {db_record.date}.")
                print(f"[DEBUG]-store_historical_fundamentals - After Update: EPS={db_record.eps}, Revenue={db_record.revenue}, DebtToEquity={db_record.debt_to_equity}, CashFlow={db_record.cash_flow}, ROI={db_record.roi}, PE Ratio: {db_record.pe_ratio}")
            else:
                print(f"[DEBUG]-store_historical_fundamentals: No fundamental data updated for {company.ticker_symbol} on {db_record.date}.")

    if updated_fundamentals_count > 0:
        print(f"[DEBUG]-store_historical_fundamentals: INFO: Updated {updated_fundamentals_count} fundamental data points for {company.ticker_symbol}.")
    else:
        print(f"[DEBUG]-store_historical_fundamentals: INFO: No new fundamental data to store for {company.ticker_symbol}.")

def store_financial_data(db: Session, ticker: str, period: str = "5y") -> bool:
    """Stores historical OHLCV and annual fundamental data for a given ticker, linking them by date."""
    logging.debug(f"Storing financial data for ticker: {ticker}")
    company = database.get_company_by_ticker(db, ticker)
    if not company:
        company_info = yf.Ticker(ticker).info
        if company_info:
            company_data = {
                "ticker_symbol": company_info.get("symbol"),
                "company_name": company_info.get("longName"),
                "exchange": company_info.get("exchange"),
                "industry": company_info.get("industry")
            }
            try:
                company = database.create_company(db, company_data)
            except Exception as e:
                logging.error(f"Error creating company {ticker} in database: {e}")
                db.rollback()
                return False
        else:
            logging.error(f"Could not retrieve company info for {ticker}")
            return False

    if company:
        most_recent_data = db.query(func.max(FinancialData.date)).filter(FinancialData.company_id == company.company_id).scalar()
        ohlcv_data_to_store = []
        if not most_recent_data:
            # No existing data, fetch the full period
            ohlcv_data_list = fetch_financial_data(ticker, period= "5y", db=db, company_id=company.company_id)
            if ohlcv_data_list:
                store_fetched_financial_data(db, company.company_id, ohlcv_data_list)
            else:
                logging.warning(f"Could not fetch initial historical data for {ticker}.")
                return False # Or handle the case where no initial data is fetched
        else:
            # Fetch data from the day after the most recent record up to today
            start_date = most_recent_data + timedelta(days=1)
            end_date = datetime.now().date()
            if start_date <= end_date:
                logging.info(f"Fetching missing historical data for {ticker} between {start_date} and {end_date}.")
                fetched_ohlcv_data = fetch_financial_data(ticker, start=start_date, end=end_date, db=db, company_id=company.company_id)
                if not fetched_ohlcv_data:
                    logging.warning(f"Could not fetch missing historical data for {ticker} between {start_date} and {end_date}.")
                    pass
                else:
                    pass
            else:
                logging.info(f"Financial data for {ticker} is up to date.")

        fundamental_data_map = fetch_historical_fundamentals(ticker, years=5)
        logging.debug(f"DEBUG: Fetched fundamental data from yfinance for {ticker}: {fundamental_data_map}")
        logging.info(f"DEBUG (Check Fundamentals): Length of fundamental_data_map for {ticker}: {len(fundamental_data_map)}") # ADD THIS LINE

        if fundamental_data_map:
            logging.info(f"DEBUG (Fundamental Reporting Dates for {ticker}): {list(fundamental_data_map.keys())}") # ADD THIS LINE

        if company and fundamental_data_map:
            updated_fundamentals_count = 0
            for fund_date, fund_values in fundamental_data_map.items():
                logging.debug(f"DEBUG: Processing fundamental data for year: {fund_date.year}, fund_date: {fund_date}, values: {fund_values}")
                logging.debug(f"DEBUG: Fundamental data retrieved for {fund_date}: EPS={fund_values.get('eps')}, Revenue={fund_values.get('revenue')}, DebtToEquity={fund_values.get('debt_to_equity')}, CashFlow={fund_values.get('cash_flow')}, ROI={fund_values.get('roi')}")
                db_records = db.query(FinancialData).filter(
                    FinancialData.company_id == company.company_id,
                    FinancialData.date == fund_date 
                ).all()
                logging.debug(f"DEBUG: Found {len(db_records)} database records for company {company.company_id} and year {fund_date.year}.")

                if not db_records:
                    logging.warning(f"No OHLCV records found for company {company.company_id} in the year {fund_date.year} to update with fundamental data.")
                    continue # Move to the next fundamental data point

                for record in db_records:
                    logging.debug(f"DEBUG: Attempting to update record with date: {record.date} (database) against fundamental year: {fund_date.year} (yfinance)")
                    logging.debug(f"DEBUG: Current database record for date {record.date}: EPS={record.eps}, Revenue={record.revenue}, DebtToEquity={record.debt_to_equity}, CashFlow={record.cash_flow}, PE Ratio={record.pe_ratio}, ROI={record.roi}")
                    updated = False
                    if record.eps is None and fund_values.get('eps') is not None:
                        logging.debug(f"DEBUG: Updating NULL EPS for {record.date} with yfinance value: {fund_values.get('eps')}")
                        record.eps = fund_values['eps']
                        updated = True
                    elif fund_values.get('eps') is not None and record.eps != fund_values.get('eps'):
                        logging.debug(f"DEBUG: EPS in yfinance: {fund_values.get('eps')}, database value: {record.eps}")

                    if record.revenue is None and fund_values.get('revenue') is not None:
                        logging.debug(f"DEBUG: Updating NULL Revenue for {record.date} with yfinance value: {fund_values.get('revenue')}")
                        record.revenue = fund_values['revenue']
                        updated = True
                    elif fund_values.get('revenue') is not None:
                        logging.debug(f"DEBUG: Revenue in yfinance: {fund_values.get('revenue')}, database value: {record.revenue}")

                    if record.debt_to_equity is None and fund_values.get('debt_to_equity') is not None:
                        logging.debug(f"DEBUG: Updating NULL DebtToEquity for {record.date} with yfinance value: {fund_values.get('debt_to_equity')}")
                        record.debt_to_equity = fund_values['debt_to_equity']
                        updated = True
                    elif fund_values.get('debt_to_equity') is not None:
                        logging.debug(f"DEBUG: DebtToEquity in yfinance: {fund_values.get('debt_to_equity')}, database value: {record.debt_to_equity}")

                    if record.cash_flow is None and fund_values.get('cash_flow') is not None:
                        logging.debug(f"DEBUG: Updating NULL CashFlow for {record.date} with yfinance value: {fund_values.get('cash_flow')}")
                        record.cash_flow = fund_values['cash_flow']
                        updated = True
                    elif fund_values.get('cash_flow') is not None:
                        logging.debug(f"DEBUG: CashFlow in yfinance: {fund_values.get('cash_flow')}, database value: {record.cash_flow}")

                    if record.roi is None and fund_values.get('roi') is not None:
                        logging.debug(f"DEBUG: Updating NULL ROI for {record.date} with yfinance value: {fund_values.get('roi')}")
                        record.roi = fund_values['roi']
                        updated = True
                    elif fund_values.get('roi') is not None:
                        logging.debug(f"DEBUG: ROI in yfinance: {fund_values.get('roi')}, database value: {record.roi}")

                    # Calculate and update P/E ratio if EPS and close price are available
                    if record.pe_ratio is None and record.eps is not None and record.eps != 0 and record.close is not None:
                        pe_calculated = record.close / record.eps
                        logging.debug(f"DEBUG: Calculating PE Ratio for {record.date}: Close={record.close}, EPS={record.eps}, PE={pe_calculated}")
                        record.pe_ratio = pe_calculated
                        updated = True
                    elif record.pe_ratio is not None:
                        logging.debug(f"DEBUG: PE Ratio already present in database: {record.pe_ratio}")
                    elif record.eps is None or record.eps == 0 or record.close is None:
                        logging.debug(f"DEBUG: Cannot calculate PE Ratio for {record.date} due to missing close price or non-positive EPS (Close: {record.close}, EPS: {record.eps})")

                    if updated:
                        updated_fundamentals_count += 1
                        logging.info(f"DEBUG (Store Fundamentals): Updated fundamentals for {company.ticker_symbol} on {record.date}.")
                        logging.debug(f"DEBUG (Store Fundamentals - After Update): EPS={record.eps}, Revenue={record.revenue}, DebtToEquity={record.debt_to_equity}, CashFlow={record.cash_flow}, ROI={record.roi}")

            try:
                db.commit()
                if updated_fundamentals_count > 0:
                    logging.info(f"Updated {updated_fundamentals_count} fundamental data points for {ticker}.")
                else:
                    logging.info(f"No fundamental data updates needed for {ticker}.")
            except Exception as e:
                logging.error(f"Error committing updated fundamental data for {ticker}: {e}")
                db.rollback()
                return False
        return True
    return False

def needs_financial_data_update(db: Session, company_id: int, threshold_hours: int = 24) -> bool:
    """Checks if the financial data for a company needs updating."""
    most_recent_data = db.query(func.max(FinancialData.date)).filter(
        FinancialData.company_id == company_id).scalar()
    if not most_recent_data:
        return True  # No data exists, so needs update

    sgt = pytz.timezone('Asia/Singapore')
    now_sgt = datetime.now(sgt).date()
    data_date_sgt = most_recent_data
    logging.info(f'DEBUG:Most recent data:{most_recent_data}')
    logging.info(f'DEBUG: NOW_SGT:{now_sgt}')
    logging.info(f'DEBUG: DATA_DATE_SGT:{data_date_sgt}')
    # Check if the latest data is from a previous day in SGT
    return data_date_sgt < now_sgt

def fetch_company_news(ticker: str, company_name: str = "", count: int = 5) -> List[Dict[str, Any]]:
    """Fetches the latest news for a specific company using yfinance."""
    logging.info(f"Fetching company news for {ticker}...")
    try:
        ticker_data = yf.Ticker(ticker)
        news = ticker_data.news
        logging.info(f"Raw company news data for {ticker}: {news}")
        if news:
            # Limit the number of news items
            latest_news = news[:count]
            formatted_news = []
            for item in latest_news:
                logging.debug(f"DEBUG: Individual news item: {item}")
                logging.debug(f"DEBUG: Content of news item: {item.get('content')}")
                content = item.get('content', {})
                formatted_news.append({
                    "title": content.get('title'),
                    "description": content.get('summary'),
                    "url": content.get('canonicalUrl', {}).get('url') or content.get('clickThroughUrl', {}).get('url'),
                    "publishedAt": datetime.fromtimestamp(item.get('publishEpoch')).isoformat() if item.get(
                        'publishEpoch') else datetime.now().isoformat(),
                    "source": {"name": "Yahoo Finance"}
                })
            logging.info(
                f"Successfully fetched {len(formatted_news)} news articles for {ticker} from Yahoo Finance.")
            return formatted_news
        else:
            logging.info(f"No news found for {ticker} on Yahoo Finance.")
            return []
    except Exception as e:
        logging.error(f"Error fetching news for {ticker} from Yahoo Finance: {e}")
        return []

def fetch_industry_news(industry: str, count: int = 3) -> List[Dict[str, Any]]:
    """Fetches the latest news related to the industry using The Guardian API."""
    guardian_api_key = "ce66226f-693d-42a5-9023-3b003666df2a"  # Your API key
    guardian_endpoint = 'https://content.guardianapis.com/search'
    if not guardian_api_key:
        logging.warning("The Guardian API key is missing.")
        return []
    try:
        query = f'"{industry}"'  # Search for the industry
        params = {
            'q': query,
            'api-key': guardian_api_key,
            'format': 'json',
            'show-fields': 'headline,trailText,webUrl,webPublicationDate',
            'order-by': 'newest',
            'page-size': count
        }
        logging.debug(f"DEBUG: Fetching industry news for '{industry}' using The Guardian API with params: {params}")
        response = requests.get(guardian_endpoint, params=params)
        logging.debug(f"DEBUG: The Guardian API response status code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        logging.info(f"The Guardian API response for industry '{industry}': {data}")
        results = data.get('response', {}).get('results', [])
        logging.debug(f"DEBUG: Number of results from The Guardian API: {len(results)}")
        industry_news = []
        for article in results:
            logging.debug(f"DEBUG: Individual Guardian article: {article}")
            fields = article.get('fields', {})
            logging.debug(f"DEBUG: Fields for the article: {fields}")
            industry_news.append({
                "title": fields.get('headline'),
                "description": fields.get('trailText'),
                "url": article.get('webUrl'),
                "publishedAt": fields.get('webPublicationDate'),
                "source": {"name": "The Guardian"}
            })
        logging.info(f"Successfully fetched {len(industry_news)} industry news articles for '{industry}' from The Guardian.")
        return industry_news
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching industry news from The Guardian for '{industry}': {e}")
        return []
    except KeyError as e:
        logging.error(f"Error parsing The Guardian API response for '{industry}': Missing key {e}")
        return []
    
def fetch_latest_news(ticker: str, industry: str, exchange: str, company_name: str = "") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Fetches the latest news for a company and its industry.
    Now using yfinance for company news. Industry news is still a placeholder.
    """
    logging.info(f"Fetching latest news for ticker: {ticker}, industry: {industry}")
    try:
        company_news = fetch_company_news(ticker, company_name, count=5)
    except Exception as e:
        logging.error(f"Error fetching company news (Yahoo Finance): {e}")
        company_news = []

    try:
        industry_news = fetch_industry_news(industry, count=3)
    except Exception as e:
        logging.error(f"Error fetching industry news (Placeholder): {e}")
        industry_news = []

    return company_news, industry_news

def store_news_articles(db: Session, company_id: int, news_articles: List[Dict[str, Any]], news_type: str = "company"):
    """
    Stores news articles in the database.
    """
    logging.info(f"Storing {len(news_articles)} {news_type} news articles for company ID: {company_id}") 
    news_items_to_add = []

    # Check for duplicates before adding
    existing_urls = {news.link for news in db.query(
        News.link).filter(News.company_id == company_id).all()}

    for article in news_articles:
        # Skip if URL already exists in the database
        if article['url'] in existing_urls:
            continue

        try:
            # Handle different types of publishedAt values safely
            if isinstance(article['publishedAt'], str):
                published_at_utc = datetime.fromisoformat(
                    article['publishedAt'].replace('Z', '+00:00'))
                published_at_sgt = published_at_utc.astimezone(
                    pytz.timezone('Asia/Singapore'))
            else:
                # If it's a MagicMock or other object during testing, use current time
                published_at_sgt = datetime.now(
                    pytz.timezone('Asia/Singapore'))

            # Add a prefix to title to identify news type
            title_prefix = f"[{news_type.upper()}] " if news_type == "industry" else ""

            news = News(
                company_id=company_id,
                title=f"{title_prefix}{article['title']}",
                link=article['url'],
                published_date=published_at_sgt,
                summary=article['description'] or "No description available."
            )
            news_items_to_add.append(news)
        except Exception as e:
            logging.error(f"Error processing article {article.get('title', 'Unknown')}: {e}")

    if news_items_to_add:
        logging.info(f"Attempting to add {len(news_items_to_add)} new news articles to the database.")
        try:
            db.add_all(news_items_to_add)
            db.commit()
            logging.info(f"Successfully added {len(news_items_to_add)} new news articles.")
        except Exception as db_error:
            logging.error(f"Database error when adding articles: {db_error}")
            db.rollback()
            raise  # Re-raise the exception so the test can catch it
    else:
        logging.info(f"No new {news_type} news articles to add")


def get_stored_news(db: Session, company_id: int, limit: int = 20) -> List[News]:
    """Retrieves stored news articles for a given company."""
    logging.info(f"Getting stored news for company ID: {company_id}, limit: {limit}")
    stored_news = db.query(News).filter(News.company_id == company_id).order_by(
        News.published_date.desc()).limit(limit).all()
    logging.info(f"Retrieved {len(stored_news)} stored news articles for company ID: {company_id}") # DEBUG
    return stored_news

def predict_financial_trends(financial_data: Optional[List[Dict[str, Any]]]) -> Dict[str, Optional[str]]:
    """Analyzes historical financial data and predicts future trends (basic implementation)."""
    trends: Dict[str, Optional[str]] = {}
    if not financial_data or len(financial_data) < 2:
        return {"revenue_growth": "Insufficient data", "profit_margin": "Insufficient data"}

    # Basic trend analysis (simplistic and for illustrative purposes)
    # More sophisticated methods would involve time series analysis.

    # Revenue trend (using a placeholder 'revenue' key - adjust if your data has it)
    revenue_present = all(item.get('revenue') is not None for item in financial_data)
    if revenue_present:
        latest_revenue = financial_data[-1].get('revenue')
        previous_revenue = financial_data[-2].get('revenue')
        if latest_revenue is not None and previous_revenue is not None and previous_revenue != 0:
            growth_rate = (latest_revenue - previous_revenue) / previous_revenue
            if growth_rate > 0.05:
                trends["revenue_growth"] = "Positive"
            elif growth_rate < -0.05:
                trends["revenue_growth"] = "Negative"
            else:
                trends["revenue_growth"] = "Neutral"
        else:
            trends["revenue_growth"] = "Insufficient data for trend"
    else:
        trends["revenue_growth"] = "Revenue data not available"

    # Profit margin trend (using a placeholder - you'll need actual profit data)
    trends["profit_margin"] = "Analysis not implemented (requires profit data)"

    return trends


def get_similar_companies(industry: Optional[str]) -> List[str]:
    """Retrieves a list of similar companies based on the industry."""
    if not industry:
        return ["No industry specified"]

    # This is a very basic placeholder. In a real application,
    # you would query a database or use an external API to find
    # companies in the same or related industries.

    similar_companies_data = {
        "Technology": ["AAPL", "MSFT", "GOOGL", "AMZN"],
        "Healthcare": ["JNJ", "PFE", "MRK"],
        "Finance": ["JPM", "BAC", "WFC"],
        # Add more industries and their common tickers
    }

    return similar_companies_data.get(industry, ["No similar companies found for this industry"])


if __name__ == '__main__':
    # Example usage (for testing purposes)
    logging.basicConfig(level=logging.DEBUG)
    ticker = "AAPL"
    company_name = "Apple Inc."

    # Test fetching company and industry news
    company_news, industry_news = fetch_latest_news(
        ticker, "Technology", "NASDAQ", company_name)
    logging.info(
        f"Latest company news for {ticker}: {len(company_news)} articles")
    logging.info(
        f"Latest industry news for Technology: {len(industry_news)} articles")

    # Get similar companies
    similar = get_similar_companies("Technology")
    logging.info(f"Similar companies in Technology: {similar}")
