"""
Stock data fetching from Financial Modeling Prep API
Free tier: 250 requests/day
"""
import requests
from datetime import datetime


class StockDataAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/stable"
        self.requests_today = 0
        self.max_requests = 250

    def get_stock_profile(self, ticker):
        """
        Get company profile data
        Returns: dict with float, sector, industry, exchange, etc.
        """
        if self.requests_today >= self.max_requests:
            return {'error': 'Daily API limit reached'}

        url = f"{self.base_url}/profile?symbol={ticker}&apikey={self.api_key}"

        try:
            response = requests.get(url, timeout=10)
            self.requests_today += 1

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    profile = data[0]
                    return {
                        'ticker': ticker,
                        'market_cap': profile.get('marketCap'),
                        'sector': profile.get('sector'),
                        'industry': profile.get('industry'),
                        'volume': profile.get('volume'),
                        'averageVolume': profile.get('averageVolume'),
                        'exchange': profile.get('exchangeShortName'),
                        'success': True
                    }
            return {'error': f'API returned status {response.status_code}', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}

    def get_stock_quote(self, ticker):
        """
        Get current quote data
        Returns: dict with volume, avg_volume, price
        """
        if self.requests_today >= self.max_requests:
            return {'error': 'Daily API limit reached'}

        url = f"{self.base_url}/shares-float?symbol={ticker}&apikey={self.api_key}"

        try:
            response = requests.get(url, timeout=10)
            self.requests_today += 1

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    quote = data[0]
                    return {
                        'ticker': ticker,
                        'freeFloat': quote.get('freeFloat'),
                        'success': True
                    }
            return {'error': f'API returned status {response.status_code}', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}

    def get_complete_stock_data(self, ticker):
        """
        Get both profile and quote data in one call (uses 2 API requests)
        """
        profile = self.get_stock_profile(ticker)
        quote = self.get_stock_quote(ticker)

        # Merge data
        complete_data = {}
        if profile.get('success'):
            complete_data.update(profile)
        if quote.get('success'):
            complete_data.update(quote)

        complete_data['success'] = profile.get('success') and quote.get('success')
        return complete_data

    def get_stock_news(self, ticker, limit=10):
        """
        Get recent news for a ticker
        Returns: list of news articles
        """
        if self.requests_today >= self.max_requests:
            return {'error': 'Daily API limit reached', 'success': False}

        url = f"{self.base_url}/stock_news?tickers={ticker}&limit={limit}&apikey={self.api_key}"

        try:
            response = requests.get(url, timeout=10)
            self.requests_today += 1

            if response.status_code == 200:
                data = response.json()
                return {
                    'news': data,
                    'success': True
                }
            return {'error': f'API returned status {response.status_code}', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}

    def get_requests_remaining(self):
        """Get number of API requests remaining today"""
        return self.max_requests - self.requests_today