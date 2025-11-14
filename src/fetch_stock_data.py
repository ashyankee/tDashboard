"""
Fetch stock data for trades
Run this at end of day to populate stock metrics
Usage: python fetch_stock_data.py
"""
import sys

sys.path.insert(0, 'src')

from database import TradingDatabase
from stock_data_api import StockDataAPI
from datetime import datetime, timedelta
import time


def fetch_data_for_today():
    """Fetch stock data for today's trades"""

    # Initialize
    db = TradingDatabase()
    api = StockDataAPI(api_key='3IqYQ2vwZndAoqUbIk3SacOdfTH9AGFq')  # Get from https://site.financialmodelingprep.com/developer/docs/

    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')

    # Get unique tickers from today
    tickers = db.get_unique_tickers_for_date(today)

    if len(tickers) == 0:
        print("No trades found for today or all data already fetched")
        return

    print(f"Fetching data for {len(tickers)} tickers from {today}...")

    # Fetch data for each ticker
    for ticker in tickers:
        print(f"Fetching {ticker}...")

        # Get stock data
        stock_data = api.get_complete_stock_data(ticker)

        if stock_data.get('success'):
            # Get all trades for this ticker today
            trades = db.get_all_trades()
            ticker_trades = trades[
                (trades['ticker'] == ticker) &
                (trades['date'] == today) &
                ((trades['data_fetched'] == 0) | (trades['data_fetched'].isna()))
                ]

            # Update each trade
            for _, trade in ticker_trades.iterrows():
                db.update_trade_stock_data(trade['id'], stock_data)
                print(f"  ✓ Updated trade {trade['id']}")
        else:
            print(f"  ✗ Failed to fetch {ticker}: {stock_data.get('error')}")

        # Rate limiting (be nice to the API)
        time.sleep(0.5)

    print(f"\nComplete! Used {api.requests_today} API requests today")


def fetch_missing_data(days_back=7, max_requests=200):
    """Fetch data for trades missing stock data (backfill)"""

    db = TradingDatabase()
    api = StockDataAPI(api_key='3IqYQ2vwZndAoqUbIk3SacOdfTH9AGFq')

    # Get trades without data
    trades = db.get_trades_without_stock_data(limit=max_requests // 2)

    if len(trades) == 0:
        print("All trades have stock data!")
        return

    # Get unique tickers
    unique_tickers = trades['ticker'].unique()

    print(f"Backfilling data for {len(unique_tickers)} tickers ({len(trades)} trades)...")

    for ticker in unique_tickers:
        if api.requests_today >= max_requests:
            print(f"Reached request limit ({max_requests}). Run again tomorrow.")
            break

        print(f"Fetching {ticker}...")
        stock_data = api.get_complete_stock_data(ticker)

        if stock_data.get('success'):
            # Update all trades for this ticker
            ticker_trades = trades[trades['ticker'] == ticker]
            for _, trade in ticker_trades.iterrows():
                db.update_trade_stock_data(trade['id'], stock_data)
            print(f"  ✓ Updated {len(ticker_trades)} trades")
        else:
            print(f"  ✗ Failed: {stock_data.get('error')}")

        time.sleep(0.5)

    print(f"\nComplete! Used {api.requests_today} API requests")


if __name__ == '__main__':
    print("=== Stock Data Fetcher ===\n")
    print("1. Fetch data for today's trades")
    print("2. Backfill missing data (last 7 days)")
    print("3. Exit")

    choice = input("\nChoose option: ")

    if choice == '1':
        fetch_data_for_today()
    elif choice == '2':
        fetch_missing_data()
    else:
        print("Exiting...")