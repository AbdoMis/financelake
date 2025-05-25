# Stock Visualization Dashboard Documentation

## Overview

The Stock Visualization Dashboard is an interactive web application designed to display historical stock price data and key financial indicators. Users can input a stock symbol and select a date range to visualize:

*   Stock price trends (Open, High, Low, Close - OHLC).
*   Trading volume.
*   Key technical indicators such as 50-day and 200-day Moving Averages (MAs).
*   Daily return rates.
*   30-day rolling price volatility.

The dashboard provides an intuitive interface for financial data analysis and exploration.

## Features

*   **Stock Symbol Input:** Allows users to specify the stock ticker symbol (e.g., AAPL, MSFT).
*   **Date Range Selection:** Enables users to pick a start and end date for the historical data.
*   **Stock Price History Chart:** Displays the closing price of the stock over the selected period as a line chart.
*   **Trading Volume Chart:** Shows the trading volume for the selected stock as a bar chart.
*   **Moving Averages (MAs):**
    *   Calculates and overlays 50-day and 200-day moving averages on the price chart.
    *   Toggles to show/hide each MA.
*   **Daily Return Rates Chart:**
    *   Calculates and displays daily percentage returns as a bar chart.
    *   Toggle to show/hide this chart.
*   **Volatility Chart:**
    *   Calculates and displays the 30-day rolling standard deviation of the stock price as a line chart.
    *   Toggle to show/hide this chart.
*   **Interactive Charts:**
    *   Provides hover functionality on charts to display specific data point details.
    *   `hovermode='x unified'` for most charts for a comprehensive view at a specific date.
    *   `hovermode='closest'` for volatility chart.
*   **Error Handling:** Displays user-friendly error messages for invalid stock symbols, unavailable data for the selected range, or API connectivity issues.
*   **Custom Styling:** Utilizes a CSS stylesheet for an improved visual experience.

## Data Source

The dashboard fetches historical stock data from a backend API.

*   **API Endpoint:** `/data/stock/{symbol}?from={start_date}&to={end_date}`
    *   `{symbol}`: The stock ticker symbol.
    *   `{start_date}`: The start date in YYYY-MM-DD format.
    *   `{end_date}`: The end date in YYYY-MM-DD format.

*   **Expected JSON Response Structure (Simplified):**
    The API is expected to return a JSON object containing the requested symbol and a list of data points. Each data point should include `date`, `open`, `high`, `low`, `close`, and `volume`.

    ```json
    {
        "symbol": "AAPL",
        "data": [
            {"date": "2023-01-01", "open": 170.00, "high": 172.50, "low": 169.00, "close": 172.00, "volume": 1000000},
            {"date": "2023-01-02", "open": 172.10, "high": 173.00, "low": 171.50, "close": 172.80, "volume": 1200000}
            // ... more data points
        ]
    }
    ```

## Project Structure

The project is organized as follows:

*   `dashboard/`
    *   `app.py`: The main Dash application file. It defines the UI layout and initializes the app.
    *   `callbacks.py`: Contains all the Dash callback functions that handle user interactions, trigger data fetching, and update the charts and error messages.
    *   `data_fetcher.py`: A module responsible for fetching data from the backend API. It handles API requests, data parsing, and basic processing into a Pandas DataFrame.
    *   `assets/`
        *   `style.css`: Contains custom CSS styles for the dashboard. Dash automatically loads files from this directory.
*   `tests/`
    *   `test_dashboard.py`: Includes unit tests for the `data_fetcher.py` module, focusing on API interaction logic and error handling.
*   `requirements.txt`: Lists all Python dependencies required for the project.
*   `documentation.md`: This file.

## Setup and Running the Dashboard

### Prerequisites

*   Python 3.x
*   pip (Python package installer)

### Installation

1.  **Clone the Repository (if applicable):**
    If you have obtained the code as a Git repository, clone it:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
    If you have the code as a folder, navigate into that folder.

2.  **Install Dependencies:**
    It's recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
    Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Start the Dashboard:**
    Navigate to the project's root directory (if not already there) and run:
    ```bash
    python dashboard/app.py
    ```

2.  **Access in Browser:**
    The dashboard will typically be available at: `http://127.0.0.1:8050/`
    Open this URL in your web browser.

### **Important Note on Backend API**

For the dashboard to function correctly and display stock data, the backend API that serves data at the `/data/stock/...` endpoint **must be running and accessible** at the configured URL (default is `http://localhost:8000`). The dashboard itself does not include this backend component.

## How to Use

1.  **Enter Stock Symbol:**
    *   In the "Stock Symbol:" input field, type the ticker symbol of the stock you want to analyze (e.g., `GOOGL`, `TSLA`).
2.  **Select Date Range:**
    *   Use the "Select Date Range:" date picker to choose a start and end date for the data.
3.  **Toggle Indicators:**
    *   **Moving Averages:** Use the checkboxes under "Moving Averages:" to show or hide the 50-day and 200-day moving average lines on the stock price chart.
    *   **Daily Returns:** Use the "Show Daily Returns" checkbox to display or hide the daily returns bar chart.
    *   **Volatility:** Use the "Show Volatility (30-day)" checkbox to display or hide the 30-day price volatility line chart.
4.  **View Charts:**
    *   The charts will update automatically based on your selections.
    *   Hover over data points on the charts to see specific values.
5.  **Error Messages:**
    *   If there's an issue (e.g., invalid symbol, no data, API down), an error message will appear below the main title.

## Future Enhancements (Optional)

*   **More Advanced Technical Indicators:** Incorporate additional indicators like RSI, MACD, Bollinger Bands.
*   **User Accounts/Preferences:** Allow users to save default settings or favorite stocks.
*   **Comparative Analysis:** Enable comparison of multiple stocks on the same charts.
*   **Real-time Data:** Integrate with a streaming data source for near real-time updates (would require significant backend changes).
*   **Enhanced API Error Handling:** Provide more granular feedback from the API if possible.

This documentation provides a comprehensive guide to understanding, setting up, and using the Stock Visualization Dashboard.
