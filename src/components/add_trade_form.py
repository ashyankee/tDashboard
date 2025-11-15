"""
Enhanced Add Trade Form with Validation and API Fetching
"""
from dash import html, dcc


def render_add_trade_form():
    """Render the add trade form with validation icons"""

    return html.Div([
        html.Div([
            html.H2("Add New Trade", style={'marginBottom': '20px'}),

            # Row 1: Date, Ticker, Fetch Button
            html.Div([
                html.Div([
                    html.Label([
                        "Date ",
                        html.Span("*", style={'color': '#ef4444'})
                    ], style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='trade-date',
                            type='text',
                            value='',
                            placeholder='YYYY-MM-DD',
                            style={'width': 'calc(100% - 30px)', 'padding': '8px', 'borderRadius': '6px',
                                   'border': '1px solid #d1d5db', 'fontSize': '14px'}
                        ),
                        html.Span("●", id='icon-date', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1', 'marginRight': '15px'}),

                html.Div([
                    html.Label([
                        "Ticker ",
                        html.Span("*", style={'color': '#ef4444'})
                    ], style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='trade-ticker',
                            type='text',
                            placeholder='AAPL',
                            style={'width': 'calc(100% - 30px)', 'padding': '8px', 'borderRadius': '6px',
                                   'border': '1px solid #d1d5db', 'fontSize': '14px', 'textTransform': 'uppercase'}
                        ),
                        html.Span("●", id='icon-ticker', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1', 'marginRight': '15px'}),

                html.Div([
                    html.Label("\u00A0", style={'fontSize': '14px', 'marginBottom': '8px', 'display': 'block'}),
                    html.Button(
                        '🔍 Fetch from API',
                        id='fetch-stock-api-btn',
                        n_clicks=0,
                        style={'padding': '8px 16px', 'backgroundColor': '#3b82f6', 'color': 'white',
                               'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
                               'fontSize': '14px', 'fontWeight': '500', 'height': '40px'}
                    )
                ], style={'flex': '1'})
            ], style={'display': 'flex', 'marginBottom': '15px'}),

            # API Fetch Status
            html.Div(id='api-fetch-status', style={'marginBottom': '15px'}),

            # Row 2: Sector (API - NOW AUTO-FILLED), Industry (API), Volume (API)
            html.Div([
                html.Div([
                    html.Label([
                        "Sector ",
                        html.Span("*", style={'color': '#ef4444'})
                    ], style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='trade-sector',
                            type='text',
                            placeholder='Auto-populated from API',
                            disabled=True,
                            style={'width': 'calc(100% - 30px)', 'padding': '8px', 'borderRadius': '6px',
                                   'border': '1px solid #d1d5db', 'fontSize': '14px', 'backgroundColor': '#f9fafb'}
                        ),
                        html.Span("●", id='icon-sector', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1', 'marginRight': '15px'}),

                html.Div([
                    html.Label("Industry", style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px',
                                                  'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='trade-industry',
                            type='text',
                            placeholder='Auto-populated from API',
                            disabled=True,
                            style={'width': 'calc(100% - 30px)', 'padding': '8px', 'borderRadius': '6px',
                                   'border': '1px solid #d1d5db', 'fontSize': '14px', 'backgroundColor': '#f9fafb'}
                        ),
                        html.Span("●", id='icon-industry', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1', 'marginRight': '15px'}),

                html.Div([
                    html.Label("Today's Volume", style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px',
                                                        'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='trade-volume',
                            type='text',
                            placeholder='Auto-populated from API',
                            disabled=True,
                            style={'width': 'calc(100% - 30px)', 'padding': '8px', 'borderRadius': '6px',
                                   'border': '1px solid #d1d5db', 'fontSize': '14px', 'backgroundColor': '#f9fafb'}
                        ),
                        html.Span("●", id='icon-volume', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1'})
            ], style={'display': 'flex', 'marginBottom': '15px'}),

            # Row 3: Average Volume (API), Float (API), News Type
            html.Div([
                html.Div([
                    html.Label("Average Volume", style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px',
                                                        'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='trade-avg-volume',
                            type='text',
                            placeholder='Auto-populated from API',
                            disabled=True,
                            style={'width': 'calc(100% - 30px)', 'padding': '8px', 'borderRadius': '6px',
                                   'border': '1px solid #d1d5db', 'fontSize': '14px', 'backgroundColor': '#f9fafb'}
                        ),
                        html.Span("●", id='icon-avg-volume', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1', 'marginRight': '15px'}),

                html.Div([
                    html.Label("Float (Shares)", style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px',
                                                        'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='trade-float',
                            type='text',
                            placeholder='Auto-populated from API',
                            disabled=True,
                            style={'width': 'calc(100% - 30px)', 'padding': '8px', 'borderRadius': '6px',
                                   'border': '1px solid #d1d5db', 'fontSize': '14px', 'backgroundColor': '#f9fafb'}
                        ),
                        html.Span("●", id='icon-float', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1', 'marginRight': '15px'}),

                html.Div([
                    html.Label([
                        "News Type ",
                        html.Span("*", style={'color': '#ef4444'})
                    ], style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    html.Div([
                        dcc.Dropdown(
                            id='trade-news',
                            options=[
                        {'label': 'None', 'value': 'None'},
                        {'label': 'Earnings Beat', 'value': 'Earnings Beat'},
                        {'label': 'Earnings Miss', 'value': 'Earnings Miss'},
                        {'label': 'Earnings Guidance', 'value': 'Earnings Guidance'},
                        {'label': 'Revenue Beat', 'value': 'Revenue Beat'},
                        {'label': 'Revenue Miss', 'value': 'Revenue Miss'},
                        {'label': 'Contract Win', 'value': 'Contract Win'},
                        {'label': 'Government Contract', 'value': 'Government Contract'},
                        {'label': 'Partnership', 'value': 'Partnership'},
                        {'label': 'Merger/Acquisition', 'value': 'Merger/Acquisition'},
                        {'label': 'Acquisition Target', 'value': 'Acquisition Target'},
                        {'label': 'Spinoff', 'value': 'Spinoff'},
                        {'label': 'FDA Approval', 'value': 'FDA Approval'},
                        {'label': 'FDA Rejection', 'value': 'FDA Rejection'},
                        {'label': 'Clinical Trial Results', 'value': 'Clinical Trial Results'},
                        {'label': 'Drug Approval', 'value': 'Drug Approval'},
                        {'label': 'Patent Approval', 'value': 'Patent Approval'},
                        {'label': 'Regulatory Approval', 'value': 'Regulatory Approval'},
                        {'label': 'Analyst Upgrade', 'value': 'Analyst Upgrade'},
                        {'label': 'Analyst Downgrade', 'value': 'Analyst Downgrade'},
                        {'label': 'Price Target Raised', 'value': 'Price Target Raised'},
                        {'label': 'Price Target Lowered', 'value': 'Price Target Lowered'},
                        {'label': 'Initiated Coverage', 'value': 'Initiated Coverage'},
                        {'label': 'Product Launch', 'value': 'Product Launch'},
                        {'label': 'New Product', 'value': 'New Product'},
                        {'label': 'Service Launch', 'value': 'Service Launch'},
                        {'label': 'Share Buyback', 'value': 'Share Buyback'},
                        {'label': 'Dividend Announcement', 'value': 'Dividend Announcement'},
                        {'label': 'Dividend Increase', 'value': 'Dividend Increase'},
                        {'label': 'Dividend Cut', 'value': 'Dividend Cut'},
                        {'label': 'Stock Split', 'value': 'Stock Split'},
                        {'label': 'Reverse Split', 'value': 'Reverse Split'},
                        {'label': 'Insider Buying', 'value': 'Insider Buying'},
                        {'label': 'Insider Selling', 'value': 'Insider Selling'},
                        {'label': 'Institutional Buying', 'value': 'Institutional Buying'},
                        {'label': 'Short Squeeze', 'value': 'Short Squeeze'},
                        {'label': 'High Short Interest', 'value': 'High Short Interest'},
                        {'label': 'CEO Change', 'value': 'CEO Change'},
                        {'label': 'Management Change', 'value': 'Management Change'},
                        {'label': 'Layoffs', 'value': 'Layoffs'},
                        {'label': 'Restructuring', 'value': 'Restructuring'},
                        {'label': 'Bankruptcy Filing', 'value': 'Bankruptcy Filing'},
                        {'label': 'Debt Offering', 'value': 'Debt Offering'},
                        {'label': 'Equity Offering', 'value': 'Equity Offering'},
                        {'label': 'Secondary Offering', 'value': 'Secondary Offering'},
                        {'label': 'IPO', 'value': 'IPO'},
                        {'label': 'Direct Listing', 'value': 'Direct Listing'},
                        {'label': 'SPAC Merger', 'value': 'SPAC Merger'},
                        {'label': 'Delisting Warning', 'value': 'Delisting Warning'},
                        {'label': 'Exchange Listing', 'value': 'Exchange Listing'},
                        {'label': 'Lawsuit Filed', 'value': 'Lawsuit Filed'},
                        {'label': 'Lawsuit Settlement', 'value': 'Lawsuit Settlement'},
                        {'label': 'SEC Investigation', 'value': 'SEC Investigation'},
                        {'label': 'Accounting Issue', 'value': 'Accounting Issue'},
                        {'label': 'Guidance Raised', 'value': 'Guidance Raised'},
                        {'label': 'Guidance Lowered', 'value': 'Guidance Lowered'},
                        {'label': 'Sales Figures', 'value': 'Sales Figures'},
                        {'label': 'Market Share Gain', 'value': 'Market Share Gain'},
                        {'label': 'Competitor News', 'value': 'Competitor News'},
                        {'label': 'Industry News', 'value': 'Industry News'},
                        {'label': 'Commodity Price Move', 'value': 'Commodity Price Move'},
                        {'label': 'Currency Impact', 'value': 'Currency Impact'},
                        {'label': 'Geopolitical Event', 'value': 'Geopolitical Event'},
                        {'label': 'Natural Disaster', 'value': 'Natural Disaster'},
                        {'label': 'Cyber Attack', 'value': 'Cyber Attack'},
                        {'label': 'Data Breach', 'value': 'Data Breach'},
                        {'label': 'Social Media Hype', 'value': 'Social Media Hype'},
                        {'label': 'Reddit/WSB Mention', 'value': 'Reddit/WSB Mention'},
                        {'label': 'Influencer Mention', 'value': 'Influencer Mention'},
                        {'label': 'Unusual Volume', 'value': 'Unusual Volume'},
                        {'label': 'Unusual Options Activity', 'value': 'Unusual Options Activity'},
                        {'label': 'Technical Breakout', 'value': 'Technical Breakout'},
                        {'label': 'Momentum Play', 'value': 'Momentum Play'},
                        {'label': 'Gap Up', 'value': 'Gap Up'},
                        {'label': 'Gap Down', 'value': 'Gap Down'},
                        {'label': 'Sympathy Play', 'value': 'Sympathy Play'},
                        {'label': 'Sector Rotation', 'value': 'Sector Rotation'},
                        {'label': 'Market Rally', 'value': 'Market Rally'},
                        {'label': 'Market Selloff', 'value': 'Market Selloff'},
                        {'label': 'Other', 'value': 'Other'},
                    ],
                            style={'width': 'calc(100% - 30px)'}
                        ),
                        html.Span("●", id='icon-news', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1'})
            ], style={'display': 'flex', 'marginBottom': '15px'}),

            # Row 4: Entry Price, Entry Time
            html.Div([
                html.Div([
                    html.Label([
                        "Entry Price ",
                        html.Span("*", style={'color': '#ef4444'})
                    ], style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='trade-entry-price',
                            type='text',
                            placeholder='18.90',
                            style={'width': 'calc(100% - 30px)', 'padding': '8px', 'borderRadius': '6px',
                                   'border': '1px solid #d1d5db', 'fontSize': '14px'}
                        ),
                        html.Span("●", id='icon-entry-price', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1', 'marginRight': '15px'}),

                html.Div([
                    html.Label([
                        "Entry Time ",
                        html.Span("*", style={'color': '#ef4444'})
                    ], style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='trade-entry-time',
                            type='time',
                            style={'width': 'calc(100% - 30px)', 'padding': '8px', 'borderRadius': '6px',
                                   'border': '1px solid #d1d5db', 'fontSize': '14px'}
                        ),
                        html.Span("●", id='icon-entry-time', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1'})
            ], style={'display': 'flex', 'marginBottom': '15px'}),

            # Row 5: Exit Price, Exit Time
            html.Div([
                html.Div([
                    html.Label([
                        "Exit Price ",
                        html.Span("*", style={'color': '#ef4444'})
                    ], style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='trade-exit-price',
                            type='text',
                            placeholder='22.00',
                            style={'width': 'calc(100% - 30px)', 'padding': '8px', 'borderRadius': '6px',
                                   'border': '1px solid #d1d5db', 'fontSize': '14px'}
                        ),
                        html.Span("●", id='icon-exit-price', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1', 'marginRight': '15px'}),

                html.Div([
                    html.Label([
                        "Exit Time ",
                        html.Span("*", style={'color': '#ef4444'})
                    ], style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='trade-exit-time',
                            type='time',
                            style={'width': 'calc(100% - 30px)', 'padding': '8px', 'borderRadius': '6px',
                                   'border': '1px solid #d1d5db', 'fontSize': '14px'}
                        ),
                        html.Span("●", id='icon-exit-time', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1'})
            ], style={'display': 'flex', 'marginBottom': '15px'}),

            # Row 6: Shares
            html.Div([
                html.Div([
                    html.Label([
                        "Shares ",
                        html.Span("*", style={'color': '#ef4444'})
                    ], style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    html.Div([
                        dcc.Input(
                            id='trade-shares',
                            type='text',
                            placeholder='100',
                            style={'width': 'calc(100% - 30px)', 'padding': '8px', 'borderRadius': '6px',
                                   'border': '1px solid #d1d5db', 'fontSize': '14px'}
                        ),
                        html.Span("●", id='icon-shares', className='validation-icon',
                                  style={'fontSize': '18px', 'color': '#9ca3af', 'marginLeft': '8px'})
                    ], style={'display': 'flex', 'alignItems': 'center'})
                ], style={'flex': '1', 'marginRight': '15px'}),

                html.Div([], style={'flex': '1'})  # Empty space
            ], style={'display': 'flex', 'marginBottom': '15px'}),

            # Row 7: Notes
            html.Div([
                html.Label("Notes",
                           style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Textarea(
                    id='trade-notes',
                    placeholder='MACD reversal at 10:45, strong bounce...',
                    style={'width': '100%', 'padding': '8px', 'borderRadius': '6px',
                           'border': '1px solid #d1d5db', 'fontSize': '14px', 'minHeight': '80px'}
                )
            ], style={'marginBottom': '20px'}),

            # Submit Button
            html.Div([
                html.Button(
                    'Save Trade',
                    id='save-trade-btn',
                    n_clicks=0,
                    style={'backgroundColor': '#10b981', 'color': 'white', 'padding': '12px 32px',
                           'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
                           'fontSize': '16px', 'fontWeight': '600'}
                ),
            ]),

            html.Div(id='save-trade-output', style={'marginTop': '15px'})

        ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '8px', 'maxWidth': '900px'})
    ])