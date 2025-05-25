from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from .data_fetcher import fetch_stock_data
from dash.exceptions import PreventUpdate # Using this for better control

def register_callbacks(app):
    @app.callback(
        [Output('stock-price-chart', 'figure'),
         Output('volume-chart', 'figure'),
         Output('daily-returns-chart', 'figure'),
         Output('volatility-chart', 'figure'),
         Output('error-message-area', 'children'), # New Output for error message
         Output('error-message-area', 'className')], # New Output for error message styling
        [Input('stock-symbol-input', 'value'),
         Input('date-range-picker', 'start_date'),
         Input('date-range-picker', 'end_date'),
         Input('ma-toggles', 'value'),
         Input('return-chart-toggle', 'value'),
         Input('volatility-chart-toggle', 'value')]
    )
    def update_charts(symbol, start_date, end_date, ma_selected_values, return_toggle_value, volatility_toggle_value):
        error_message = ""
        error_className = ""

        if not all([symbol, start_date, end_date]):
            # This case might be better handled by preventing update or setting a specific message
            # For now, let's assume PreventUpdate or make it a specific user instruction error
            error_message = "Please ensure a stock symbol, start date, and end date are selected."
            error_className = "error"
            # Return empty figures and the error message
            empty_fig = go.Figure(layout={'xaxis': {'visible': False}, 'yaxis': {'visible': False}})
            return empty_fig, empty_fig, empty_fig, empty_fig, error_message, error_className


        if ma_selected_values is None: ma_selected_values = []
        if return_toggle_value is None: return_toggle_value = []
        if volatility_toggle_value is None: volatility_toggle_value = []

        df = fetch_stock_data(symbol, start_date, end_date)

        # Default empty/placeholder figures
        empty_layout = {'xaxis': {'visible': False}, 'yaxis': {'visible': False}, 
                        'annotations': [{'text': 'No data found or chart hidden', 'xref': 'paper', 'yref': 'paper', 
                                         'showarrow': False, 'font': {'size': 16}}]}
        
        price_fig = go.Figure(layout=empty_layout).update_layout(title_text=f"Stock Price (No Data)")
        volume_fig = go.Figure(layout=empty_layout).update_layout(title_text=f"Trading Volume (No Data)")
        daily_returns_fig = go.Figure(layout=empty_layout).update_layout(title_text="Daily Returns (Toggle On or No Data)")
        volatility_fig = go.Figure(layout=empty_layout).update_layout(title_text="Volatility (Toggle On or No Data)")

        if df.empty:
            error_message = f"Error: No data found for symbol '{symbol}' from {start_date} to {end_date}. Please check the symbol or try a different range."
            error_className = "error"
            # Update titles of placeholder figs to reflect the error for this specific case
            price_fig.update_layout(title_text=f"Stock Price for {symbol} (No Data)")
            volume_fig.update_layout(title_text=f"Trading Volume for {symbol} (No Data)")
            return price_fig, volume_fig, daily_returns_fig, volatility_fig, error_message, error_className
        # else: # Optional: success message
            # error_message = f"Data for {symbol} loaded successfully."
            # error_className = "success"

        # Stock Price Chart (Line Chart) - Re-initialize if data is present
        price_fig = go.Figure() 
        price_fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close', line=dict(color='blue')))

        # Calculate and add Moving Averages
        if 'Close' in df.columns:
            if 'MA50' in ma_selected_values:
                df['MA50'] = df['Close'].rolling(window=50, min_periods=1).mean() # min_periods=1 to show partial MA
                if not df['MA50'].isnull().all():
                    price_fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], mode='lines', name='50-Day MA', line=dict(color='orange')))
            
            if 'MA200' in ma_selected_values:
                df['MA200'] = df['Close'].rolling(window=200, min_periods=1).mean() # min_periods=1 to show partial MA
                if not df['MA200'].isnull().all():
                    price_fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], mode='lines', name='200-Day MA', line=dict(color='purple')))

        price_fig.update_layout(
            title_text=f"{symbol} Stock Price with Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            showlegend=True,
            hovermode='x unified' # Example hovermode
        )

        # Volume Chart (Bar Chart) - Re-initialize if data is present
        volume_fig = go.Figure()
        volume_fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'))
        volume_fig.update_layout(
            title_text=f"{symbol} Trading Volume",
            xaxis_title="Date",
            yaxis_title="Volume",
            showlegend=True,
            hovermode='x unified' # Example hovermode
        )

        # Daily Returns Chart
        if 'SHOW_RETURNS' in return_toggle_value and 'Close' in df.columns and not df['Close'].empty:
            df['Daily Return'] = df['Close'].pct_change() * 100
            daily_returns_fig = go.Figure() # Re-initialize
            daily_returns_fig.add_trace(go.Bar(x=df.index, y=df['Daily Return'], name='Daily Return'))
            daily_returns_fig.update_layout(
                title_text=f"{symbol} Daily Return Rates (%)",
                xaxis_title="Date",
                yaxis_title="Return (%)",
                showlegend=True,
                hovermode='x unified' # Example hovermode
            )

        # Volatility Chart
        if 'SHOW_VOLATILITY' in volatility_toggle_value and 'Close' in df.columns and not df['Close'].empty:
            df['Volatility'] = df['Close'].rolling(window=30, min_periods=1).std() # 30-day rolling std, min_periods=1
            volatility_fig = go.Figure() # Re-initialize
            volatility_fig.add_trace(go.Scatter(x=df.index, y=df['Volatility'], mode='lines', name='30-Day Volatility'))
            volatility_fig.update_layout(
                title_text=f"{symbol} 30-Day Price Volatility",
                xaxis_title="Date",
                yaxis_title="Standard Deviation",
                showlegend=True,
                hovermode='closest' # Example hovermode
            )
        # Else, it remains the placeholder figure defined earlier

        return price_fig, volume_fig, daily_returns_fig, volatility_fig, error_message, error_className
