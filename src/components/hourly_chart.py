"""
Hourly Performance Chart Component
Shows net P/L grouped by 15-minute intervals during trading hours
"""
from dash import html


def render_hourly_chart(db):
    """
    Render hourly performance chart

    Args:
        db: TradingDatabase instance

    Returns:
        Dash HTML component
    """
    hourly_data = db.get_hourly_performance()

    if len(hourly_data) == 0:
        return html.Div([
            html.H3("Hourly Performance", className='hourly-title'),
            html.P("No trades yet",
                   style={'textAlign': 'center', 'color': '#9ca3af', 'padding': '40px'})
        ], className='hourly-chart')

    # Find max absolute value for scaling
    max_pnl = max(abs(item['pnl']) for item in hourly_data)

    hourly_rows = []
    for item in hourly_data:
        pnl = item['pnl']
        time_label = item['time']

        # Calculate bar width as percentage (max 45% on each side)
        width_percent = min((abs(pnl) / max_pnl) * 45, 45)

        if pnl > 0:
            # Profit bar (grows right from center)
            bar = html.Div(
                className='hourly-bar hourly-bar-profit',
                style={'width': f'{width_percent}%'}
            )
            # Amount displayed at end of bar
            amount = html.Div(
                f"${pnl:,.2f}",
                className='hourly-amount hourly-amount-right'
            )
        else:
            # Loss bar (grows left from center)
            bar = html.Div(
                className='hourly-bar hourly-bar-loss',
                style={'width': f'{width_percent}%'}
            )
            # Amount displayed at end of bar
            amount = html.Div(
                f"-${abs(pnl):,.2f}",
                className='hourly-amount hourly-amount-left'
            )

        hourly_rows.append(
            html.Div([
                html.Div(time_label, className='hourly-time'),
                html.Div([
                    html.Div(className='hourly-center-line'),
                    bar,
                    amount
                ], className='hourly-bar-container')
            ], className='hourly-row')
        )

    return html.Div([
        html.H3("Hourly Performance", className='hourly-title'),
        html.Div(hourly_rows, className='hourly-rows')
    ], className='hourly-chart')