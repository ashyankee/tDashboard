"""
Callbacks for the Logs tab
"""
from dash import Output, Input, html


def register_logs_callbacks(app, db):
    """Register all logs tab callbacks"""

    @app.callback(
        [Output('logs-status-message', 'children'),
         Output('tab-content', 'children', allow_duplicate=True)],
        [Input('delete-all-logs-btn', 'n_clicks'),
         Input('trim-logs-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def handle_logs_actions(delete_clicks, trim_clicks):
        from dash import callback_context
        from components.logs import render_logs

        if not callback_context.triggered:
            return "", render_logs(db)

        button_id = callback_context.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'delete-all-logs-btn':
            count = db.delete_all_logs()
            db.add_log('DELETE_ALL_LOGS', 'SYSTEM', f'All logs deleted ({count} entries removed)', None)

            message = html.Div([
                html.P(f"✓ Successfully deleted {count} log entries",
                       style={'color': '#10b981', 'padding': '12px', 'backgroundColor': '#d1fae5',
                              'borderRadius': '6px', 'fontSize': '14px', 'fontWeight': '500',
                              'margin': '0'})
            ])

            return message, render_logs(db)

        elif button_id == 'trim-logs-btn':
            deleted = db.trim_logs(keep_count=25)
            db.add_log('TRIM_LOGS', 'SYSTEM', f'Logs trimmed, kept 25 most recent ({deleted} entries removed)', None)

            message = html.Div([
                html.P(f"✓ Successfully trimmed logs. Deleted {deleted} older entries, kept 25 most recent",
                       style={'color': '#f59e0b', 'padding': '12px', 'backgroundColor': '#fef3c7',
                              'borderRadius': '6px', 'fontSize': '14px', 'fontWeight': '500',
                              'margin': '0'})
            ])

            return message, render_logs(db)

        return "", render_logs(db)