import sqlite3
import pandas as pd
from datetime import datetime


class TradingDatabase:
    def __init__(self, db_name='trades.db'):
        self.db_name = db_name
        self.create_tables()
        self.create_logs_table()
        self.migrate_logs_table()
        self.migrate_tax_settings()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create trades table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS trades
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           date
                           TEXT
                           NOT
                           NULL,
                           day_of_week
                           TEXT,
                           ticker
                           TEXT
                           NOT
                           NULL,
                           sector
                           TEXT,
                           news_type
                           TEXT,
                           entry_price
                           REAL
                           NOT
                           NULL,
                           entry_time
                           TEXT
                           NOT
                           NULL,
                           exit_price
                           REAL
                           NOT
                           NULL,
                           exit_time
                           TEXT
                           NOT
                           NULL,
                           shares
                           INTEGER
                           NOT
                           NULL,
                           position_size
                           REAL,
                           hold_duration
                           INTEGER,
                           profit_loss
                           REAL,
                           profit_loss_percent
                           REAL,
                           is_win
                           INTEGER,
                           notes
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Create capital transactions table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS capital_transactions
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           date
                           TEXT
                           NOT
                           NULL,
                           type
                           TEXT
                           NOT
                           NULL,
                           amount
                           REAL
                           NOT
                           NULL,
                           notes
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Insert initial capital if not exists
        cursor.execute('SELECT COUNT(*) FROM capital_transactions')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                           INSERT INTO capital_transactions (date, type, amount, notes)
                           VALUES (?, 'deposit', 0, 'Initial balance')
                           ''', (datetime.now().strftime('%Y-%m-%d'),))

        # Create tax settings table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS tax_settings
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           CHECK
                       (
                           id =
                           1
                       ),
                           filing_status TEXT DEFAULT 'married_jointly',
                           user_income REAL DEFAULT 160000,
                           spouse_income REAL DEFAULT 98000,
                           user_visa_status TEXT DEFAULT 'H1B',
                           spouse_visa_status TEXT DEFAULT 'H4_EAD',
                           trader_name TEXT DEFAULT 'Spouse'
                           )
                       ''')

        conn.commit()
        conn.close()

    def add_trade(self, trade_data):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Calculate fields
        entry_price = float(trade_data['entry_price'])
        exit_price = float(trade_data['exit_price'])
        shares = int(trade_data['shares'])

        profit_loss = (exit_price - entry_price) * shares
        profit_loss_percent = ((exit_price - entry_price) / entry_price) * 100
        position_size = entry_price * shares

        # Calculate hold duration
        entry_time_str = trade_data['entry_time']
        exit_time_str = trade_data['exit_time']

        def time_to_minutes(time_str):
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            return hours * 60 + minutes

        entry_minutes = time_to_minutes(entry_time_str)
        exit_minutes = time_to_minutes(exit_time_str)

        if exit_minutes >= entry_minutes:
            hold_duration = exit_minutes - entry_minutes
        else:
            hold_duration = abs(exit_minutes - entry_minutes)

        # Get day of week
        from datetime import datetime
        date_obj = datetime.strptime(trade_data['date'], '%Y-%m-%d')
        day_of_week = date_obj.strftime('%A')

        # Parse optional numeric fields
        volume = float(trade_data['volume']) if trade_data.get('volume') else None
        avg_volume = float(trade_data['avg_volume']) if trade_data.get('avg_volume') else None
        float_val = float(trade_data['float']) if trade_data.get('float') else None

        cursor.execute('''
                       INSERT INTO trades (date, day_of_week, ticker, sector, industry,
                                           news_type, entry_price, entry_time, exit_price, exit_time,
                                           shares, position_size, hold_duration, profit_loss, profit_loss_percent,
                                           is_win, notes, day_volume, avg_volume, float)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ''', (
                           trade_data['date'], day_of_week, trade_data['ticker'],
                           trade_data['sector'], trade_data.get('industry'),
                           trade_data['news_type'],
                           entry_price, entry_time_str, exit_price, exit_time_str, shares,
                           position_size, hold_duration, profit_loss, profit_loss_percent,
                           1 if profit_loss > 0 else 0, trade_data.get('notes', ''),
                           volume, avg_volume, float_val
                       ))

        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_all_trades(self):
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT * FROM trades ORDER BY date DESC', conn)
        conn.close()
        return df

    def get_stats(self):
        df = self.get_all_trades()
        if len(df) == 0:
            return None

        wins = df[df['is_win'] == 1]
        losses = df[df['is_win'] == 0]

        return {
            'total_trades': len(df),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': (len(wins) / len(df)) * 100,
            'total_profit': df['profit_loss'].sum(),
            'avg_win': wins['profit_loss'].mean() if len(wins) > 0 else 0,
            'avg_loss': losses['profit_loss'].mean() if len(losses) > 0 else 0,
            'best_trade': df['profit_loss'].max(),
            'worst_trade': df['profit_loss'].min()
        }

    def export_to_csv(self, filename='trades_export.csv'):
        df = self.get_all_trades()
        df.to_csv(filename, index=False)
        return filename

    def update_tax_settings(self, filing_status, estimated_income, self_employed):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       UPDATE tax_settings
                       SET filing_status    = ?,
                           estimated_income = ?,
                           self_employed    = ?
                       WHERE id = 1
                       ''', (filing_status, estimated_income, 1 if self_employed else 0))
        conn.commit()
        conn.close()

    def get_tax_settings(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tax_settings WHERE id = 1')
        result = cursor.fetchone()
        conn.close()
        return {
            'filing_status': result[1] if result else 'single',
            'estimated_income': result[2] if result else 0,
            'self_employed': bool(result[3]) if result else False
        }

    def add_capital_transaction(self, date, trans_type, amount, notes=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO capital_transactions (date, type, amount, notes)
                       VALUES (?, ?, ?, ?)
                       ''', (date, trans_type, amount, notes))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_capital_transactions(self):
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT * FROM capital_transactions ORDER BY date DESC', conn)
        conn.close()
        return df

    def get_current_capital(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get deposits
        cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM capital_transactions WHERE type = "deposit"')
        deposits = cursor.fetchone()[0]

        # Get withdrawals
        cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM capital_transactions WHERE type = "withdrawal"')
        withdrawals = cursor.fetchone()[0]

        # Get trading profit/loss
        cursor.execute('SELECT COALESCE(SUM(profit_loss), 0) FROM trades')
        trading_pl = cursor.fetchone()[0]

        conn.close()

        return {
            'deposits': deposits,
            'withdrawals': withdrawals,
            'trading_pl': trading_pl,
            'total': deposits - withdrawals + trading_pl
        }

    def get_streak(self):
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT date, profit_loss FROM trades ORDER BY date ASC', conn)
        conn.close()

        if len(df) == 0:
            return {
                'net_positive_current': 0,
                'net_positive_best': 0,
                'zero_loss_current': 0,
                'zero_loss_best': 0
            }

        # Group by date and calculate both metrics
        daily_totals = df.groupby('date')['profit_loss'].sum()
        daily_all_wins = df.groupby('date')['profit_loss'].apply(lambda x: (x > 0).all())

        # Net Positive streak (day's total P/L > 0)
        net_positive_current = 0
        net_positive_best = 0
        temp_streak = 0

        for date in daily_totals.index:
            if daily_totals[date] > 0:
                temp_streak += 1
                net_positive_best = max(net_positive_best, temp_streak)
            else:
                temp_streak = 0

        # Current net positive streak (backwards from most recent)
        for date in reversed(daily_totals.index):
            if daily_totals[date] > 0:
                net_positive_current += 1
            else:
                break

        # Zero Loss streak (all trades profitable that day)
        zero_loss_current = 0
        zero_loss_best = 0
        temp_streak = 0

        for date in daily_all_wins.index:
            if daily_all_wins[date]:
                temp_streak += 1
                zero_loss_best = max(zero_loss_best, temp_streak)
            else:
                temp_streak = 0

        # Current zero loss streak (backwards from most recent)
        for date in reversed(daily_all_wins.index):
            if daily_all_wins[date]:
                zero_loss_current += 1
            else:
                break

        return {
            'net_positive_current': net_positive_current,
            'net_positive_best': net_positive_best,
            'zero_loss_current': zero_loss_current,
            'zero_loss_best': zero_loss_best
        }

    def execute_query(self, query):
        """Execute a SQL query and return results/status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Execute the query
            cursor.execute(query)

            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                conn.close()
                return {
                    'success': True,
                    'type': 'select',
                    'rows': results,
                    'columns': columns,
                    'message': f'Query executed successfully. Returned {len(results)} rows.'
                }
            else:
                # For INSERT, UPDATE, DELETE, etc.
                conn.commit()
                rows_affected = cursor.rowcount
                conn.close()
                return {
                    'success': True,
                    'type': 'modify',
                    'rows_affected': rows_affected,
                    'message': f'Query executed successfully. {rows_affected} row(s) affected.'
                }
        except Exception as e:
            conn.close()
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }

    def calculate_taxes_simple(self):
        """
        Calculate taxes ONLY on trading income
        Simple calculation: How much tax do I owe on my trading profits?
        """
        from datetime import datetime

        conn = self.get_connection()
        cursor = conn.cursor()

        # Get total trading gains and losses
        cursor.execute('SELECT COALESCE(SUM(profit_loss), 0) FROM trades WHERE profit_loss > 0')
        total_gains = cursor.fetchone()[0]

        cursor.execute('SELECT COALESCE(SUM(profit_loss), 0) FROM trades WHERE profit_loss < 0')
        total_losses = abs(cursor.fetchone()[0])

        # Net trading income
        net_trading_income = total_gains - total_losses

        conn.close()

        # If net loss, no taxes owed
        if net_trading_income <= 0:
            return {
                'total_tax_owed': 0,
                'federal_tax': 0,
                'ga_state_tax': 0,
                'net_trading_income': net_trading_income,
                'total_gains': total_gains,
                'total_losses': total_losses,
                'quarterly_estimate': 0,
                'year': datetime.now().year
            }

        # Assume top tax bracket since you have high W-2 income
        # Federal: 24% (your bracket based on $258k household income)
        federal_rate = 0.24
        federal_tax = net_trading_income * federal_rate

        # Georgia: 5.49% flat rate
        ga_rate = 0.0549
        ga_state_tax = net_trading_income * ga_rate

        # Total tax on trading profits
        total_tax = federal_tax + ga_state_tax

        # Quarterly estimate
        quarterly_estimate = total_tax / 4

        # Get current quarter
        current_month = datetime.now().month
        if current_month <= 3:
            current_quarter = 1
        elif current_month <= 5:
            current_quarter = 2
        elif current_month <= 8:
            current_quarter = 3
        else:
            current_quarter = 4

        current_year = datetime.now().year
        quarters = [
            {'quarter': 1, 'period': 'Jan-Mar', 'deadline': f'April 15, {current_year}'},
            {'quarter': 2, 'period': 'Apr-May', 'deadline': f'June 16, {current_year}'},
            {'quarter': 3, 'period': 'Jun-Aug', 'deadline': f'September 15, {current_year}'},
            {'quarter': 4, 'period': 'Sep-Dec', 'deadline': f'January 15, {current_year + 1}'}
        ]

        # Find next deadline
        next_deadline = quarters[current_quarter - 1] if current_quarter <= 4 else quarters[0]

        return {
            'total_tax_owed': total_tax,
            'federal_tax': federal_tax,
            'federal_rate': federal_rate * 100,
            'ga_state_tax': ga_state_tax,
            'ga_rate': ga_rate * 100,
            'net_trading_income': net_trading_income,
            'total_gains': total_gains,
            'total_losses': total_losses,
            'quarterly_estimate': quarterly_estimate,
            'current_quarter': current_quarter,
            'next_deadline': next_deadline,
            'all_quarters': quarters,
            'year': current_year
        }

    def get_tax_settings(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tax_settings WHERE id = 1')
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'filing_status': result[1],
                'user_income': result[2],
                'spouse_income': result[3],
                'visa_status': result[4]
            }
        return {
            'filing_status': 'married_jointly',
            'user_income': 160000,
            'spouse_income': 98000,
            'visa_status': 'H1B'
        }

    def update_tax_settings(self, filing_status, user_income, spouse_income, visa_status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       UPDATE tax_settings
                       SET filing_status = ?,
                           user_income   = ?,
                           spouse_income = ?,
                           visa_status   = ?
                       WHERE id = 1
                       ''', (filing_status, user_income, spouse_income, visa_status))
        conn.commit()
        conn.close()

    def migrate_tax_settings(self):
        """Migrate tax_settings table to new schema"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Check if old columns exist
            cursor.execute("PRAGMA table_info(tax_settings)")
            columns = [col[1] for col in cursor.fetchall()]

            # If user_income doesn't exist, we need to migrate
            if 'user_income' not in columns:
                # Drop old table
                cursor.execute('DROP TABLE IF EXISTS tax_settings')

                # Create new table with correct schema
                cursor.execute('''
                               CREATE TABLE tax_settings
                               (
                                   id                 INTEGER PRIMARY KEY CHECK (id = 1),
                                   filing_status      TEXT DEFAULT 'married_jointly',
                                   user_income        REAL DEFAULT 160000,
                                   spouse_income      REAL DEFAULT 98000,
                                   user_visa_status   TEXT DEFAULT 'H1B',
                                   spouse_visa_status TEXT DEFAULT 'H4_EAD',
                                   trader_name        TEXT DEFAULT 'Spouse'
                               )
                               ''')

                # Insert default values
                cursor.execute('''
                               INSERT INTO tax_settings
                               (id, filing_status, user_income, spouse_income, user_visa_status, spouse_visa_status,
                                trader_name)
                               VALUES (1, 'married_jointly', 160000, 98000, 'H1B', 'H4_EAD', 'Spouse')
                               ''')

                conn.commit()
                print("✓ Tax settings table migrated successfully")
        except Exception as e:
            print(f"Migration error: {e}")
        finally:
            conn.close()

    def get_monthly_calendar(self, year=None, month=None):
        """Get calendar data for a specific month"""
        from datetime import datetime
        import calendar

        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month

        conn = self.get_connection()

        # Get all trades for the month
        query = '''
                SELECT date, SUM (profit_loss) as daily_pnl
                FROM trades
                WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                GROUP BY date \
                '''

        df = pd.read_sql_query(query, conn, params=(str(year), f'{month:02d}'))
        conn.close()

        # Create calendar structure
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]

        # Convert dataframe to dict for easy lookup
        daily_pnl = {}
        for _, row in df.iterrows():
            day = int(row['date'].split('-')[2])
            daily_pnl[day] = float(row['daily_pnl'])

        # Calculate month total
        month_total = sum(daily_pnl.values())

        return {
            'year': year,
            'month': month,
            'month_name': month_name,
            'calendar': cal,
            'daily_pnl': daily_pnl,
            'month_total': month_total,
            'num_trading_days': len(daily_pnl),
            'winning_days': len([v for v in daily_pnl.values() if v > 0]),
            'losing_days': len([v for v in daily_pnl.values() if v < 0])
        }

    def get_hourly_performance(self):
        """Get P/L grouped by 15-minute intervals during trading hours"""
        import pandas as pd
        from datetime import time

        conn = self.get_connection()
        df = pd.read_sql_query('SELECT entry_time, profit_loss FROM trades', conn)
        conn.close()

        if len(df) == 0:
            return []

        # Parse entry times and group into 15-min intervals
        hourly_data = {}

        for _, row in df.iterrows():
            time_str = row['entry_time']
            pnl = row['profit_loss']

            # Parse time
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0

            # Round down to nearest 15-minute interval
            interval_minute = (minute // 15) * 15

            # Create time label
            time_label = f"{hour:02d}:{interval_minute:02d}"

            # Accumulate P/L
            if time_label not in hourly_data:
                hourly_data[time_label] = 0
            hourly_data[time_label] += pnl

        # Convert to list and sort by time
        result = []
        for time_label, pnl in hourly_data.items():
            hour, minute = map(int, time_label.split(':'))
            # Create sortable time value
            time_value = hour * 60 + minute
            result.append({
                'time': time_label,
                'time_value': time_value,
                'pnl': pnl
            })

        # Sort by time
        result.sort(key=lambda x: x['time_value'])

        return result

    def get_settings(self):
        """Get user settings"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create settings table if it doesn't exist
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS settings
                       (
                           key
                           TEXT
                           PRIMARY
                           KEY,
                           value
                           TEXT
                       )
                       ''')

        # Get all settings
        cursor.execute('SELECT key, value FROM settings')
        rows = cursor.fetchall()
        conn.close()

        # Default settings
        defaults = {
            'color_profit_primary': '#10b981',
            'color_profit_secondary': '#059669',
            'color_loss_primary': '#ef4444',
            'color_loss_secondary': '#dc2626',
            'color_accent_primary': '#3b82f6',
        }

        # Override with saved settings
        settings = defaults.copy()
        for key, value in rows:
            settings[key] = value

        return settings

    def save_setting(self, key, value):
        """Save a single setting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
        ''', (key, value))
        conn.commit()
        conn.close()

    def reset_settings(self):
        """Reset all settings to defaults"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM settings')
        conn.commit()
        conn.close()

    def update_trade_stock_data(self, trade_id, stock_data):
        """Update a trade with stock metrics data"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
                       UPDATE trades
                       SET float        = ?,
                           avg_volume   = ?,
                           day_volume   = ?,
                           market_cap   = ?,
                           stock_type   = ?,
                           exchange     = ?,
                           auto_sector  = ?,
                           data_fetched = 1
                       WHERE id = ?
                       ''', (
                           stock_data.get('float'),
                           stock_data.get('avg_volume'),
                           stock_data.get('day_volume'),
                           stock_data.get('market_cap'),
                           stock_data.get('stock_type'),
                           stock_data.get('exchange'),
                           stock_data.get('sector'),
                           trade_id
                       ))

        conn.commit()
        conn.close()

    def get_trades_without_stock_data(self, limit=50):
        """Get trades that haven't had stock data fetched yet"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
                               SELECT id, ticker, date
                               FROM trades
                               WHERE data_fetched = 0 OR data_fetched IS NULL
                               ORDER BY date DESC
                                   LIMIT ?
                               ''', conn, params=(limit,))
        conn.close()
        return df

    def get_unique_tickers_for_date(self, date):
        """Get unique tickers traded on a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT DISTINCT ticker
                       FROM trades
                       WHERE date = ? AND (data_fetched = 0 OR data_fetched IS NULL)
                       ''', (date,))
        tickers = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tickers

    def get_profits_by_price(self):
        """Get P/L grouped by entry price bands"""
        import pandas as pd

        conn = self.get_connection()
        df = pd.read_sql_query('SELECT entry_price, profit_loss FROM trades', conn)
        conn.close()

        if len(df) == 0:
            return []

        # Define price bands
        def get_price_band(price):
            if price < 1:
                return 'Sub $1'
            elif price < 2:
                return '$1'
            elif price < 3:
                return '$2'
            elif price < 4:
                return '$3'
            elif price < 5:
                return '$4'
            elif price < 6:
                return '$5'
            elif price < 7:
                return '$6'
            elif price < 8:
                return '$7'
            elif price < 9:
                return '$8'
            elif price < 10:
                return '$9'
            elif price < 15:
                return '$10-14'
            elif price < 20:
                return '$15-19'
            else:
                return '$20+'

        # Apply price bands
        df['price_band'] = df['entry_price'].apply(get_price_band)

        # Group by price band and sum P/L
        grouped = df.groupby('price_band')['profit_loss'].sum().reset_index()
        grouped.columns = ['price_band', 'pnl']

        # Define band order
        band_order = ['Sub $1', '$1', '$2', '$3', '$4', '$5', '$6', '$7', '$8', '$9',
                      '$10-14', '$15-19', '$20+']

        # Sort by band order
        grouped['sort_order'] = grouped['price_band'].apply(lambda x: band_order.index(x) if x in band_order else 999)
        grouped = grouped.sort_values('sort_order')

        # Convert to list of dicts
        result = []
        for _, row in grouped.iterrows():
            result.append({
                'price_band': row['price_band'],
                'pnl': row['pnl']
            })

        return result

    def create_logs_table(self):
        """Create logs table if it doesn't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS logs
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           timestamp
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           action_type
                           TEXT
                           NOT
                           NULL,
                           action_category
                           TEXT
                           NOT
                           NULL,
                           description
                           TEXT
                           NOT
                           NULL,
                           details
                           TEXT,
                           is_read
                           INTEGER
                           DEFAULT
                           0,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        conn.commit()
        conn.close()

    def add_log(self, action_type, action_category, description, details=None):
        """
        Add a log entry

        Args:
            action_type: Type of action (e.g., 'ADD_TRADE', 'DELETE_TRADE', 'ADD_CAPITAL', 'SYSTEM')
            action_category: Category (e.g., 'TRADE', 'CAPITAL', 'SYSTEM', 'DATABASE')
            description: Human-readable description
            details: Additional details (optional, can be JSON string)

        Returns:
            Log ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
                       INSERT INTO logs (action_type, action_category, description, details)
                       VALUES (?, ?, ?, ?)
                       ''', (action_type, action_category, description, details))

        conn.commit()
        log_id = cursor.lastrowid
        conn.close()

        return log_id

    def get_all_logs(self, limit=None):
        """Get all logs, optionally limited"""
        conn = self.get_connection()

        if limit:
            query = 'SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?'
            df = pd.read_sql_query(query, conn, params=(limit,))
        else:
            query = 'SELECT * FROM logs ORDER BY timestamp DESC'
            df = pd.read_sql_query(query, conn)

        conn.close()
        return df

    def delete_all_logs(self):
        """Delete all log entries"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM logs')
        count = cursor.fetchone()[0]

        cursor.execute('DELETE FROM logs')
        conn.commit()
        conn.close()

        return count

    def trim_logs(self, keep_count=25):
        """Keep only the most recent N logs"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get count before trim
        cursor.execute('SELECT COUNT(*) FROM logs')
        before_count = cursor.fetchone()[0]

        # Delete all except the most recent keep_count
        cursor.execute('''
                       DELETE
                       FROM logs
                       WHERE id NOT IN (SELECT id
                                        FROM logs
                                        ORDER BY timestamp DESC
                           LIMIT ?
                           )
                       ''', (keep_count,))

        conn.commit()
        deleted_count = before_count - keep_count if before_count > keep_count else 0
        conn.close()

        return deleted_count

    def get_unread_logs_count(self):
        """Get count of unread logs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM logs WHERE is_read = 0')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def mark_logs_as_read(self):
        """Mark all logs as read"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE logs SET is_read = 1 WHERE is_read = 0')
        conn.commit()
        conn.close()

    def migrate_logs_table(self):
        """Add is_read column to existing logs table"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Check if column exists
            cursor.execute("PRAGMA table_info(logs)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'is_read' not in columns:
                cursor.execute('ALTER TABLE logs ADD COLUMN is_read INTEGER DEFAULT 0')
                conn.commit()
                print("✓ Added is_read column to logs table")
        except Exception as e:
            print(f"Migration error: {e}")
        finally:
            conn.close()