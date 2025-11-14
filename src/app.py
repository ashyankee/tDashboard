import sys
from pickle import FALSE

if sys.version_info >= (3, 12):
    import pkgutil
    import importlib.util

    pkgutil.find_loader = lambda name: importlib.util.find_spec(name)

import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime
import sys
from config import FMP_API_KEY
import re

# Add src to path if needed
sys.path.insert(0, 'src')

from database import TradingDatabase
from components import render_hourly_chart, render_calendar, render_settings
from components.add_trade_form import render_add_trade_form

# Import config for API
try:
    from config import FMP_API_KEY
except ImportError:
    FMP_API_KEY = None
    print("Warning: config.py not found or FMP_API_KEY not set")

# Initialize the database
db = TradingDatabase()

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Trading Dashboard"

# Add custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            body {
                margin: 0;
                font-family: 'Inter', sans-serif;
            }
            input, textarea, select {
                font-family: 'Inter', sans-serif !important;
            }
            .Select-value-label {
                font-family: 'Inter', sans-serif !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# Define the layout
app.layout = html.Div([
    html.Div([
        html.H1("Road to $100K", style={'color': '#1f2937'}),
        html.P("Comprehensive view of all trades", style={'color': '#6b7280'}),
    ], style={'padding': '20px', 'backgroundColor': 'white', 'marginBottom': '20px', 'borderRadius': '8px',
              'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}),

    dcc.Tabs(id='tabs', value='dashboard', children=[
        dcc.Tab(label='Dashboard', value='dashboard'),
        dcc.Tab(label='Add Trade', value='add_trade'),
        dcc.Tab(label='Capital', value='capital'),
        dcc.Tab(label='Tax Calculator', value='taxes'),
        dcc.Tab(label='Maintenance', value='maintenance'),
        dcc.Tab(label='Settings', value='settings'),
    ]),

    html.Div(id='tab-content', style={'marginTop': '20px', 'border-radius': '25px'}),

    # Hidden div for triggering updates
    dcc.Interval(id='interval-component', interval=5000, n_intervals=0),

], style={'backgroundColor': '#f9fafb', 'minHeight': '100vh', 'padding': '20px'})


# Callback for tab content
@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value')
)
def render_tab_content(tab):
    if tab == 'dashboard':
        return render_dashboard()
    elif tab == 'add_trade':
        return render_add_trade()
    elif tab == 'capital':
        return render_capital()
    elif tab == 'taxes':
        return render_taxes()
    elif tab == 'maintenance':
        return render_maintenance()
    elif tab == 'settings':
        return render_settings(db)


def render_dashboard():
    stats = db.get_stats()
    streak_data = db.get_streak()

    if not stats:
        return html.Div([
            html.Div([
                html.H3("No trades yet", style={'textAlign': 'center', 'color': '#6b7280'}),
                html.P("Add your first trade to see analytics", style={'textAlign': 'center', 'color': '#9ca3af'}),
            ], style={'padding': '60px', 'backgroundColor': 'white', 'borderRadius': '8px', 'marginTop': '20px'})
        ])

    df = db.get_all_trades()

    # Capital card
    capital = db.get_current_capital()

    # Streak card
    # Streak card (consolidated)
    def get_streak_color(streak):
        if streak == 0:
            return '#60a5fa'  # Blue
        elif streak <= 2:
            return '#34d399'  # Green
        elif streak <= 4:
            return '#fbbf24'  # Yellow
        elif streak <= 6:
            return '#fb923c'  # Orange
        else:
            return '#ef4444'  # Red hot

    zero_loss_color = get_streak_color(streak_data['zero_loss_current'])



    # Stats cards
    stats_cards = html.Div([

        html.Div([
            html.P("Current Capital", style={'fontSize': '14px', 'color': '#6b7280', 'marginBottom': '8px'}),
            html.H2(f"${capital['total']:.2f}",
                    style={'color': '#1f2937', 'margin': '0'}),
            html.Div([
                html.Span(f"Trading P/L: ${capital['trading_pl']:.2f}",
                          style={'fontSize': '12px', 'color': '#3b82f6' if capital['trading_pl'] >= 0 else '#ef4444'}),
            ], style={'marginTop': '10px'}),
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '8px',
                  'boxShadow': '0 1px 3px rgba(0,0,0,0.1)', 'width': '10vw', 'height': '9vh',
                  'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),



        html.Div([
            html.P("Total Profit", style={'fontSize': '14px', 'color': '#6b7280', 'marginBottom': '8px'}),
            html.H2(f"${stats['total_profit']:.2f}",
                    style={'color': '#10b981' if stats['total_profit'] >= 0 else '#ef4444', 'margin': '0'}),
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '8px',
                  'boxShadow': '0 1px 3px rgba(0,0,0,0.1)', 'width': '10vw', 'height': '9vh'
            , 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),

        html.Div([
            html.P("Accuracy", style={'fontSize': '14px', 'color': '#6b7280', 'marginBottom': '8px'}),
            html.H2(f"{stats['win_rate']:.1f}%", style={'color': '#3b82f6', 'margin': '0'}),
            html.P(f"{stats['wins']}W / {stats['losses']}L",
                   style={'fontSize': '12px', 'color': '#9ca3af', 'marginTop': '4px'}),
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '8px',
                  'boxShadow': '0 1px 3px rgba(0,0,0,0.1)', 'width': '10vw', 'height': '9vh',
                  'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),


        #Streak Card
        html.Div([
            html.P("Zero Loss Profit Streak",
                   style={'fontSize': '14px', 'color': '#6b7280', 'marginBottom': '3px', 'textAlign': 'center'}),
            html.Div([
                html.Span("🔥 " if streak_data['zero_loss_current'] > 0 else "❄️ ",
                          style={'fontSize': '18px', 'marginRight': '10px'}),
                html.Span(f"{streak_data['zero_loss_current']}",
                          style={'fontSize': '30px', 'color': zero_loss_color, 'font-weight': 'bold'}),
            ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'marginBottom': '8px'}),
            html.P(f"Net Positive Streak: {streak_data['net_positive_current']} Days",
                   style={'fontSize': '12px', 'color': '#6b7280', 'textAlign': 'center', 'margin': '0'}),
            html.P(f"Longest Zero Loss: {streak_data['zero_loss_best']} Days",
                   style={'fontSize': '12px', 'color': '#6b7280', 'textAlign': 'center', 'margin': '0'}),
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '8px',
                  'boxShadow': '0 1px 3px rgba(0,0,0,0.1)','width': '10vw', 'height': '9vh',
                  'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),

        html.Div([
            html.P("Avg Win / Loss", style={'fontSize': '14px', 'color': '#6b7280', 'marginBottom': '8px'}),
            html.H3(f"${stats['avg_win']:.2f}", style={'color': '#10b981', 'margin': '5px 0', 'fontSize': '20px'}),
            html.H3(f"${stats['avg_loss']:.2f}", style={'color': '#ef4444', 'margin': '5px 0', 'fontSize': '20px'}),
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '8px',
                  'boxShadow': '0 1px 3px rgba(0,0,0,0.1)', 'width': '10vw', 'height': '9vh',
                  'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),

        html.Div([
            html.P("Best / Worst", style={'fontSize': '14px', 'color': '#6b7280', 'marginBottom': '8px'}),
            html.H3(f"${stats['best_trade']:.2f}", style={'color': '#10b981', 'margin': '5px 0', 'fontSize': '20px'}),
            html.H3(f"${stats['worst_trade']:.2f}", style={'color': '#ef4444', 'margin': '5px 0', 'fontSize': '20px'}),
        ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '8px',
                  'boxShadow': '0 1px 3px rgba(0,0,0,0.1)', 'width': '10vw', 'height': '9vh',
                  'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),


    ], style={'padding': '20px', 'marginBottom': '20px', 'textAlign': 'center', 'backgroundColor': 'MediumAquamarine',
              'display': 'flex',  # Enable Flexbox
              'justifyContent': 'space-between',  # Distribute space evenly (optional, use if needed)
              'alignItems': 'flex-start'})

#Graphs
    calendar_component = render_calendar(db)
    hourly_chart = render_hourly_chart(db)


    # Win rate by day
    win_rate_by_day = df.groupby('day_of_week').agg({
        'is_win': 'mean',
        'id': 'count'
    }).reset_index()
    win_rate_by_day['win_rate'] = win_rate_by_day['is_win'] * 100
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    win_rate_by_day = win_rate_by_day[win_rate_by_day['day_of_week'].isin(day_order)]

    day_chart = dcc.Graph(
        figure=go.Figure(
            data=[go.Bar(x=win_rate_by_day['day_of_week'],
                         y=win_rate_by_day['win_rate'],
                         marker_color='#10b981')],
            layout=go.Layout(title='Win Rate by Day', xaxis_title='Day', yaxis_title='Win Rate (%)',
                             template='plotly_white')
        )
    )

    # Trade history table - FLASHY VERSION
    trade_table_content = []
    if len(df) > 0:
        # Table header
        header = html.Thead(
            html.Tr([
                html.Th("Date"),
                html.Th("Ticker"),
                html.Th("Entry"),
                html.Th("Exit"),
                html.Th("Hold"),
                html.Th("P/L ($)"),
                html.Th("P/L (%)"),
            ])
        )

        # Table body
        rows = []
        for _, trade in df.sort_values('date', ascending=False).iterrows():
            row_class = 'win-row' if trade['is_win'] == 1 else 'loss-row'

            row = html.Tr([
                html.Td(trade['date'], className='date-cell'),
                html.Td(trade['ticker'], className='ticker-cell'),
                html.Td(f"${trade['entry_price']:.2f}", className='price-cell'),
                html.Td(f"${trade['exit_price']:.2f}", className='price-cell'),
                html.Td(
                    html.Span(f"{int(trade['hold_duration'])}m", className='hold-badge')
                ),
                html.Td(
                    html.Span(
                        f"${trade['profit_loss']:.2f}",
                        className=f"profit-badge {'profit-positive' if trade['profit_loss'] > 0 else 'profit-negative'}"
                    )
                ),
                html.Td(
                    html.Span(
                        f"{trade['profit_loss_percent']:.2f}%",
                        className=f"percent-badge {'percent-positive' if trade['profit_loss_percent'] > 0 else 'percent-negative'}"
                    )
                ),
            ], className=row_class)

            rows.append(row)

        body = html.Tbody(rows)

        trade_table = html.Table([header, body], className='trades-table')
    else:
        trade_table = html.Div("No trades yet", className='empty-trades')

    trade_table_section = html.Div([
        html.H3("Recent Trades", style={'marginTop': '30px', 'marginBottom': '15px', 'color': '#1f2937'}),
        trade_table
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'marginTop': '20px'})

    return html.Div([
        stats_cards,
        html.Div([calendar_component],
                 style={'width': '49%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
        html.Div([hourly_chart], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        trade_table_section
    ])


def render_add_trade():
    from components.add_trade_form import render_add_trade_form
    return render_add_trade_form()


@app.callback(
    Output('save-trade-output', 'children'),
    Input('save-trade-btn', 'n_clicks'),
    State('trade-date', 'value'),
    State('trade-ticker', 'value'),
    State('trade-sector', 'value'),
    State('trade-news', 'value'),
    State('trade-entry-price', 'value'),
    State('trade-entry-time', 'value'),
    State('trade-exit-price', 'value'),
    State('trade-exit-time', 'value'),
    State('trade-shares', 'value'),
    State('trade-notes', 'value'),
    prevent_initial_call=True
)
def save_trade(n_clicks, date, ticker, sector, news, entry_price, entry_time, exit_price, exit_time, shares, notes):
    if not all([ticker, entry_price, entry_time, exit_price, exit_time, shares]):
        return "Please fill all required fields"

    trade_data = {
        'date': date,
        'ticker': ticker.upper(),
        'sector': sector,
        'news_type': news,
        'entry_price': entry_price,
        'entry_time': entry_time,
        'exit_price': exit_price,
        'exit_time': exit_time,
        'shares': shares,
        'notes': notes or ''
    }

    db.add_trade(trade_data)
    return f"✓ Trade saved successfully! ({ticker})"


def render_taxes():
    tax_data = db.calculate_taxes_simple()

    return html.Div([
        # Big tax owed number
        html.Div([
            html.P("Taxes Owed on Trading",
                   style={'fontSize': '18px', 'color': '#6b7280', 'marginBottom': '10px', 'textAlign': 'center'}),
            html.H1(f"${tax_data['total_tax_owed']:,.2f}",
                    style={'color': '#ef4444', 'margin': '0', 'fontSize': '64px',
                           'fontWeight': '700', 'textAlign': 'center'}),
            html.P(f"On ${tax_data['net_trading_income']:,.2f} net profit",
                   style={'fontSize': '16px', 'color': '#9ca3af', 'marginTop': '10px', 'textAlign': 'center'}),
        ], style={'backgroundColor': 'white', 'padding': '50px', 'borderRadius': '8px',
                  'marginBottom': '20px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),

        # Trading summary
        html.Div([
            html.H3("Trading Summary", style={'marginBottom': '20px', 'color': '#1f2937'}),
            html.Div([
                html.Div([
                    html.P("Total Gains", style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '5px'}),
                    html.H3(f"${tax_data['total_gains']:,.2f}",
                            style={'color': '#10b981', 'margin': '0', 'fontSize': '28px', 'fontWeight': '700'}),
                ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#d1fae5',
                          'borderRadius': '8px', 'flex': '1'}),

                html.Div([
                    html.P("Total Losses", style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '5px'}),
                    html.H3(f"${tax_data['total_losses']:,.2f}",
                            style={'color': '#ef4444', 'margin': '0', 'fontSize': '28px', 'fontWeight': '700'}),
                ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#fee2e2',
                          'borderRadius': '8px', 'flex': '1', 'margin': '0 20px'}),

                html.Div([
                    html.P("Net Profit", style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '5px'}),
                    html.H3(f"${tax_data['net_trading_income']:,.2f}",
                            style={'color': '#3b82f6', 'margin': '0', 'fontSize': '28px', 'fontWeight': '700'}),
                ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#dbeafe',
                          'borderRadius': '8px', 'flex': '1'}),
            ], style={'display': 'flex', 'gap': '0'}),
        ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '8px',
                  'marginBottom': '20px'}),

        # Tax breakdown
        html.Div([
            html.H3("Tax Breakdown", style={'marginBottom': '20px', 'color': '#1f2937'}),
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Tax Type", style={'textAlign': 'left', 'padding': '15px',
                                                   'backgroundColor': '#f3f4f6', 'fontWeight': '600'}),
                        html.Th("Rate", style={'textAlign': 'center', 'padding': '15px',
                                               'backgroundColor': '#f3f4f6', 'fontWeight': '600'}),
                        html.Th("Amount", style={'textAlign': 'right', 'padding': '15px',
                                                 'backgroundColor': '#f3f4f6', 'fontWeight': '600'}),
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td([
                            html.Div("Federal Tax", style={'fontWeight': '500', 'fontSize': '15px'}),
                            html.Div("Short-term capital gains",
                                     style={'fontSize': '12px', 'color': '#9ca3af', 'marginTop': '3px'}),
                        ], style={'padding': '15px'}),
                        html.Td(f"{tax_data['federal_rate']:.1f}%",
                                style={'padding': '15px', 'textAlign': 'center', 'fontSize': '15px',
                                       'fontWeight': '500'}),
                        html.Td(f"${tax_data['federal_tax']:,.2f}",
                                style={'padding': '15px', 'textAlign': 'right', 'fontSize': '16px',
                                       'fontWeight': '600', 'color': '#ef4444'}),
                    ], style={'borderBottom': '1px solid #e5e7eb'}),

                    html.Tr([
                        html.Td([
                            html.Div("Georgia State Tax", style={'fontWeight': '500', 'fontSize': '15px'}),
                            html.Div("Flat rate on net income",
                                     style={'fontSize': '12px', 'color': '#9ca3af', 'marginTop': '3px'}),
                        ], style={'padding': '15px'}),
                        html.Td(f"{tax_data['ga_rate']:.2f}%",
                                style={'padding': '15px', 'textAlign': 'center', 'fontSize': '15px',
                                       'fontWeight': '500'}),
                        html.Td(f"${tax_data['ga_state_tax']:,.2f}",
                                style={'padding': '15px', 'textAlign': 'right', 'fontSize': '16px',
                                       'fontWeight': '600', 'color': '#ef4444'}),
                    ], style={'borderBottom': '2px solid #e5e7eb'}),

                    html.Tr([
                        html.Td(html.Strong("Total Tax on Trading"),
                                style={'padding': '15px', 'fontSize': '16px'}),
                        html.Td(f"{(tax_data['federal_rate'] + tax_data['ga_rate']):.2f}%",
                                style={'padding': '15px', 'textAlign': 'center', 'fontSize': '15px',
                                       'fontWeight': '600'}),
                        html.Td(html.Strong(f"${tax_data['total_tax_owed']:,.2f}"),
                                style={'padding': '15px', 'textAlign': 'right', 'fontSize': '20px',
                                       'color': '#dc2626'}),
                    ], style={'backgroundColor': '#fef2f2'}),
                ])
            ], style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #e5e7eb',
                      'borderRadius': '8px', 'overflow': 'hidden'}),
        ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '8px',
                  'marginBottom': '20px'}),

        # Quarterly payments
        html.Div([
            html.Div([
                html.Span("📅 ", style={'fontSize': '28px', 'marginRight': '15px'}),
                html.Div([
                    html.H3("Quarterly Estimated Payment", style={'margin': '0 0 5px 0', 'fontSize': '18px'}),
                    html.P(f"Next due: {tax_data['next_deadline']['deadline']} (Q{tax_data['current_quarter']})",
                           style={'margin': '0', 'fontSize': '14px', 'color': '#6b7280'}),
                ]),
            ], style={'display': 'flex', 'alignItems': 'center', 'flex': '1'}),
            html.Div([
                html.H2(f"${tax_data['quarterly_estimate']:,.2f}",
                        style={'margin': '0', 'color': '#ef4444', 'fontSize': '32px', 'fontWeight': '700'}),
            ], style={'textAlign': 'right'}),
        ], style={'backgroundColor': '#fef3c7', 'padding': '25px', 'borderRadius': '8px',
                  'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between',
                  'border': '2px solid #fbbf24', 'marginBottom': '20px'}),

        # Payment schedule
        html.Div([
            html.H3("2025 Quarterly Payment Schedule", style={'marginBottom': '20px'}),
            html.Div([
                html.Div([
                    html.Div([
                        html.H4(f"Q{q['quarter']}",
                                style={'margin': '0 0 8px 0', 'fontSize': '22px',
                                       'color': '#ef4444' if q['quarter'] == tax_data[
                                           'current_quarter'] else '#6b7280'}),
                        html.P(q['period'], style={'margin': '0 0 8px 0', 'fontSize': '13px', 'color': '#6b7280'}),
                        html.P(q['deadline'], style={'margin': '0 0 12px 0', 'fontSize': '14px', 'fontWeight': '500'}),
                        html.P(f"${tax_data['quarterly_estimate']:,.2f}",
                               style={'margin': '0', 'fontSize': '20px', 'fontWeight': '700', 'color': '#1f2937'}),
                    ], style={'padding': '20px', 'textAlign': 'center', 'borderRadius': '8px',
                              'backgroundColor': '#fef3c7' if q['quarter'] == tax_data[
                                  'current_quarter'] else '#f9fafb',
                              'border': f"2px solid {'#fbbf24' if q['quarter'] == tax_data['current_quarter'] else '#e5e7eb'}"})
                ], style={'flex': '1'})
                for q in tax_data['all_quarters']
            ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '15px'}),
        ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '8px',
                  'marginBottom': '20px'}),

        # Simple note
        html.Div([
            html.H3("💡 How This Works", style={'marginBottom': '15px', 'color': '#1f2937'}),
            html.Ul([
                html.Li("This calculates taxes ONLY on your trading profits",
                        style={'marginBottom': '8px', 'color': '#4b5563'}),
                html.Li("Rate used: 24% Federal + 5.49% Georgia = 29.49% total",
                        style={'marginBottom': '8px', 'color': '#4b5563'}),
                html.Li("Make quarterly payments to avoid penalties",
                        style={'marginBottom': '8px', 'color': '#4b5563'}),
                html.Li("Keep this separate from your W-2 withholdings",
                        style={'marginBottom': '8px', 'color': '#4b5563'}),
                html.Li("Consult a tax professional for complete tax planning",
                        style={'marginBottom': '0', 'color': '#ef4444', 'fontWeight': '600'}),
            ], style={'paddingLeft': '25px', 'margin': '0'}),
        ], style={'backgroundColor': '#f0f9ff', 'padding': '25px', 'borderRadius': '8px',
                  'border': '1px solid #bfdbfe'}),

    ], style={'maxWidth': '1000px', 'margin': '0 auto'})


# --- Function to open the browser ---
def open_browser():
    # Wait a moment for the server to start (e.g., 1 second)
    time.sleep(1)
    # Use the webbrowser module to open the default browser to the app's address
    webbrowser.open_new_tab('http://127.0.0.1:8050/')


def render_capital():
    capital = db.get_current_capital()
    transactions = db.get_capital_transactions()

    return html.Div([
        # Summary card
        html.Div([
            html.H2(f"${capital['total']:.2f}", style={'textAlign': 'center', 'color': '#1f2937', 'margin': '0'}),
            html.P("Current Capital", style={'textAlign': 'center', 'color': '#6b7280', 'marginTop': '5px'}),
            html.Div([
                html.Div([
                    html.P("Deposits", style={'fontSize': '12px', 'color': '#6b7280'}),
                    html.H4(f"${capital['deposits']:.2f}", style={'color': '#10b981', 'margin': '5px 0'}),
                ], style={'textAlign': 'center', 'width': '33%', 'display': 'inline-block'}),
                html.Div([
                    html.P("Withdrawals", style={'fontSize': '12px', 'color': '#6b7280'}),
                    html.H4(f"${capital['withdrawals']:.2f}", style={'color': '#ef4444', 'margin': '5px 0'}),
                ], style={'textAlign': 'center', 'width': '33%', 'display': 'inline-block'}),
                html.Div([
                    html.P("Trading P/L", style={'fontSize': '12px', 'color': '#6b7280'}),
                    html.H4(f"${capital['trading_pl']:.2f}",
                            style={'color': '#10b981' if capital['trading_pl'] >= 0 else '#ef4444', 'margin': '5px 0'}),
                ], style={'textAlign': 'center', 'width': '33%', 'display': 'inline-block'}),
            ], style={'marginTop': '20px', 'paddingTop': '20px', 'borderTop': '1px solid #e5e7eb'}),
        ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '8px', 'marginBottom': '20px'}),

        # Deposit form
        html.Div([
            html.H3("Add Deposit", style={'marginBottom': '20px', 'color': '#10b981'}),
            html.Div([
                html.Div([
                    html.Label("Date"),
                    dcc.Input(id='deposit-date', type='text', value=datetime.now().strftime('%Y-%m-%d'),
                              style={'width': '100%', 'padding': '8px'}),
                ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}),
                html.Div([
                    html.Label("Amount"),
                    dcc.Input(id='deposit-amount', type='number', step=0.01,
                              style={'width': '100%', 'padding': '8px'}),
                ], style={'width': '48%', 'display': 'inline-block'}),
            ], style={'marginBottom': '15px'}),
            html.Div([
                html.Label("Notes"),
                dcc.Input(id='deposit-notes', type='text', placeholder='Initial deposit, transfer from bank, etc.',
                          style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
            ]),
            html.Button('Add Deposit', id='add-deposit-btn', n_clicks=0,
                        style={'backgroundColor': '#10b981', 'color': 'white', 'padding': '10px 20px',
                               'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer'}),
            html.Div(id='deposit-output', style={'marginTop': '10px', 'color': '#10b981'}),
        ], style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '8px', 'marginBottom': '20px',
                  'width': '48%', 'display': 'inline-block', 'marginRight': '4%', 'verticalAlign': 'top'}),

        # Withdrawal form
        html.Div([
            html.H3("Add Withdrawal", style={'marginBottom': '20px', 'color': '#ef4444'}),
            html.Div([
                html.Div([
                    html.Label("Date"),
                    dcc.Input(id='withdrawal-date', type='text', value=datetime.now().strftime('%Y-%m-%d'),
                              style={'width': '100%', 'padding': '8px'}),
                ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}),
                html.Div([
                    html.Label("Amount"),
                    dcc.Input(id='withdrawal-amount', type='number', step=0.01,
                              style={'width': '100%', 'padding': '8px'}),
                ], style={'width': '48%', 'display': 'inline-block'}),
            ], style={'marginBottom': '15px'}),
            html.Div([
                html.Label("Notes"),
                dcc.Input(id='withdrawal-notes', type='text', placeholder='Withdrawal to bank, expenses, etc.',
                          style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
            ]),
            html.Button('Add Withdrawal', id='add-withdrawal-btn', n_clicks=0,
                        style={'backgroundColor': '#ef4444', 'color': 'white', 'padding': '10px 20px',
                               'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer'}),
            html.Div(id='withdrawal-output', style={'marginTop': '10px', 'color': '#ef4444'}),
        ], style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '8px', 'marginBottom': '20px',
                  'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        # Transaction history
        html.Div([
            html.H3("Transaction History", style={'marginBottom': '15px'}),
            dash_table.DataTable(
                data=transactions.to_dict('records') if len(transactions) > 0 else [],
                columns=[
                    {'name': 'Date', 'id': 'date'},
                    {'name': 'Type', 'id': 'type'},
                    {'name': 'Amount', 'id': 'amount'},
                    {'name': 'Notes', 'id': 'notes'},
                ],
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#f3f4f6', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{type} = "deposit"'},
                        'color': '#10b981'
                    },
                    {
                        'if': {'filter_query': '{type} = "withdrawal"'},
                        'color': '#ef4444'
                    }
                ]
            ) if len(transactions) > 0 else html.P("No transactions yet",
                                                   style={'textAlign': 'center', 'color': '#9ca3af', 'padding': '20px'})
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px'}),
    ])


@app.callback(
    Output('deposit-output', 'children'),
    Input('add-deposit-btn', 'n_clicks'),
    State('deposit-date', 'value'),
    State('deposit-amount', 'value'),
    State('deposit-notes', 'value'),
    prevent_initial_call=True
)
def add_deposit(n_clicks, date, amount, notes):
    if not amount or float(amount) <= 0:
        return "Please enter a valid amount"

    db.add_capital_transaction(date, 'deposit', float(amount), notes or '')
    return f"✓ Deposit of ${float(amount):.2f} added successfully!"


@app.callback(
    Output('withdrawal-output', 'children'),
    Input('add-withdrawal-btn', 'n_clicks'),
    State('withdrawal-date', 'value'),
    State('withdrawal-amount', 'value'),
    State('withdrawal-notes', 'value'),
    prevent_initial_call=True
)
def add_withdrawal(n_clicks, date, amount, notes):
    if not amount or float(amount) <= 0:
        return "Please enter a valid amount"

    db.add_capital_transaction(date, 'withdrawal', float(amount), notes or '')
    return f"✓ Withdrawal of ${float(amount):.2f} added successfully!"


def render_maintenance():
    return html.Div([
        html.Div([
            html.H2("Database Maintenance", style={'marginBottom': '10px', 'color': '#ef4444'}),
            html.P("⚠️ Warning: Use with caution! These queries directly modify your database.",
                   style={'color': '#f59e0b', 'marginBottom': '20px', 'backgroundColor': '#fef3c7',
                          'padding': '10px', 'borderRadius': '6px', 'border': '1px solid #fbbf24'}),

            html.Div([
                html.H3("Quick Actions", style={'marginBottom': '15px', 'fontSize': '16px'}),
                html.P("Common queries:", style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '10px'}),
                html.Div([
                    html.Button('View All Trades', id='quick-view-trades', n_clicks=0,
                                style={'marginRight': '10px', 'marginBottom': '10px', 'padding': '8px 15px',
                                       'backgroundColor': '#3b82f6', 'color': 'white', 'border': 'none',
                                       'borderRadius': '6px', 'cursor': 'pointer', 'fontSize': '13px'}),
                    html.Button('View Capital Transactions', id='quick-view-capital', n_clicks=0,
                                style={'marginRight': '10px', 'marginBottom': '10px', 'padding': '8px 15px',
                                       'backgroundColor': '#3b82f6', 'color': 'white', 'border': 'none',
                                       'borderRadius': '6px', 'cursor': 'pointer', 'fontSize': '13px'}),
                    html.Button('Count All Records', id='quick-count', n_clicks=0,
                                style={'marginRight': '10px', 'marginBottom': '10px', 'padding': '8px 15px',
                                       'backgroundColor': '#3b82f6', 'color': 'white', 'border': 'none',
                                       'borderRadius': '6px', 'cursor': 'pointer', 'fontSize': '13px'}),
                    html.Button('Fetch Today\'s Stock Data', id='fetch-stock-data-btn', n_clicks=0,
                                style={'marginRight': '10px', 'marginBottom': '10px', 'padding': '8px 15px',
                                       'backgroundColor': '#10b981', 'color': 'white', 'border': 'none',
                                       'borderRadius': '6px', 'cursor': 'pointer', 'fontSize': '13px'}),
                ]),
            ], style={'marginBottom': '25px', 'padding': '15px', 'backgroundColor': '#f9fafb',
                      'borderRadius': '6px', 'border': '1px solid #e5e7eb'}),

            html.Div([
                html.H3("Custom Query", style={'marginBottom': '15px', 'fontSize': '16px'}),
                html.Label("SQL Query:", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Textarea(
                    id='sql-query-input',
                    placeholder='DELETE FROM trades WHERE id = 1;\n\nSELECT * FROM trades WHERE date = "2025-11-11";\n\nUPDATE trades SET ticker = "AAPL" WHERE id = 5;',
                    style={'width': '100%', 'height': '150px', 'padding': '10px',
                           'fontFamily': 'monospace', 'fontSize': '13px',
                           'border': '1px solid #d1d5db', 'borderRadius': '6px',
                           'marginBottom': '15px'}
                ),
                html.Div([
                    html.Button('Execute Query', id='execute-query-btn', n_clicks=0,
                                style={'backgroundColor': '#ef4444', 'color': 'white', 'padding': '10px 20px',
                                       'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
                                       'fontSize': '14px', 'fontWeight': '500', 'marginRight': '10px'}),
                    html.Button('Clear', id='clear-query-btn', n_clicks=0,
                                style={'backgroundColor': '#6b7280', 'color': 'white', 'padding': '10px 20px',
                                       'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
                                       'fontSize': '14px'}),
                ]),
            ], style={'marginBottom': '20px'}),

            html.Div(id='query-output', style={'marginTop': '20px'}),

        ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '8px', 'maxWidth': '900px'})
    ])


@app.callback(
    Output('query-output', 'children', allow_duplicate=True),
    Input('fetch-stock-data-btn', 'n_clicks'),
    prevent_initial_call=True
)
def fetch_stock_data_callback(n_clicks):
    # Run the fetch function
    # This is a simplified version - the full version is in fetch_stock_data.py
    return html.Div([
        html.P("Stock data fetching started! Check terminal for progress.",
               style={'color': '#10b981', 'padding': '15px', 'backgroundColor': '#d1fae5', 'borderRadius': '6px'})
    ])


# Callback for quick action buttons
@app.callback(
    Output('sql-query-input', 'value'),
    Input('quick-view-trades', 'n_clicks'),
    Input('quick-view-capital', 'n_clicks'),
    Input('quick-count', 'n_clicks'),
    Input('clear-query-btn', 'n_clicks'),
    prevent_initial_call=True
)
def set_quick_query(view_trades, view_capital, count, clear):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ''

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'quick-view-trades':
        return 'SELECT * FROM trades ORDER BY date DESC LIMIT 20;'
    elif button_id == 'quick-view-capital':
        return 'SELECT * FROM capital_transactions ORDER BY date DESC;'
    elif button_id == 'quick-count':
        return 'SELECT COUNT(*) as total_trades FROM trades;'
    elif button_id == 'clear-query-btn':
        return ''

    return ''


# Callback for query execution
@app.callback(
    Output('query-output', 'children'),
    Input('execute-query-btn', 'n_clicks'),
    State('sql-query-input', 'value'),
    prevent_initial_call=True
)
def execute_sql_query(n_clicks, query):
    if not query or not query.strip():
        return html.Div([
            html.P("⚠️ Please enter a query", style={'color': '#f59e0b', 'padding': '15px',
                                                     'backgroundColor': '#fef3c7', 'borderRadius': '6px'})
        ])

    result = db.execute_query(query)

    if result['success']:
        if result['type'] == 'select':
            # Display SELECT results in a table
            if len(result['rows']) == 0:
                return html.Div([
                    html.Div([
                        html.P("✓ " + result['message'], style={'color': '#10b981', 'fontWeight': '500'}),
                    ], style={'padding': '15px', 'backgroundColor': '#d1fae5', 'borderRadius': '6px',
                              'marginBottom': '15px'}),
                    html.P("No rows returned.", style={'color': '#6b7280', 'fontStyle': 'italic'})
                ])

            # Create table data
            table_data = []
            for row in result['rows']:
                row_dict = {}
                for i, col in enumerate(result['columns']):
                    row_dict[col] = row[i]
                table_data.append(row_dict)

            return html.Div([
                html.Div([
                    html.P("✓ " + result['message'], style={'color': '#10b981', 'fontWeight': '500'}),
                ], style={'padding': '15px', 'backgroundColor': '#d1fae5', 'borderRadius': '6px',
                          'marginBottom': '15px'}),

                dash_table.DataTable(
                    data=table_data,
                    columns=[{'name': col, 'id': col} for col in result['columns']],
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'fontFamily': 'monospace',
                        'fontSize': '12px'
                    },
                    style_header={
                        'backgroundColor': '#f3f4f6',
                        'fontWeight': 'bold',
                        'border': '1px solid #e5e7eb'
                    },
                    style_data={
                        'border': '1px solid #e5e7eb'
                    },
                    page_size=20,
                )
            ])
        else:
            # Display modification results
            return html.Div([
                html.Div([
                    html.P("✓ " + result['message'],
                           style={'color': '#10b981', 'fontWeight': '500', 'fontSize': '14px'}),
                ], style={'padding': '15px', 'backgroundColor': '#d1fae5', 'borderRadius': '6px'})
            ])
    else:
        # Display error
        return html.Div([
            html.Div([
                html.P("✗ Query Failed", style={'color': '#ef4444', 'fontWeight': '500', 'marginBottom': '8px'}),
                html.P(result['message'], style={'color': '#991b1b', 'fontFamily': 'monospace', 'fontSize': '13px'}),
            ], style={'padding': '15px', 'backgroundColor': '#fee2e2', 'borderRadius': '6px',
                      'border': '1px solid #fca5a5'})
        ])

    # Update color hex displays
    @app.callback(
        [Output('color-profit-primary-hex', 'children'),
         Output('color-profit-secondary-hex', 'children'),
         Output('color-loss-primary-hex', 'children'),
         Output('color-loss-secondary-hex', 'children'),
         Output('color-accent-primary-hex', 'children')],
        [Input('color-profit-primary', 'value'),
         Input('color-profit-secondary', 'value'),
         Input('color-loss-primary', 'value'),
         Input('color-loss-secondary', 'value'),
         Input('color-accent-primary', 'value')]
    )
    def update_hex_displays(c1, c2, c3, c4, c5):
        return c1, c2, c3, c4, c5

    # Save settings
    @app.callback(
        Output('settings-save-status', 'children'),
        Input('save-settings-btn', 'n_clicks'),
        [State('color-profit-primary', 'value'),
         State('color-profit-secondary', 'value'),
         State('color-loss-primary', 'value'),
         State('color-loss-secondary', 'value'),
         State('color-accent-primary', 'value')],
        prevent_initial_call=True
    )
    def save_settings(n_clicks, profit_pri, profit_sec, loss_pri, loss_sec, accent):
        db.save_setting('color_profit_primary', profit_pri)
        db.save_setting('color_profit_secondary', profit_sec)
        db.save_setting('color_loss_primary', loss_pri)
        db.save_setting('color_loss_secondary', loss_sec)
        db.save_setting('color_accent_primary', accent)

        return html.Div([
            html.P("✓ Settings saved! Refresh the page to see changes.",
                   style={'color': '#10b981', 'fontWeight': '500', 'backgroundColor': '#d1fae5',
                          'padding': '10px 15px', 'borderRadius': '6px', 'marginTop': '10px'})
        ])

    # Reset settings
    @app.callback(
        Output('settings-save-status', 'children', allow_duplicate=True),
        Input('reset-settings-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_settings(n_clicks):
        db.reset_settings()
        return html.Div([
            html.P("✓ Settings reset to defaults! Refresh the page.",
                   style={'color': '#3b82f6', 'fontWeight': '500', 'backgroundColor': '#dbeafe',
                          'padding': '10px 15px', 'borderRadius': '6px', 'marginTop': '10px'})
        ])

#Call backs for Validation

# ==================== VALIDATION CALLBACKS ====================

@app.callback(
    [Output('icon-date', 'children'),
     Output('icon-date', 'style')],
    Input('trade-date', 'value'),
    prevent_initial_call=False
)
def validate_date(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value or value == '':
        return "●", {**base_style, 'color': '#9ca3af'}

    # Check if it's a valid date format YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}
        except:
            return "✗", {**base_style, 'color': '#ef4444', 'fontWeight': 'bold'}
    else:
        return "✗", {**base_style, 'color': '#ef4444', 'fontWeight': 'bold'}


@app.callback(
    [Output('icon-ticker', 'children'),
     Output('icon-ticker', 'style')],
    Input('trade-ticker', 'value'),
    prevent_initial_call=False
)
def validate_ticker(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value or value == '':
        return "●", {**base_style, 'color': '#9ca3af'}

    # Check if it's letters only, 1-5 characters
    if value.replace(' ', '').isalpha() and 1 <= len(value.replace(' ', '')) <= 5:
        return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}
    else:
        return "✗", {**base_style, 'color': '#ef4444', 'fontWeight': 'bold'}


@app.callback(
    [Output('icon-sector', 'children'),
     Output('icon-sector', 'style')],
    Input('trade-sector', 'value'),
    prevent_initial_call=False
)
def validate_sector(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value:
        return "●", {**base_style, 'color': '#9ca3af'}
    return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}


@app.callback(
    [Output('icon-news', 'children'),
     Output('icon-news', 'style')],
    Input('trade-news', 'value'),
    prevent_initial_call=False
)
def validate_news(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value:
        return "●", {**base_style, 'color': '#9ca3af'}
    return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}


@app.callback(
    [Output('icon-entry-price', 'children'),
     Output('icon-entry-price', 'style')],
    Input('trade-entry-price', 'value'),
    prevent_initial_call=False
)
def validate_entry_price(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value or value == '':
        return "●", {**base_style, 'color': '#9ca3af'}

    try:
        price = float(value)
        if price > 0:
            return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}
        else:
            return "✗", {**base_style, 'color': '#ef4444', 'fontWeight': 'bold'}
    except:
        return "✗", {**base_style, 'color': '#ef4444', 'fontWeight': 'bold'}


@app.callback(
    [Output('icon-exit-price', 'children'),
     Output('icon-exit-price', 'style')],
    Input('trade-exit-price', 'value'),
    prevent_initial_call=False
)
def validate_exit_price(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value or value == '':
        return "●", {**base_style, 'color': '#9ca3af'}

    try:
        price = float(value)
        if price > 0:
            return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}
        else:
            return "✗", {**base_style, 'color': '#ef4444', 'fontWeight': 'bold'}
    except:
        return "✗", {**base_style, 'color': '#ef4444', 'fontWeight': 'bold'}


@app.callback(
    [Output('icon-entry-time', 'children'),
     Output('icon-entry-time', 'style')],
    Input('trade-entry-time', 'value'),
    prevent_initial_call=False
)
def validate_entry_time(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value or value == '':
        return "●", {**base_style, 'color': '#9ca3af'}
    return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}


@app.callback(
    [Output('icon-exit-time', 'children'),
     Output('icon-exit-time', 'style')],
    Input('trade-exit-time', 'value'),
    prevent_initial_call=False
)
def validate_exit_time(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value or value == '':
        return "●", {**base_style, 'color': '#9ca3af'}
    return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}


@app.callback(
    [Output('icon-shares', 'children'),
     Output('icon-shares', 'style')],
    Input('trade-shares', 'value'),
    prevent_initial_call=False
)
def validate_shares(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value or value == '':
        return "●", {**base_style, 'color': '#9ca3af'}

    try:
        shares = int(value)
        if shares > 0:
            return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}
        else:
            return "✗", {**base_style, 'color': '#ef4444', 'fontWeight': 'bold'}
    except:
        return "✗", {**base_style, 'color': '#ef4444', 'fontWeight': 'bold'}


# Non-required field validations (always show gray or green, never red)
@app.callback(
    [Output('icon-industry', 'children'),
     Output('icon-industry', 'style')],
    Input('trade-industry', 'value'),
    prevent_initial_call=False
)
def validate_industry(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value or value == '':
        return "●", {**base_style, 'color': '#9ca3af'}
    return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}


@app.callback(
    [Output('icon-volume', 'children'),
     Output('icon-volume', 'style')],
    Input('trade-volume', 'value'),
    prevent_initial_call=False
)
def validate_volume(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value or value == '':
        return "●", {**base_style, 'color': '#9ca3af'}
    return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}


@app.callback(
    [Output('icon-avg-volume', 'children'),
     Output('icon-avg-volume', 'style')],
    Input('trade-avg-volume', 'value'),
    prevent_initial_call=False
)
def validate_avg_volume(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value or value == '':
        return "●", {**base_style, 'color': '#9ca3af'}
    return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}


@app.callback(
    [Output('icon-float', 'children'),
     Output('icon-float', 'style')],
    Input('trade-float', 'value'),
    prevent_initial_call=False
)
def validate_float(value):
    base_style = {'fontSize': '18px', 'marginLeft': '8px'}

    if not value or value == '':
        return "●", {**base_style, 'color': '#9ca3af'}
    return "✓", {**base_style, 'color': '#10b981', 'fontWeight': 'bold'}


# ==================== API FETCH CALLBACK ====================

@app.callback(
    [Output('trade-industry', 'value'),
     Output('trade-volume', 'value'),
     Output('trade-avg-volume', 'value'),
     Output('trade-float', 'value'),
     Output('api-fetch-status', 'children')],
    Input('fetch-stock-api-btn', 'n_clicks'),
    State('trade-ticker', 'value'),
    prevent_initial_call=True
)
def fetch_stock_data_for_form(n_clicks, ticker):
    if not ticker or ticker.strip() == '':
        return None, None, None, None, html.Div([
            html.P("⚠️ Please enter a ticker first",
                   style={'color': '#f59e0b', 'padding': '10px', 'backgroundColor': '#fef3c7',
                          'borderRadius': '6px', 'fontSize': '13px'})
        ])

    if not FMP_API_KEY or FMP_API_KEY == 'YOUR_API_KEY_HERE':
        return None, None, None, None, html.Div([
            html.P("⚠️ API key not configured. Please add your FMP API key to src/config.py",
                   style={'color': '#f59e0b', 'padding': '10px', 'backgroundColor': '#fef3c7',
                          'borderRadius': '6px', 'fontSize': '13px'})
        ])

    try:
        from stock_data_api import StockDataAPI
        api = StockDataAPI(api_key=FMP_API_KEY)

        data = api.get_complete_stock_data(ticker.upper().strip())

        if data.get('success'):
            volume = f"{int(data.get('volume', 0)):,}" if data.get('volume') else None
            avg_vol = f"{int(data.get('averageVolume', 0)):,}" if data.get('averageVolume') else None
            float_val = f"{int(data.get('freeFloat', 0)):,}" if data.get('freeFloat') else None

            return (
                data.get('industry', ''),
                volume,
                avg_vol,
                float_val,
                html.Div([
                    html.P(f"✓ Data fetched for {ticker.upper()}!",
                           style={'color': '#10b981', 'padding': '10px', 'backgroundColor': '#d1fae5',
                                  'borderRadius': '6px', 'fontSize': '13px', 'fontWeight': '500'})
                ])
            )
        else:
            return None, None, None, None, html.Div([
                html.P(f"✗ Failed to fetch data: {data.get('error', 'Unknown error')}",
                       style={'color': '#ef4444', 'padding': '10px', 'backgroundColor': '#fee2e2',
                              'borderRadius': '6px', 'fontSize': '13px'})
            ])
    except Exception as e:
        return None, None, None, None, html.Div([
            html.P(f"✗ Error: {str(e)}",
                   style={'color': '#ef4444', 'padding': '10px', 'backgroundColor': '#fee2e2',
                          'borderRadius': '6px', 'fontSize': '13px'})
        ])


if __name__ == '__main__':
    app.run(debug=False)
    threading.Thread(target=open_browser).start()
