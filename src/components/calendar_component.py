from dash import html
from datetime import datetime


def render_calendar(db):
    """Render monthly trading calendar"""
    current_date = datetime.now()
    calendar_data = db.get_monthly_calendar(current_date.year, current_date.month)

    # Day headers
    day_headers = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    header_row = html.Div([
        html.Div(day, className='cal-header')
        for day in day_headers
    ], className='cal-header-row')

    # Build all day cells
    all_day_cells = []
    for week in calendar_data['calendar']:
        for day in week:
            if day == 0:
                # Empty cell
                all_day_cells.append(html.Div('', className='cal-day cal-empty'))
            else:
                # Check if this day has trades
                if day in calendar_data['daily_pnl']:
                    pnl = calendar_data['daily_pnl'][day]
                    cell_class = 'cal-day cal-profit' if pnl > 0 else 'cal-day cal-loss'

                    # Check if today
                    is_today = (day == current_date.day and current_date.month == calendar_data['month'])
                    if is_today:
                        cell_class += ' cal-today'

                    arrow = '↑' if pnl > 0 else '↓'

                    all_day_cells.append(
                        html.Div([
                            html.Div(str(day), className='cal-day-num'),
                            html.Div([
                                html.Span(arrow, className='cal-arrow'),
                                html.Span(f"${abs(pnl):.0f}", className='cal-amount')
                            ], className='cal-pnl')
                        ], className=cell_class, title=f"${pnl:.2f}")
                    )
                else:
                    # No trades this day
                    cell_class = 'cal-day cal-no-trade'
                    is_today = (day == current_date.day and current_date.month == calendar_data['month'])
                    if is_today:
                        cell_class += ' cal-today'

                    all_day_cells.append(
                        html.Div(str(day), className=cell_class)
                    )

    days_grid = html.Div(all_day_cells, className='cal-grid')

    # Calendar component
    return html.Div([
        # Header
        html.Div([
            html.H3(f"{calendar_data['month_name']} {calendar_data['year']}", className='cal-title'),
            html.Div([
                html.P("Month P/L", className='cal-total-label'),
                html.Div([
                    html.Span('↑ ' if calendar_data['month_total'] >= 0 else '↓ ', className='cal-total-arrow'),
                    html.Span(f"${abs(calendar_data['month_total']):,.2f}", className='cal-total-amount')
                ],
                    className=f"cal-total {'cal-total-profit' if calendar_data['month_total'] >= 0 else 'cal-total-loss'}")
            ]),
        ], className='cal-header-section'),

        header_row,
        days_grid,

        # Stats
        html.Div([
            html.Div([
                html.P(str(calendar_data['winning_days']), className='cal-stat-value cal-stat-green'),
                html.P("Green Days", className='cal-stat-label'),
            ], className='cal-stat'),
            html.Div([
                html.P(str(calendar_data['losing_days']), className='cal-stat-value cal-stat-red'),
                html.P("Red Days", className='cal-stat-label'),
            ], className='cal-stat'),
            html.Div([
                html.P(str(calendar_data['num_trading_days']), className='cal-stat-value cal-stat-blue'),
                html.P("Trading Days", className='cal-stat-label'),
            ], className='cal-stat'),
        ], className='cal-stats'),
    ], className='calendar-container')