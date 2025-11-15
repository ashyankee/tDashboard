"""
Logs Component
Display system and user action logs
"""
from dash import html, dash_table
import pandas as pd


def render_logs(db):
    """Render the logs page"""
    logs_df = db.get_all_logs()

    # Format timestamp for display
    if len(logs_df) > 0:
        logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

    return html.Div([
        html.Div([
            html.Div([
                html.H2("System Logs", style={'marginBottom': '10px', 'color': '#1f2937'}),
                html.P(f"Total entries: {len(logs_df)}",
                       style={'color': '#6b7280', 'marginBottom': '0'}),
            ], style={'flex': '1'}),

            # Action buttons
            html.Div([
                html.Button(
                    '🗑️ Delete All',
                    id='delete-all-logs-btn',
                    n_clicks=0,
                    style={'backgroundColor': '#ef4444', 'color': 'white', 'padding': '10px 20px',
                           'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
                           'fontSize': '14px', 'fontWeight': '600', 'marginRight': '10px'}
                ),
                html.Button(
                    '✂️ Trim Logs (Keep 25)',
                    id='trim-logs-btn',
                    n_clicks=0,
                    style={'backgroundColor': '#f59e0b', 'color': 'white', 'padding': '10px 20px',
                           'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
                           'fontSize': '14px', 'fontWeight': '600'}
                ),
            ], style={'display': 'flex', 'alignItems': 'center'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start',
                  'marginBottom': '20px'}),

        # Status message
        html.Div(id='logs-status-message', style={'marginBottom': '15px'}),

        # Logs table
        html.Div([
            render_logs_table(logs_df) if len(logs_df) > 0 else html.P(
                "No logs yet. System will automatically log all actions.",
                style={'textAlign': 'center', 'color': '#9ca3af', 'padding': '60px',
                       'backgroundColor': '#f9fafb', 'borderRadius': '8px'}
            )
        ])

    ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '8px', 'maxWidth': '1400px'})


def render_logs_table(logs_df):
    """Render the logs as a table"""
    if len(logs_df) == 0:
        return html.P("No logs", style={'textAlign': 'center', 'color': '#9ca3af', 'padding': '20px'})

    # Select columns to display
    display_df = logs_df[['timestamp', 'action_category', 'action_type', 'description', 'details']].copy()

    return dash_table.DataTable(
        data=display_df.to_dict('records'),
        columns=[
            {'name': 'Timestamp', 'id': 'timestamp'},
            {'name': 'Category', 'id': 'action_category'},
            {'name': 'Action', 'id': 'action_type'},
            {'name': 'Description', 'id': 'description'},
            {'name': 'Details', 'id': 'details'},
        ],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontSize': '13px',
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        style_header={
            'backgroundColor': '#f3f4f6',
            'fontWeight': '700',
            'fontSize': '13px',
            'color': '#1f2937',
            'border': '1px solid #e5e7eb',
            'textTransform': 'uppercase',
            'letterSpacing': '0.5px'
        },
        style_data={
            'border': '1px solid #e5e7eb',
            'backgroundColor': 'white',
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'action_category', 'filter_query': '{action_category} = "TRADE"'},
                'backgroundColor': '#dbeafe',
                'fontWeight': '600',
                'color': '#1e40af'
            },
            {
                'if': {'column_id': 'action_category', 'filter_query': '{action_category} = "CAPITAL"'},
                'backgroundColor': '#d1fae5',
                'fontWeight': '600',
                'color': '#065f46'
            },
            {
                'if': {'column_id': 'action_category', 'filter_query': '{action_category} = "SYSTEM"'},
                'backgroundColor': '#fef3c7',
                'fontWeight': '600',
                'color': '#92400e'
            },
            {
                'if': {'column_id': 'action_category', 'filter_query': '{action_category} = "DATABASE"'},
                'backgroundColor': '#fee2e2',
                'fontWeight': '600',
                'color': '#991b1b'
            },
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f9fafb'
            }
        ],
        page_size=50,
        sort_action='native',
        filter_action='native',
    )