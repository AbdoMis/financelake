import unittest
from unittest.mock import patch, Mock
import pandas as pd
from pandas.testing import assert_frame_equal
import json # For JSONDecodeError if needed directly
from datetime import datetime

# Adjust the path if your project structure is different.
# This assumes 'dashboard' directory is at the same level as 'tests'
# and that the parent directory of 'dashboard' and 'tests' is in PYTHONPATH.
# If running from the root of the project, this should work.
from dashboard.data_fetcher import fetch_stock_data
from requests.exceptions import RequestException, JSONDecodeError as RequestsJSONDecodeError # Used by data_fetcher for response.json()

# If data_fetcher explicitly uses json.JSONDecodeError for its own parsing before requests.json(),
# we might need to mock that too, but the current data_fetcher.py uses response.json()
# which can raise requests.exceptions.JSONDecodeError or json.JSONDecodeError depending on requests version
# and underlying json library. For safety, we can mock both or rely on requests.exceptions.JSONDecodeError.

import requests # Import requests for its exception types

class TestFetchStockData(unittest.TestCase):

    def setUp(self):
        self.symbol = "TEST"
        self.start_date = "2024-01-01"
        self.end_date = "2024-01-02"
        self.api_base_url = "http://mockapi.com"
        self.expected_url = f"{self.api_base_url}/data/stock/{self.symbol}?from={self.start_date}&to={self.end_date}"

    @patch('dashboard.data_fetcher.requests.get')
    def test_fetch_stock_data_success(self, mock_get):
        sample_api_response = {
            "symbol": self.symbol,
            "data": [
                {"date": "2024-01-01", "open": 150.00, "close": 155.00, "high": 157.00, "low": 149.00, "volume": 1000000},
                {"date": "2024-01-02", "open": 156.00, "close": 158.00, "high": 159.00, "low": 154.00, "volume": 1100000}
            ]
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_get.return_value = mock_response

        result_df = fetch_stock_data(self.symbol, self.start_date, self.end_date, api_base_url=self.api_base_url)

        mock_get.assert_called_once_with(self.expected_url, timeout=10)

        # Expected DataFrame should match the column order produced by fetch_stock_data's processing
        # The processing order is: Date, Open, High, Low, Close, Volume (after rename)
        # and Date becomes index.
        expected_data_list = [
            # Order of keys in dicts here doesn't strictly matter for pd.DataFrame construction,
            # but the final column order in expected_df must be correct.
            {'Date': datetime(2024, 1, 1), 'Open': 150.00, 'High': 157.00, 'Low': 149.00, 'Close': 155.00, 'Volume': 1000000},
            {'Date': datetime(2024, 1, 2), 'Open': 156.00, 'High': 159.00, 'Low': 154.00, 'Close': 158.00, 'Volume': 1100000}
        ]
        expected_df = pd.DataFrame(expected_data_list)
        expected_df['Date'] = pd.to_datetime(expected_df['Date'])
        expected_df.set_index('Date', inplace=True)
        
        # Explicitly set column order for expected_df to match what fetch_stock_data produces
        # before type conversion, if necessary.
        # The column_mapping in fetch_stock_data is:
        # {'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}
        # The required_cols check is: ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        # Date is then set as index. So the final columns should be in the order of the original data keys
        # after mapping, minus 'Date'.
        # The sample_api_response has keys: "date", "open", "close", "high", "low", "volume"
        # After mapping: Date, Open, Close, High, Low, Volume
        # Then Date is set to index. So remaining columns: Open, Close, High, Low, Volume
        # This was the source of the error. The expected_df columns must match this order.
        
        expected_df = expected_df[['Open', 'Close', 'High', 'Low', 'Volume']]


        # Ensure dtypes match what fetch_stock_data produces
        expected_df['Open'] = pd.to_numeric(expected_df['Open'])
        expected_df['High'] = pd.to_numeric(expected_df['High'])
        expected_df['Low'] = pd.to_numeric(expected_df['Low'])
        expected_df['Close'] = pd.to_numeric(expected_df['Close'])
        expected_df['Volume'] = pd.to_numeric(expected_df['Volume'], downcast='integer')

        assert_frame_equal(result_df, expected_df, check_dtype=True)

    @patch('dashboard.data_fetcher.requests.get')
    def test_fetch_stock_data_api_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        # Configure raise_for_status to simulate HTTPError
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response, request=Mock()) # Add dummy request
        mock_get.return_value = mock_response

        result_df = fetch_stock_data(self.symbol, self.start_date, self.end_date, api_base_url=self.api_base_url)
        
        mock_get.assert_called_once_with(self.expected_url, timeout=10)
        self.assertTrue(result_df.empty)

    @patch('dashboard.data_fetcher.requests.get')
    def test_fetch_stock_data_request_exception(self, mock_get):
        mock_get.side_effect = RequestException("Test network error")

        result_df = fetch_stock_data(self.symbol, self.start_date, self.end_date, api_base_url=self.api_base_url)
        
        mock_get.assert_called_once_with(self.expected_url, timeout=10)
        self.assertTrue(result_df.empty)

    @patch('dashboard.data_fetcher.requests.get')
    def test_fetch_stock_data_json_decode_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        # Correctly instantiate RequestsJSONDecodeError
        # The constructor for json.JSONDecodeError (which requests.exceptions.JSONDecodeError inherits) is (msg, doc, pos)
        mock_response.json.side_effect = RequestsJSONDecodeError("Test JSON decode error", "dummy_doc", 0)
        mock_get.return_value = mock_response

        result_df = fetch_stock_data(self.symbol, self.start_date, self.end_date, api_base_url=self.api_base_url)
        
        mock_get.assert_called_once_with(self.expected_url, timeout=10)
        self.assertTrue(result_df.empty)

    @patch('dashboard.data_fetcher.requests.get')
    def test_fetch_stock_data_invalid_format_missing_data_key(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"symbol": self.symbol, "records": []} # Missing 'data' key
        mock_get.return_value = mock_response

        result_df = fetch_stock_data(self.symbol, self.start_date, self.end_date, api_base_url=self.api_base_url)
        
        mock_get.assert_called_once_with(self.expected_url, timeout=10)
        self.assertTrue(result_df.empty)

    @patch('dashboard.data_fetcher.requests.get')
    def test_fetch_stock_data_invalid_format_data_not_list(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"symbol": self.symbol, "data": "not a list"} # 'data' is not a list
        mock_get.return_value = mock_response

        result_df = fetch_stock_data(self.symbol, self.start_date, self.end_date, api_base_url=self.api_base_url)
        
        mock_get.assert_called_once_with(self.expected_url, timeout=10)
        self.assertTrue(result_df.empty)


    @patch('dashboard.data_fetcher.requests.get')
    def test_fetch_stock_data_empty_data_list(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"symbol": self.symbol, "data": []}
        mock_get.return_value = mock_response

        result_df = fetch_stock_data(self.symbol, self.start_date, self.end_date, api_base_url=self.api_base_url)
        
        mock_get.assert_called_once_with(self.expected_url, timeout=10)
        self.assertTrue(result_df.empty)

    @patch('dashboard.data_fetcher.requests.get')
    def test_fetch_stock_data_missing_columns_in_df(self, mock_get):
        # API returns data points that are missing 'open' for example
        sample_api_response = {
            "symbol": self.symbol,
            "data": [
                {"date": "2024-01-01", "close": 155.00, "high": 157.00, "low": 149.00, "volume": 1000000}
            ]
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_get.return_value = mock_response

        result_df = fetch_stock_data(self.symbol, self.start_date, self.end_date, api_base_url=self.api_base_url)
        
        mock_get.assert_called_once_with(self.expected_url, timeout=10)
        self.assertTrue(result_df.empty, "DataFrame should be empty if required columns are missing after mapping")

    @patch('dashboard.data_fetcher.requests.get')
    def test_fetch_stock_data_non_numeric_ohlc(self, mock_get):
        # API returns data with non-numeric 'open'
        sample_api_response = {
            "symbol": self.symbol,
            "data": [
                {"date": "2024-01-01", "open": "not-a-number", "close": 155.00, "high": 157.00, "low": 149.00, "volume": 1000000},
                {"date": "2024-01-02", "open": 156.00, "close": 158.00, "high": 159.00, "low": 154.00, "volume": 1100000}
            ]
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_get.return_value = mock_response

        result_df = fetch_stock_data(self.symbol, self.start_date, self.end_date, api_base_url=self.api_base_url)
        
        mock_get.assert_called_once_with(self.expected_url, timeout=10)
        
        # Expecting a DataFrame where 'Open' for the first row is NaN due to coercion
        # The current data_fetcher.py doesn't drop NaNs, so the frame won't be empty.
        # It prints a warning. Let's check if the NaN is there.
        self.assertFalse(result_df.empty)
        self.assertTrue(pd.isna(result_df.loc[pd.to_datetime("2024-01-01"), 'Open']))
        self.assertEqual(result_df.loc[pd.to_datetime("2024-01-02"), 'Open'], 156.00)


if __name__ == '__main__':
    unittest.main()
