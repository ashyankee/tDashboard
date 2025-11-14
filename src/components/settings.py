"""
Settings Component
Allows users to customize colors and appearance
"""
from dash import html, dcc


def render_settings(db):
    """
    Render settings page

    Args:
        db: TradingDatabase instance

    Returns:
        Dash HTML component
    """
    # Get current settings
    settings = db.get_settings()

    return html.Div([
        html.H2("Dashboard Settings", style={'marginBottom': '30px', 'color': '#1f2937'}),

        # Color Settings Section
        html.Div([
            html.H3("Color Customization", style={'marginBottom': '20px', 'color': '#374151', 'fontSize': '18px'}),

            # Profit/Win Colors
            html.Div([
                html.H4("Profit/Win Colors", style={'marginBottom': '15px', 'color': '#4b5563', 'fontSize': '16px'}),

                html.Div([
                    html.Div([
                        html.Label("Primary Profit Color",
                                   style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px',
                                          'display': 'block'}),
                        dcc.Input(
                            id='color-profit-primary',
                            type='color',
                            value=settings.get('color_profit_primary', '#10b981'),
                            style={'width': '100px', 'height': '40px', 'border': '1px solid #d1d5db',
                                   'borderRadius': '6px', 'cursor': 'pointer'}
                        ),
                        html.Span(settings.get('color_profit_primary', '#10b981'),
                                  id='color-profit-primary-hex',
                                  style={'marginLeft': '10px', 'fontSize': '13px', 'color': '#6b7280',
                                         'fontFamily': 'monospace'})
                    ], style={'marginBottom': '15px'}),

                    html.Div([
                        html.Label("Secondary Profit Color",
                                   style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px',
                                          'display': 'block'}),
                        dcc.Input(
                            id='color-profit-secondary',
                            type='color',
                            value=settings.get('color_profit_secondary', '#059669'),
                            style={'width': '100px', 'height': '40px', 'border': '1px solid #d1d5db',
                                   'borderRadius': '6px', 'cursor': 'pointer'}
                        ),
                        html.Span(settings.get('color_profit_secondary', '#059669'),
                                  id='color-profit-secondary-hex',
                                  style={'marginLeft': '10px', 'fontSize': '13px', 'color': '#6b7280',
                                         'fontFamily': 'monospace'})
                    ], style={'marginBottom': '15px'}),
                ]),
            ], style={'backgroundColor': '#f9fafb', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px'}),

            # Loss Colors
            html.Div([
                html.H4("Loss Colors", style={'marginBottom': '15px', 'color': '#4b5563', 'fontSize': '16px'}),

                html.Div([
                    html.Div([
                        html.Label("Primary Loss Color",
                                   style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px',
                                          'display': 'block'}),
                        dcc.Input(
                            id='color-loss-primary',
                            type='color',
                            value=settings.get('color_loss_primary', '#ef4444'),
                            style={'width': '100px', 'height': '40px', 'border': '1px solid #d1d5db',
                                   'borderRadius': '6px', 'cursor': 'pointer'}
                        ),
                        html.Span(settings.get('color_loss_primary', '#ef4444'),
                                  id='color-loss-primary-hex',
                                  style={'marginLeft': '10px', 'fontSize': '13px', 'color': '#6b7280',
                                         'fontFamily': 'monospace'})
                    ], style={'marginBottom': '15px'}),

                    html.Div([
                        html.Label("Secondary Loss Color",
                                   style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px',
                                          'display': 'block'}),
                        dcc.Input(
                            id='color-loss-secondary',
                            type='color',
                            value=settings.get('color_loss_secondary', '#dc2626'),
                            style={'width': '100px', 'height': '40px', 'border': '1px solid #d1d5db',
                                   'borderRadius': '6px', 'cursor': 'pointer'}
                        ),
                        html.Span(settings.get('color_loss_secondary', '#dc2626'),
                                  id='color-loss-secondary-hex',
                                  style={'marginLeft': '10px', 'fontSize': '13px', 'color': '#6b7280',
                                         'fontFamily': 'monospace'})
                    ], style={'marginBottom': '15px'}),
                ]),
            ], style={'backgroundColor': '#f9fafb', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px'}),

            # Neutral Colors
            html.Div([
                html.H4("Accent Colors", style={'marginBottom': '15px', 'color': '#4b5563', 'fontSize': '16px'}),

                html.Div([
                    html.Div([
                        html.Label("Primary Accent (Buttons, Links)",
                                   style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px',
                                          'display': 'block'}),
                        dcc.Input(
                            id='color-accent-primary',
                            type='color',
                            value=settings.get('color_accent_primary', '#3b82f6'),
                            style={'width': '100px', 'height': '40px', 'border': '1px solid #d1d5db',
                                   'borderRadius': '6px', 'cursor': 'pointer'}
                        ),
                        html.Span(settings.get('color_accent_primary', '#3b82f6'),
                                  id='color-accent-primary-hex',
                                  style={'marginLeft': '10px', 'fontSize': '13px', 'color': '#6b7280',
                                         'fontFamily': 'monospace'})
                    ], style={'marginBottom': '15px'}),
                ]),
            ], style={'backgroundColor': '#f9fafb', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '30px'}),

            # Preview Section
            html.Div([
                html.H4("Preview", style={'marginBottom': '15px', 'color': '#4b5563', 'fontSize': '16px'}),
                html.Div([
                    html.Div([
                        html.Div("Profit Example", style={'padding': '15px', 'borderRadius': '6px',
                                                          'marginBottom': '10px', 'color': 'white', 'fontWeight': '600',
                                                          'background': f"linear-gradient(135deg, {settings.get('color_profit_primary', '#10b981')} 0%, {settings.get('color_profit_secondary', '#059669')} 100%)"}),
                        html.Div("Loss Example", style={'padding': '15px', 'borderRadius': '6px',
                                                        'marginBottom': '10px', 'color': 'white', 'fontWeight': '600',
                                                        'background': f"linear-gradient(135deg, {settings.get('color_loss_primary', '#ef4444')} 0%, {settings.get('color_loss_secondary', '#dc2626')} 100%)"}),
                        html.Button("Button Example", style={'padding': '10px 20px', 'borderRadius': '6px',
                                                             'border': 'none', 'color': 'white', 'fontWeight': '500',
                                                             'backgroundColor': settings.get('color_accent_primary',
                                                                                             '#3b82f6'),
                                                             'cursor': 'pointer'}),
                    ], id='color-preview')
                ]),
            ], style={'backgroundColor': '#f9fafb', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '30px'}),

            # Action Buttons
            html.Div([
                html.Button('Save Settings', id='save-settings-btn', n_clicks=0,
                            style={'backgroundColor': '#10b981', 'color': 'white', 'padding': '12px 24px',
                                   'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
                                   'fontSize': '15px', 'fontWeight': '600', 'marginRight': '10px'}),
                html.Button('Reset to Defaults', id='reset-settings-btn', n_clicks=0,
                            style={'backgroundColor': '#6b7280', 'color': 'white', 'padding': '12px 24px',
                                   'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
                                   'fontSize': '15px', 'fontWeight': '600'}),
            ], style={'marginTop': '20px'}),

            html.Div(id='settings-save-status', style={'marginTop': '15px'}),

        ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '8px', 'maxWidth': '800px'}),

    ], style={'maxWidth': '1200px'})