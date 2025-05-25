import dash
from dash import dcc
from dash import html
from datetime import datetime, timedelta
from .callbacks import register_callbacks # Import the registration function

# Initialize the Dash App
app = dash.Dash(__name__)
server = app.server # Expose server for potential WSGI use

# Default dates
today = datetime.now().date()
three_months_ago = today - timedelta(days=90)

# App Layout
app.layout = html.Div(className='container', children=[ # Added className='container' to the main Div
    html.H1(
        children="Stock Visualization Dashboard",
        style={'textAlign': 'center', 'marginBottom': '20px'}
    ),

    # Error Message Area
    html.Div(id='error-message-area', children="", style={'textAlign': 'center'}), # Initially empty, styled via CSS

    # Input Controls Section
    html.Div(
        children=[
            # Stock Symbol Input
            html.Div(children=[
                html.Label("Stock Symbol:"),
                dcc.Input(
                    id='stock-symbol-input',
                    type='text',
                    value='AAPL',  # Default value
                    style={'marginLeft': '10px', 'marginRight': '20px'}
                )
            ], style={'display': 'inline-block'}),

            # Date Range Picker
            html.Div(children=[
                html.Label("Select Date Range:"),
                dcc.DatePickerRange(
                    id='date-range-picker',
                    min_date_allowed=datetime(2010, 1, 1).date(),
                    max_date_allowed=today,
                    start_date=three_months_ago,
                    end_date=today,
                    display_format='YYYY-MM-DD',
                    style={'marginLeft': '10px'}
                )
            ], style={'display': 'inline-block'})
        ],
        style={'textAlign': 'center', 'marginBottom': '30px', 'padding': '20px', 'border': '1px solid #eee'}
    ),

    # Chart Placeholders Section
    html.Div(
        id='charts-container',
        children=[
            html.Div(children=[
                html.Label("Moving Averages:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Checklist(
                    id='ma-toggles',
                    options=[
                        {'label': '50-Day MA', 'value': 'MA50'},
                        {'label': '200-Day MA', 'value': 'MA200'}
                    ],
                    value=['MA50', 'MA200'], # Default to selected
                    inline=True, 
                    style={'display': 'inline-block', 'marginRight': '20px'} # Added marginRight
                ),
                html.Label("Daily Returns:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Checklist(
                    id='return-chart-toggle',
                    options=[{'label': 'Show Daily Returns', 'value': 'SHOW_RETURNS'}],
                    value=[], # Hidden by default
                    inline=True,
                    style={'display': 'inline-block', 'marginRight': '20px'} # Added marginRight
                ),
                html.Label("Volatility:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Checklist(
                    id='volatility-chart-toggle',
                    options=[{'label': 'Show Volatility (30-day)', 'value': 'SHOW_VOLATILITY'}],
                    value=[], # Hidden by default
                    inline=True,
                    style={'display': 'inline-block'}
                )
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),
            dcc.Graph(id='stock-price-chart'),
            dcc.Graph(id='volume-chart'),
            dcc.Graph(id='daily-returns-chart'),
            dcc.Graph(id='volatility-chart')
        ],
        style={'padding': '20px'}
    )
]) # Removed the direct style from the main Div as it's now handled by .container

register_callbacks(app) # Register the callbacks

# Run the App
if __name__ == '__main__':
    app.run_server(debug=True)
