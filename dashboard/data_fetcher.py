import requests
import pandas as pd
from datetime import datetime, timedelta
import json # For JSONDecodeError

# API_BASE_URL = "http://localhost:8000"  # Configurable base URL

def fetch_stock_data(symbol: str, start_date: str, end_date: str, api_base_url: str = "http://localhost:8000") -> pd.DataFrame:
    """
    Fetches historical stock data (OHLCV) for a given symbol and date range from the backend API.

    Args:
        symbol (str): The stock symbol (e.g., "AAPL").
        start_date (str): The start date for data fetching (format "YYYY-MM-DD").
        end_date (str): The end date for data fetching (format "YYYY-MM-DD").

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the OHLCV data.
                      Returns an empty DataFrame if no data is found or an error occurs.
    """
    api_url = f"{api_base_url}/data/stock/{symbol}?from={start_date}&to={end_date}"
    print(f"Attempting to fetch data from API: {api_url}")

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
        
        # Try to parse JSON
        try:
            parsed_json_data = response.json()
        except json.JSONDecodeError as e: # More specific exception
            print(f"Error decoding JSON from API for {symbol}: {e}")
            return pd.DataFrame()
        except requests.exceptions.JSONDecodeError as e: # requests' own wrapper if preferred
             print(f"Error decoding JSON (requests) from API for {symbol}: {e}")
             return pd.DataFrame()


        # Validate parsed data structure
        if not isinstance(parsed_json_data, dict) or \
           'symbol' not in parsed_json_data or \
           'data' not in parsed_json_data or \
           not isinstance(parsed_json_data['data'], list):
            print(f"Invalid data format received from API for {symbol}.")
            return pd.DataFrame()
        
        if parsed_json_data['symbol'].upper() != symbol.upper():
            print(f"Warning: API returned data for symbol {parsed_json_data['symbol']} when {symbol} was requested.")
            # Depending on strictness, one might return pd.DataFrame() here

        if not parsed_json_data['data']: # Empty data list
            print(f"No data points returned in API response for {symbol} for the given date range.")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(parsed_json_data['data'])

        # Rename columns (API output keys to DataFrame column names)
        # Example: if API returns {'date': ..., 'open_price': ...}
        # This needs to match the *actual* keys in the API response.
        # Assuming API returns: date, open, high, low, close, volume
        column_mapping = {
            'date': 'Date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }
        df.rename(columns=column_mapping, inplace=True)

        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            print(f"Missing one or more required columns {required_cols} after renaming. Available: {df.columns}")
            return pd.DataFrame()

        # Convert 'Date' column to datetime and set as index
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        # Ensure numeric columns are of appropriate types
        numeric_cols = ['Open', 'High', 'Low', 'Close']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce') # errors='coerce' will turn non-numeric to NaT/NaN
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce', downcast='integer') # Volume often integer

        if df.isnull().values.any(): # Check for NaNs introduced by coerce
            print(f"Warning: Non-numeric data found and replaced with NaN in one or more OHLCV columns for {symbol}.")
            # df.dropna(inplace=True) # Optionally drop rows with NaN if that's desired behavior

        return df

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error fetching data from API for {symbol}: {e}. Status: {e.response.status_code if e.response else 'N/A'}")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e: # Catches network issues, timeouts, etc.
        print(f"Error fetching data from API for {symbol}: {e}")
        return pd.DataFrame()
    except Exception as e: # Catch-all for other unexpected errors during processing
        print(f"An unexpected error occurred while processing data for {symbol}: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    print("Testing data_fetcher.py with API integration...")
    # Example usage: Fetch data for AAPL for the last month
    symbol_to_fetch = "MSFT" # Changed to avoid potential conflicts with previous yfinance test
    # Using a date range less likely to have very recent, incomplete data
    # and also more likely to exist if the API is pre-populated
    start_date_str = "2023-01-01" 
    end_date_str = "2023-01-31"

    print(f"Attempting to fetch data for {symbol_to_fetch} from {start_date_str} to {end_date_str} using API...")
    # Note: This will try to connect to http://localhost:8000
    # It's expected to fail if the API server isn't running, which is fine for this test.
    stock_df = fetch_stock_data(symbol_to_fetch, start_date_str, end_date_str)

    if not stock_df.empty:
        print(f"\nSuccessfully retrieved and processed data for {symbol_to_fetch} from API:")
        print("Head:")
        print(stock_df.head())
        print("\nTail:")
        print(stock_df.tail())
        print("\nInfo:")
        stock_df.info()
    else:
        print(f"Could not retrieve or process data for {symbol_to_fetch} from API. This is expected if API is not running or symbol/date has no data.")

    # Test with a non-existent symbol (expecting API to handle or return empty)
    symbol_error_test = "NONEXISTENTAPISYMBOL"
    print(f"\nAttempting to fetch data for non-existent symbol {symbol_error_test} (expecting graceful failure or empty)...")
    error_df = fetch_stock_data(symbol_error_test, start_date_str, end_date_str)
    if error_df.empty:
        print(f"As expected, received an empty DataFrame for {symbol_error_test}.")
    else:
        print(f"Unexpectedly received data for {symbol_error_test}:")
        print(error_df.head())
