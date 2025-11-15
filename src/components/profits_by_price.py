"""
Profits by Price Band Component
Shows total P/L grouped by entry price bands
"""
from dash import html


def render_profits_by_price(db):
    """
    Render profits by price band chart

    Args:
        db: TradingDatabase instance

    Returns:
        Dash HTML component
    """
    price_data = db.get_profits_by_price()

    if len(price_data) == 0:
        return html.Div([
            html.H3("Profits by Price", className='price-chart-title'),
            html.P("No trades yet",
                   style={'textAlign': 'center', 'color': '#9ca3af', 'padding': '40px'})
        ], className='price-chart')

    # Find max absolute value for scaling
    max_pnl = max(abs(item['pnl']) for item in price_data)

    price_rows = []
    for item in price_data:
        pnl = item['pnl']
        price_band = item['price_band']

        # Calculate bar width as percentage (max 45% on each side)
        width_percent = min((abs(pnl) / max_pnl) * 45, 45) if max_pnl > 0 else 0

        if pnl > 0:
            # Profit bar (grows right from center)
            bar = html.Div(
                className='price-bar price-bar-profit',
                style={'width': f'{width_percent}%'}
            )
            # Amount displayed INSIDE the bar at the end
            amount = html.Div(
                f"${pnl:,.0f}",
                className='price-amount price-amount-right',
                style={'left': f'calc(50% + {max(width_percent - 8, 0)}%)'}  # Position inside bar
            )
        else:
            # Loss bar (grows left from center)
            bar = html.Div(
                className='price-bar price-bar-loss',
                style={'width': f'{width_percent}%'}
            )
            # Amount displayed INSIDE the bar at the end
            amount = html.Div(
                f"-${abs(pnl):,.0f}",
                className='price-amount price-amount-left',
                style={'right': f'calc(50% + {max(width_percent - 8, 0)}%)'}  # Position inside bar
            )

        price_rows.append(
            html.Div([
                html.Div(price_band, className='price-label'),
                html.Div([
                    html.Div(className='price-center-line'),
                    bar,
                    amount
                ], className='price-bar-container')
            ], className='price-row')
        )

    return html.Div([
        html.H3("Profits by Price", className='price-chart-title'),
        html.Div(price_rows, className='price-rows')
    ], className='price-chart')