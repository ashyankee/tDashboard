"""
Alpha Vantage API integration
More reliable data for stock metrics
"""
import requests


class AlphaVantageAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.requests_today = 0
        self.max_requests = 500  # Alpha Vantage free tier limit

    def get_company_overview(self, ticker):
        """
        Get company overview including float, sector, industry
        Returns: dict with company data
        """
        params = {
            'function': 'OVERVIEW',
            'symbol': ticker,
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            self.requests_today += 1

            if response.status_code == 200:
                data = response.json()

                # Check if we got valid data (not rate limited)
                if 'Symbol' in data:
                    return {
                        'ticker': data.get('Symbol'),
                        'sector': data.get('Sector'),
                        'industry': data.get('Industry'),
                        'shares_outstanding': int(data.get('SharesOutstanding', 0)),
                        'shares_float': int(data.get('SharesFloat', 0)),
                        'market_cap': int(data.get('MarketCapitalization', 0)) if data.get(
                            'MarketCapitalization') else None,
                        'success': True
                    }
                elif 'Note' in data:
                    return {'error': 'API rate limit reached', 'success': False}
                else:
                    return {'error': 'Invalid ticker or no data available', 'success': False}

            return {'error': f'API returned status {response.status_code}', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}

    def get_global_quote(self, ticker):
        """
        Get real-time quote with current price and volume
        Returns: dict with quote data
        """
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': ticker,
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            self.requests_today += 1

            if response.status_code == 200:
                data = response.json()

                if 'Global Quote' in data and data['Global Quote']:
                    quote = data['Global Quote']
                    return {
                        'ticker': quote.get('01. symbol'),
                        'price': float(quote.get('05. price', 0)),
                        'volume': int(quote.get('06. volume', 0)),
                        'change': float(quote.get('09. change', 0)),
                        'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
                        'success': True
                    }
                elif 'Note' in data:
                    return {'error': 'API rate limit reached', 'success': False}
                else:
                    return {'error': 'Invalid ticker or no data available', 'success': False}

            return {'error': f'API returned status {response.status_code}', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}

    def get_daily_time_series(self, ticker, outputsize='compact'):
        """
        Get daily time series data (last 100 days for compact)
        Returns: dict with time series data
        """
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': ticker,
            'outputsize': outputsize,
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            self.requests_today += 1

            if response.status_code == 200:
                data = response.json()

                if 'Time Series (Daily)' in data:
                    return {
                        'time_series': data['Time Series (Daily)'],
                        'success': True
                    }
                elif 'Note' in data:
                    return {'error': 'API rate limit reached', 'success': False}
                else:
                    return {'error': 'Invalid ticker or no data available', 'success': False}

            return {'error': f'API returned status {response.status_code}', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}

    def calculate_average_volume(self, ticker, days=50):
        """
        Calculate average volume over specified number of days
        Returns: average volume as int
        """
        time_series_data = self.get_daily_time_series(ticker)

        if not time_series_data.get('success'):
            return {'error': time_series_data.get('error'), 'success': False}

        time_series = time_series_data['time_series']
        volumes = []

        # Get volumes from time series (limit to specified days)
        for date, data in list(time_series.items())[:days]:
            volume = int(data.get('5. volume', 0))
            volumes.append(volume)

        if len(volumes) > 0:
            avg_volume = sum(volumes) // len(volumes)
            return {
                'avg_volume': avg_volume,
                'days_calculated': len(volumes),
                'success': True
            }
        else:
            return {'error': 'No volume data available', 'success': False}

    def get_complete_stock_data(self, ticker):
        """
        Get all stock data in one call (uses 3 API requests)
        - Company overview (float, sector, industry)
        - Global quote (current price, volume)
        - Time series (for average volume calculation)
        """
        overview = self.get_company_overview(ticker)
        quote = self.get_global_quote(ticker)
        avg_vol_data = self.calculate_average_volume(ticker, days=50)

        if not overview.get('success'):
            return overview

        if not quote.get('success'):
            return quote

        # Merge all data
        complete_data = {
            'ticker': ticker.upper(),
            'sector': overview.get('sector'),
            'industry': overview.get('industry'),
            'shares_float': overview.get('shares_float'),
            'shares_outstanding': overview.get('shares_outstanding'),
            'market_cap': overview.get('market_cap'),
            'price': quote.get('price'),
            'volume': quote.get('volume'),
            'change': quote.get('change'),
            'change_percent': quote.get('change_percent'),
            'avg_volume': avg_vol_data.get('avg_volume', 0) if avg_vol_data.get('success') else 0,
            'success': True
        }

        return complete_data

    def get_requests_remaining(self):
        """Get number of API requests remaining today"""
        return self.max_requests - self.requests_today

    def get_news_sentiment(self, ticker, limit=50):
        """
        Get news with sentiment analysis for a ticker
        Returns: dict with news articles and sentiment data
        """
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': ticker,
            'limit': limit,
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            self.requests_today += 1

            if response.status_code == 200:
                data = response.json()

                if 'feed' in data:
                    return {
                        'news': data['feed'],
                        'sentiment_label': data.get('sentiment_score_definition'),
                        'success': True
                    }
                elif 'Note' in data:
                    return {'error': 'API rate limit reached', 'success': False}
                else:
                    return {'error': 'No news available', 'success': False}

            return {'error': f'API returned status {response.status_code}', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}