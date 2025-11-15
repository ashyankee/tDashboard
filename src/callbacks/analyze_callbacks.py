"""
Callbacks for the Analyze tab
"""
from dash import Output, Input, State, html
from config import ALPHA_VANTAGE_API_KEY
from datetime import datetime, timedelta


def register_analyze_callbacks(app):
    """Register all analyze tab callbacks"""

    @app.callback(
        [Output('analyze-results', 'children'),
         Output('api-requests-counter', 'children')],
        Input('analyze-btn', 'n_clicks'),
        State('analyze-ticker', 'value'),
        prevent_initial_call=True
    )
    def analyze_stock(n_clicks, ticker):
        from alpha_vantage_api import AlphaVantageAPI
        from components.analyze import render_analysis_results

        # Initialize API counter display
        api_counter = html.Div([
            html.P("API Requests", style={'fontSize': '12px', 'color': '#6b7280', 'margin': '0'}),
            html.P("--/500", id='api-count-display',
                   style={'fontSize': '20px', 'fontWeight': '700', 'color': '#3b82f6', 'margin': '0'})
        ])

        if not ticker or ticker.strip() == '':
            return html.Div([
                html.P("⚠️ Please enter a ticker",
                       style={'color': '#f59e0b', 'padding': '10px', 'backgroundColor': '#fef3c7',
                              'borderRadius': '6px', 'fontSize': '13px'})
            ]), api_counter

        try:
            api = AlphaVantageAPI(api_key=ALPHA_VANTAGE_API_KEY)

            # Fetch complete stock data (uses 3 API calls)
            data = api.get_complete_stock_data(ticker.upper().strip())

            # Fetch news sentiment (uses 1 API call)
            news_data = api.get_news_sentiment(ticker.upper().strip(), limit=50)

            # Update API counter
            remaining = api.get_requests_remaining()
            used = api.requests_today
            counter_color = '#10b981' if remaining > 200 else '#f59e0b' if remaining > 100 else '#ef4444'

            api_counter = html.Div([
                html.P("API Requests Today", style={'fontSize': '12px', 'color': '#6b7280', 'margin': '0'}),
                html.P(f"{used}/{api.max_requests}",
                       style={'fontSize': '20px', 'fontWeight': '700', 'color': counter_color, 'margin': '0'}),
                html.P(f"{remaining} remaining", style={'fontSize': '11px', 'color': '#9ca3af', 'margin': '0'})
            ])

            if data.get('success'):
                # Calculate metrics
                shares_float = data.get('shares_float', 0)
                float_millions = shares_float / 1_000_000  # Convert to millions
                volume = data.get('volume', 0)
                avg_volume = data.get('avg_volume', 0)

                # Calculate float rotation
                float_rotation = (volume / shares_float) if shares_float > 0 else 0

                # Calculate relative volume
                relative_volume = (volume / avg_volume) if avg_volume > 0 else 0

                # Determine float category
                if float_millions < 20:
                    float_category = 'Low Float'
                elif float_millions < 100:
                    float_category = 'Medium Float'
                else:
                    float_category = 'High Float'

                # Process news data - filter for yesterday and today only
                processed_news = []
                if news_data.get('success'):
                    today = datetime.now().date()
                    yesterday = today - timedelta(days=1)

                    for article in news_data.get('news', []):
                        # Parse time published
                        time_published = article.get('time_published', '')
                        if time_published:
                            try:
                                # Format: YYYYMMDDTHHMMSS
                                article_date = datetime.strptime(time_published[:8], '%Y%m%d').date()

                                # Only include yesterday and today
                                if article_date == today or article_date == yesterday:
                                    # Find ticker sentiment
                                    ticker_sentiment = None
                                    for ts in article.get('ticker_sentiment', []):
                                        if ts.get('ticker') == ticker.upper():
                                            ticker_sentiment = {
                                                'score': float(ts.get('ticker_sentiment_score', 0)),
                                                'label': ts.get('ticker_sentiment_label', 'Neutral')
                                            }
                                            break

                                    if ticker_sentiment:
                                        processed_news.append({
                                            'title': article.get('title'),
                                            'url': article.get('url'),
                                            'time_published': time_published,
                                            'source': article.get('source'),
                                            'summary': article.get('summary'),
                                            'banner_image': article.get('banner_image'),
                                            'sentiment_score': ticker_sentiment['score'],
                                            'sentiment_label': ticker_sentiment['label']
                                        })
                            except:
                                continue

                # Prepare data for rendering
                analysis_data = {
                    'success': True,
                    'ticker': ticker.upper(),
                    'free_float': float_millions,  # In millions
                    'volume': volume,
                    'avg_volume': avg_volume,
                    'float_rotation': float_rotation,
                    'relative_volume': relative_volume,
                    'float_category': float_category,
                    'sector': data.get('sector', 'N/A'),
                    'industry': data.get('industry', 'N/A'),
                    'price': data.get('price', 0),
                    'change_percent': data.get('change_percent', '0'),
                    'news': processed_news
                }

                return render_analysis_results(analysis_data), api_counter
            else:
                return render_analysis_results({
                    'success': False,
                    'error': data.get('error', 'Unknown error')
                }), api_counter

        except Exception as e:
            return render_analysis_results({
                'success': False,
                'error': str(e)
            }), api_counter