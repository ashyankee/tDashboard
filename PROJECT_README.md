# Trading Dashboard Project

## Project Overview
A day trading analytics dashboard built with Plotly Dash and SQLite. Tracks trades, calculates taxes, visualizes performance by time/day, and provides comprehensive analytics.

## Tech Stack
- **Backend**: Python 3.11+, SQLite
- **Frontend**: Plotly Dash, Recharts
- **Styling**: CSS (external stylesheets in assets/)

## Project Structure
```
trading_dashboard/
├── src/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── hourly_chart.py      # Hourly P/L visualization
│   │   ├── calendar_component.py # Monthly calendar heatmap
│   │   └── settings.py           # User customization settings
│   ├── database.py               # SQLite ORM and queries
│   └── app.py                    # Main Dash application
├── assets/
│   ├── style.css                 # Main stylesheet
│   ├── calendar.css              # Calendar-specific styles
│   └── hourly_chart.css          # Hourly chart styles
└── trades.db                     # SQLite database
```

## Database Schema

### Tables:
1. **trades** - All trading transactions
   - Fields: date, ticker, sector, news_type, entry_price, entry_time, exit_price, exit_time, shares, profit_loss, hold_duration, etc.

2. **capital_transactions** - Deposits/withdrawals
   - Fields: date, type (deposit/withdrawal), amount, notes

3. **tax_settings** - User tax information
   - Fields: filing_status, user_income, spouse_income, visa_status

4. **settings** - UI customization settings
   - Key-value pairs for colors, preferences

## Key Features

### Dashboard Tab
- Current capital display (deposits - withdrawals + trading P/L)
- Win streak tracker (net positive and zero loss streaks)
- Stats cards (total profit, win rate, avg win/loss, best/worst)
- Monthly calendar heatmap (green/red days)
- Hourly performance chart (15-min intervals)
- Recent trades table (flashy green/red styling)

### Add Trade Tab
- Form to log trades with all details
- Supports penny stock precision (5+ decimals)
- Auto-calculates P/L, hold duration, day of week

### Capital Tab
- Track deposits and withdrawals
- View transaction history
- Shows current capital breakdown

### Tax Calculator Tab
- **ONLY calculates taxes on trading profits** (not full household income)
- 24% Federal + 5.49% Georgia = 29.49% total
- Quarterly payment schedule
- Tracks gains/losses separately
- H4 EAD specific (spouse trading, H1B holder cannot day trade)

### Settings Tab
- Customize profit/loss colors
- Accent color customization
- Preview changes
- Persistent storage

### Maintenance Tab
- Execute SQL queries directly
- View/modify database
- Quick action buttons (view trades, capital transactions)
- Safety warnings

## Important Business Logic

### Trading Rules
- Wife on H4 EAD does the trading (H1B holder cannot day trade)
- All trades are same-day (no overnight holds)
- Entry/exit times tracked for hourly analysis
- Hold times in minutes (sometimes negative if AM/PM confusion)

### Tax Calculation
- Only taxes trading profits, not household W-2 income
- Married Filing Jointly
- Georgia resident (5.49% flat state tax)
- Federal rate: 24% (based on $258k household income bracket)
- NO self-employment tax (investor status, not trader status)

### Streak Calculation
- **Net Positive Streak**: Days where total P/L > 0 (can have some losers)
- **Zero Loss Streak**: Days with NO losing trades at all
- Tracks current and best streaks

### Calendar Logic
- Groups trades by date, sums daily P/L
- Green = net positive day, Red = net loss day
- Shows $ amount on each day
- Only current month displayed

### Hourly Chart Logic
- Groups trades by 15-minute intervals (entry time)
- Rounds 9:05 → 9:00, 10:11 → 10:15, etc.
- Accumulates all trades in that interval
- Green bars grow right (profit), red bars grow left (loss)
- Bar width scales to P/L amount

## Known Issues/Quirks
- Dashboard doesn't auto-refresh after database changes (need to switch tabs or refresh page)
- Hold times can be negative if entry/exit times cross AM/PM incorrectly
- Capital vs Total Gains confusion: Gains can be higher than capital (compounding)
- Must use `type='time'` inputs to avoid AM/PM confusion

## Running the App
```bash
python src/app.py
# Opens on http://127.0.0.1:8050
```

## Development Notes
- All database methods in `database.py` (TradingDatabase class)
- All UI components in `src/components/`
- CSS is modular (separate files for major components)
- Uses Dash callbacks for interactivity
- No localStorage (not supported in artifacts)
- Cash account trading (no PDT rule issues)

## User Context
- User: H1B visa holder, $160k salary
- Spouse: H4 EAD, $98k salary + day trading
- Location: Georgia
- Filing: Married Filing Jointly
- Capital: Started with ~$2k-$5k
- Strategy: Momentum day trading (10-15 min holds, MACD strategy)
- Goal: Track performance, optimize timing, calculate taxes
```

## Option 2: Quick Onboarding Prompt

Copy this into a new chat:
```
I have an existing trading dashboard project I need help with. Here's the context:

**Project**: Day trading analytics dashboard (Python/Dash/SQLite)
**Structure**: src/app.py (main), src/database.py (SQLite ORM), src/components/ (UI components), assets/ (CSS)

**Key Details**:
- Wife trades on H4 EAD (I'm H1B, can't day trade)
- Tax calc: ONLY on trading profits (24% Fed + 5.49% GA)
- Cash account, momentum day trading (10-15min holds)
- Calendar shows monthly P/L heatmap
- Hourly chart groups by 15min intervals (entry time)
- Streak tracking (net positive vs zero loss)

**Database tables**: trades, capital_transactions, tax_settings, settings

**Current issue**: [describe what you need help with]

The project is in: /path/to/trading_dashboard/

Files to reference: [list specific files if needed]