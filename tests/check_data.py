import yfinance as yf
import pandas as pd

def check_yfinance_data(ticker, period="5y"):
    """
    Manually checks if yfinance can fetch historical data for a given ticker and period.

    Args:
        ticker (str): The stock ticker symbol (e.g., "GOOG", "AMZN").
        period (str): The time period for the historical data (e.g., "1mo", "1y", "5y", "max").
                      See yfinance documentation for valid periods.
    """
    try:
        data = yf.download(ticker, period=period)
        if data.empty:
            print(f"No historical OHLCV data found for {ticker} for the period '{period}'.")
        else:
            print(f"Successfully fetched historical OHLCV data for {ticker} for the period '{period}':")
            print(data.head())  # Display the first few rows of the data
            print(f"Data spans from {data.index.min()} to {data.index.max()}")
    except Exception as e:
        print(f"An error occurred while fetching data for {ticker}: {e}")

if __name__ == "__main__":
    tickers_to_check = ["GOOGL", "AMZN"]  # Use "GOOGL" for one class of Google
    period_to_check = "5y"

    for ticker in tickers_to_check:
        check_yfinance_data(ticker, period_to_check)

    # You can also check for a specific date range:
    def check_yfinance_data_range(ticker, start_date, end_date):
        """
        Manually checks if yfinance can fetch historical data for a given ticker and date range.

        Args:
            ticker (str): The stock ticker symbol.
            start_date (str): The start date in 'YYYY-MM-DD' format.
            end_date (str): The end date in 'YYYY-MM-DD' format.
        """
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            if data.empty:
                print(f"No historical OHLCV data found for {ticker} between {start_date} and {end_date}.")
            else:
                print(f"Successfully fetched historical OHLCV data for {ticker} between {start_date} and {end_date}:")
                print(data.head())
                print(f"Data spans from {data.index.min()} to {data.index.max()}")
        except Exception as e:
            print(f"An error occurred while fetching data for {ticker}: {e}")

    print("\nChecking specific date range...")
    check_yfinance_data_range("GOOGL", "2020-04-17", "2020-04-24") # Example date range
    check_yfinance_data_range("AMZN", "2020-04-17", "2020-04-24")