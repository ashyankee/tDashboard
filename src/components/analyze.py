"""
Stock Analysis Component
Pre-trade screening tool
"""
from dash import html, dcc


def render_analyze():
    """Render the analyze tab"""
    return html.Div([
        html.Div([
            # Header with API counter
            html.Div([
                html.Div([
                    html.H2("Stock Analyzer",
                            style={'marginBottom': '10px', 'color': '#1f2937', 'display': 'inline-block'}),
                    html.P("Quick pre-trade screening tool",
                           style={'color': '#6b7280', 'marginBottom': '0px'}),
                ], style={'flex': '1'}),

                # API Requests Counter
                html.Div(id='api-requests-counter', style={'textAlign': 'right'}),

            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start',
                      'marginBottom': '30px'}),

            # Ticker Input
            html.Div([
                html.Label("Enter Ticker Symbol",
                           style={'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                html.Div([
                    dcc.Input(
                        id='analyze-ticker',
                        type='text',
                        placeholder='OTLK',
                        style={'width': '200px', 'padding': '10px', 'borderRadius': '6px',
                               'border': '1px solid #d1d5db', 'fontSize': '16px',
                               'textTransform': 'uppercase', 'marginRight': '10px'}
                    ),
                    html.Button(
                        'Analyze',
                        id='analyze-btn',
                        n_clicks=0,
                        style={'backgroundColor': '#3b82f6', 'color': 'white', 'padding': '10px 24px',
                               'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
                               'fontSize': '16px', 'fontWeight': '600'}
                    ),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '30px'}),
            ]),

            # Analysis Results
            html.Div(id='analyze-results', style={'marginTop': '20px'})

        ], style={'backgroundColor': 'white', 'padding': '40px', 'borderRadius': '8px', 'maxWidth': '1200px'})
    ])


def render_analysis_results(data):
    """Render the analysis results after fetching data"""

    if not data.get('success'):
        return html.Div([
            html.P(f"⚠️ {data.get('error', 'Failed to fetch data')}",
                   style={'color': '#ef4444', 'padding': '15px', 'backgroundColor': '#fee2e2',
                          'borderRadius': '6px', 'fontSize': '14px'})
        ])

    ticker = data.get('ticker', 'N/A')
    free_float = data.get('free_float', 0)
    volume = data.get('volume', 0)
    avg_volume = data.get('avg_volume', 0)
    float_rotation = data.get('float_rotation', 0)
    relative_volume = data.get('relative_volume', 0)
    float_category = data.get('float_category', 'Unknown')
    sector = data.get('sector', 'N/A')
    industry = data.get('industry', 'N/A')
    price = data.get('price', 0)
    news_articles = data.get('news', [])

    # Determine color for float category
    if float_category == 'Low Float':
        float_color = '#ef4444'
        float_icon = '🔥'
        float_desc = 'High volatility potential - Can move significantly on volume'
    elif float_category == 'Medium Float':
        float_color = '#f59e0b'
        float_icon = '⚡'
        float_desc = 'Good balance of liquidity and movement'
    else:
        float_color = '#3b82f6'
        float_icon = '💧'
        float_desc = 'High liquidity - Harder to move significantly'

    # Determine if relative volume is high
    rvol_hot = relative_volume > 2.0
    rotation_hot = float_rotation > 1.0

    # Calculate sentiment metrics
    sentiment_metrics = calculate_sentiment_metrics(news_articles)

    return html.Div([
        # ==================== SECTION 1: STOCK METRICS ====================
        html.Div([
            # Header with ticker
            html.Div([
                html.H1(ticker, style={'display': 'inline-block', 'margin': '0 15px 0 0',
                                       'color': '#1f2937', 'fontSize': '36px'}),
                html.Span(f"${price:.2f}", style={'fontSize': '24px', 'color': '#6b7280', 'marginRight': '10px'}),
                html.Span(f"{data.get('change_percent', '0')}%",
                          style={'fontSize': '18px', 'fontWeight': '600',
                                 'color': '#10b981' if float(data.get('change_percent', 0)) > 0 else '#ef4444'})
            ], style={'marginBottom': '10px'}),

            html.Div([
                html.Span(f"{sector}", style={'fontSize': '14px', 'color': '#6b7280', 'marginRight': '15px'}),
                html.Span(f"• {industry}", style={'fontSize': '14px', 'color': '#6b7280'}),
            ], style={'marginBottom': '30px'}),

            # Float Category Banner
            html.Div([
                html.Span(float_icon, style={'fontSize': '28px', 'marginRight': '15px'}),
                html.Div([
                    html.H3(float_category, style={'margin': '0', 'fontSize': '24px', 'fontWeight': '700'}),
                    html.P(float_desc, style={'margin': '5px 0 0 0', 'fontSize': '14px'}),
                ])
            ], style={'backgroundColor': float_color + '20', 'padding': '20px', 'borderRadius': '8px',
                      'marginBottom': '30px', 'border': f'2px solid {float_color}',
                      'display': 'flex', 'alignItems': 'center'}),

            # Key Metrics Grid
            html.Div([
                # Free Float
                html.Div([
                    html.P("Free Float", style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '5px'}),
                    html.H2(f"{free_float:.2f}M",
                            style={'color': '#1f2937', 'margin': '0', 'fontSize': '28px', 'fontWeight': '700'}),
                ], style={'padding': '20px', 'backgroundColor': '#f9fafb', 'borderRadius': '8px',
                          'border': '1px solid #e5e7eb'}),

                # Volume
                html.Div([
                    html.P("Current Volume", style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '5px'}),
                    html.H2(f"{volume:,.0f}",
                            style={'color': '#1f2937', 'margin': '0', 'fontSize': '28px', 'fontWeight': '700'}),
                ], style={'padding': '20px', 'backgroundColor': '#f9fafb', 'borderRadius': '8px',
                          'border': '1px solid #e5e7eb'}),

                # Avg Volume
                html.Div([
                    html.P("Avg Volume", style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '5px'}),
                    html.H2(f"{avg_volume:,.0f}",
                            style={'color': '#1f2937', 'margin': '0', 'fontSize': '28px', 'fontWeight': '700'}),
                ], style={'padding': '20px', 'backgroundColor': '#f9fafb', 'borderRadius': '8px',
                          'border': '1px solid #e5e7eb'}),

            ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)', 'gap': '20px',
                      'marginBottom': '30px'}),

            # Analysis Metrics
            html.Div([
                html.H3("Analysis Metrics", style={'marginBottom': '20px', 'color': '#1f2937'}),

                html.Div([
                    # Float Rotation
                    html.Div([
                        html.Div([
                            html.P("Float Rotation",
                                   style={'fontSize': '14px', 'color': '#6b7280', 'marginBottom': '8px'}),
                            html.Div([
                                html.H2(f"{float_rotation:.2f}x",
                                        style={'color': '#10b981' if rotation_hot else '#6b7280',
                                               'margin': '0', 'fontSize': '32px', 'fontWeight': '700',
                                               'display': 'inline-block', 'marginRight': '10px'}),
                                html.Span('🔥 HOT!' if rotation_hot else '',
                                          style={'fontSize': '18px', 'fontWeight': '600', 'color': '#ef4444'}),
                            ], style={'display': 'flex', 'alignItems': 'center'}),
                            html.P("Volume / Float",
                                   style={'fontSize': '12px', 'color': '#9ca3af', 'marginTop': '5px'}),
                        ]),
                        html.Div([
                            html.P(
                                '✓ High interest - shares trading multiple times' if rotation_hot
                                else 'Low rotation - limited interest',
                                style={'fontSize': '13px', 'color': '#10b981' if rotation_hot else '#6b7280',
                                       'marginTop': '10px', 'padding': '10px',
                                       'backgroundColor': '#d1fae5' if rotation_hot else '#f3f4f6',
                                       'borderRadius': '6px'}
                            )
                        ])
                    ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '8px',
                              'border': '2px solid #10b981' if rotation_hot else '1px solid #e5e7eb'}),

                    # Relative Volume
                    html.Div([
                        html.Div([
                            html.P("Relative Volume",
                                   style={'fontSize': '14px', 'color': '#6b7280', 'marginBottom': '8px'}),
                            html.Div([
                                html.H2(f"{relative_volume:.2f}x",
                                        style={'color': '#10b981' if rvol_hot else '#6b7280',
                                               'margin': '0', 'fontSize': '32px', 'fontWeight': '700',
                                               'display': 'inline-block', 'marginRight': '10px'}),
                                html.Span('🔥 HOT!' if rvol_hot else '',
                                          style={'fontSize': '18px', 'fontWeight': '600', 'color': '#ef4444'}),
                            ], style={'display': 'flex', 'alignItems': 'center'}),
                            html.P("Current / Average Volume",
                                   style={'fontSize': '12px', 'color': '#9ca3af', 'marginTop': '5px'}),
                        ]),
                        html.Div([
                            html.P(
                                '✓ Above average volume - strong interest' if rvol_hot
                                else 'Below average volume',
                                style={'fontSize': '13px', 'color': '#10b981' if rvol_hot else '#6b7280',
                                       'marginTop': '10px', 'padding': '10px',
                                       'backgroundColor': '#d1fae5' if rvol_hot else '#f3f4f6',
                                       'borderRadius': '6px'}
                            )
                        ])
                    ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '8px',
                              'border': '2px solid #10b981' if rvol_hot else '1px solid #e5e7eb'}),

                ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px'}),

            ], style={'backgroundColor': '#f9fafb', 'padding': '30px', 'borderRadius': '8px',
                      'marginBottom': '30px'}),

        ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '8px',
                  'marginBottom': '30px', 'border': '1px solid #e5e7eb'}),

        # ==================== SECTION 2: NEWS & SENTIMENT ====================
        html.Div([
            html.H2("📰 News & Sentiment Analysis", style={'marginBottom': '20px', 'color': '#1f2937'}),
            html.P("Recent news from yesterday and today", style={'color': '#6b7280', 'marginBottom': '30px'}),

            # Sentiment Summary
            render_sentiment_summary(sentiment_metrics),

            # News Articles
            html.Div([
                html.H3("Recent Articles", style={'marginBottom': '20px', 'color': '#1f2937'}),
                render_news_articles(news_articles)
            ], style={'marginTop': '30px'}),

        ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '8px',
                  'marginBottom': '30px', 'border': '1px solid #e5e7eb'}),

        # ==================== FINAL RECOMMENDATION ====================
        render_trade_recommendation(float_category, rotation_hot, rvol_hot, sentiment_metrics),

    ])


def calculate_sentiment_metrics(news_articles):
    """Calculate aggregated sentiment metrics from news"""
    if not news_articles or len(news_articles) == 0:
        return {
            'total_articles': 0,
            'avg_score': 0,
            'bullish_count': 0,
            'bearish_count': 0,
            'neutral_count': 0,
            'overall_sentiment': 'Neutral',
            'sentiment_strength': 'No Data'
        }

    scores = [article['sentiment_score'] for article in news_articles]
    labels = [article['sentiment_label'] for article in news_articles]

    avg_score = sum(scores) / len(scores) if scores else 0

    # Count sentiment labels
    bullish_count = sum(1 for label in labels if 'Bullish' in label)
    bearish_count = sum(1 for label in labels if 'Bearish' in label)
    neutral_count = sum(1 for label in labels if 'Neutral' in label)

    # Determine overall sentiment
    if avg_score > 0.15:
        overall_sentiment = 'Bullish'
        sentiment_strength = 'Strong' if avg_score > 0.3 else 'Moderate'
    elif avg_score < -0.15:
        overall_sentiment = 'Bearish'
        sentiment_strength = 'Strong' if avg_score < -0.3 else 'Moderate'
    else:
        overall_sentiment = 'Neutral'
        sentiment_strength = 'Weak'

    return {
        'total_articles': len(news_articles),
        'avg_score': avg_score,
        'bullish_count': bullish_count,
        'bearish_count': bearish_count,
        'neutral_count': neutral_count,
        'overall_sentiment': overall_sentiment,
        'sentiment_strength': sentiment_strength
    }


def render_sentiment_summary(metrics):
    """Render sentiment summary with visualization"""
    if metrics['total_articles'] == 0:
        return html.Div([
            html.P("No recent news found for yesterday or today",
                   style={'textAlign': 'center', 'color': '#9ca3af', 'padding': '40px',
                          'backgroundColor': '#f9fafb', 'borderRadius': '8px'})
        ])

    # Sentiment color
    if metrics['overall_sentiment'] == 'Bullish':
        sentiment_color = '#10b981'
        sentiment_icon = '📈'
    elif metrics['overall_sentiment'] == 'Bearish':
        sentiment_color = '#ef4444'
        sentiment_icon = '📉'
    else:
        sentiment_color = '#6b7280'
        sentiment_icon = '➡️'

    return html.Div([
        # Overall Sentiment Banner
        html.Div([
            html.Span(sentiment_icon, style={'fontSize': '32px', 'marginRight': '15px'}),
            html.Div([
                html.H3(f"{metrics['overall_sentiment']} Sentiment",
                        style={'margin': '0', 'fontSize': '28px', 'fontWeight': '700', 'color': sentiment_color}),
                html.P(f"{metrics['sentiment_strength']} - Based on {metrics['total_articles']} articles",
                       style={'margin': '5px 0 0 0', 'fontSize': '14px', 'color': '#6b7280'}),
            ])
        ], style={'backgroundColor': sentiment_color + '15', 'padding': '25px', 'borderRadius': '8px',
                  'border': f'2px solid {sentiment_color}', 'display': 'flex', 'alignItems': 'center',
                  'marginBottom': '25px'}),

        # Sentiment Breakdown
        html.Div([
            # Avg Sentiment Score
            html.Div([
                html.P("Avg Sentiment Score", style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '8px'}),
                html.H2(f"{metrics['avg_score']:.3f}",
                        style={'color': sentiment_color, 'margin': '0', 'fontSize': '32px', 'fontWeight': '700'}),
                html.P("(-1 to +1 scale)", style={'fontSize': '11px', 'color': '#9ca3af', 'marginTop': '5px'}),
            ], style={'padding': '20px', 'backgroundColor': '#f9fafb', 'borderRadius': '8px',
                      'border': '1px solid #e5e7eb', 'textAlign': 'center'}),

            # Bullish Articles
            html.Div([
                html.P("Bullish Articles", style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '8px'}),
                html.H2(str(metrics['bullish_count']),
                        style={'color': '#10b981', 'margin': '0', 'fontSize': '32px', 'fontWeight': '700'}),
                html.P(f"{(metrics['bullish_count'] / metrics['total_articles'] * 100):.0f}% of total",
                       style={'fontSize': '11px', 'color': '#9ca3af', 'marginTop': '5px'}),
            ], style={'padding': '20px', 'backgroundColor': '#d1fae5', 'borderRadius': '8px',
                      'border': '1px solid #10b981', 'textAlign': 'center'}),

            # Neutral Articles
            html.Div([
                html.P("Neutral Articles", style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '8px'}),
                html.H2(str(metrics['neutral_count']),
                        style={'color': '#6b7280', 'margin': '0', 'fontSize': '32px', 'fontWeight': '700'}),
                html.P(f"{(metrics['neutral_count'] / metrics['total_articles'] * 100):.0f}% of total",
                       style={'fontSize': '11px', 'color': '#9ca3af', 'marginTop': '5px'}),
            ], style={'padding': '20px', 'backgroundColor': '#f3f4f6', 'borderRadius': '8px',
                      'border': '1px solid #d1d5db', 'textAlign': 'center'}),

            # Bearish Articles
            html.Div([
                html.P("Bearish Articles", style={'fontSize': '13px', 'color': '#6b7280', 'marginBottom': '8px'}),
                html.H2(str(metrics['bearish_count']),
                        style={'color': '#ef4444', 'margin': '0', 'fontSize': '32px', 'fontWeight': '700'}),
                html.P(f"{(metrics['bearish_count'] / metrics['total_articles'] * 100):.0f}% of total",
                       style={'fontSize': '11px', 'color': '#9ca3af', 'marginTop': '5px'}),
            ], style={'padding': '20px', 'backgroundColor': '#fee2e2', 'borderRadius': '8px',
                      'border': '1px solid #ef4444', 'textAlign': 'center'}),

        ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '15px'}),
    ])


def render_news_articles(news_articles):
    """Render news articles with sentiment"""
    if not news_articles or len(news_articles) == 0:
        return html.P("No articles found",
                      style={'textAlign': 'center', 'color': '#9ca3af', 'padding': '20px'})

    from datetime import datetime

    news_items = []
    for article in news_articles:
        # Parse time
        time_published = article['time_published']
        try:
            dt = datetime.strptime(time_published[:8], '%Y%m%d')
            time_str = dt.strftime('%b %d, %Y')
            hour = time_published[9:11]
            minute = time_published[11:13]
            time_str += f" at {hour}:{minute}"
        except:
            time_str = 'Unknown'

        # Sentiment color
        sentiment_label = article['sentiment_label']
        if 'Bullish' in sentiment_label:
            sentiment_color = '#10b981'
            sentiment_bg = '#d1fae5'
        elif 'Bearish' in sentiment_label:
            sentiment_color = '#ef4444'
            sentiment_bg = '#fee2e2'
        else:
            sentiment_color = '#6b7280'
            sentiment_bg = '#f3f4f6'

        news_items.append(
            html.Div([
                html.Div([
                    html.A(
                        article['title'],
                        href=article['url'],
                        target='_blank',
                        style={'fontSize': '16px', 'fontWeight': '600', 'color': '#1f2937',
                               'textDecoration': 'none', 'display': 'block', 'marginBottom': '8px'}
                    ),
                    html.P(article['summary'][:200] + '...' if len(article['summary']) > 200 else article['summary'],
                           style={'fontSize': '14px', 'color': '#6b7280', 'marginBottom': '12px', 'lineHeight': '1.5'}),
                    html.Div([
                        html.Span(article['source'],
                                  style={'fontSize': '12px', 'color': '#9ca3af', 'marginRight': '15px'}),
                        html.Span(time_str,
                                  style={'fontSize': '12px', 'color': '#9ca3af', 'marginRight': '15px'}),
                        html.Span(f"{sentiment_label} ({article['sentiment_score']:.3f})",
                                  style={'fontSize': '12px', 'fontWeight': '600', 'padding': '4px 8px',
                                         'borderRadius': '4px', 'backgroundColor': sentiment_bg,
                                         'color': sentiment_color}),
                    ]),
                ], style={'flex': '1'}),

                # Image thumbnail if available
                html.Div([
                             html.Img(src=article.get('banner_image', ''),
                                      style={'width': '140px', 'height': '90px', 'objectFit': 'cover',
                                             'borderRadius': '6px'})
                         ] if article.get('banner_image') else [], style={'marginLeft': '20px'})

            ], style={'padding': '20px', 'borderBottom': '1px solid #e5e7eb',
                      'display': 'flex', 'alignItems': 'flex-start',
                      'transition': 'background-color 0.2s'},
                className='news-item')
        )

    return html.Div(news_items, style={'border': '1px solid #e5e7eb', 'borderRadius': '8px'})


def render_trade_recommendation(float_category, rotation_hot, rvol_hot, sentiment_metrics):
    """Final trade recommendation based on all factors"""

    # Score the trade (0-10)
    score = 0
    factors = []

    # Float analysis (0-3 points)
    if float_category == 'Low Float':
        score += 3
        factors.append('✓ Low float - high volatility potential')
    elif float_category == 'Medium Float':
        score += 2
        factors.append('✓ Medium float - good balance')

    else:
        score += 1
        factors.append('⚠️ High float - harder to move')

    # Volume analysis (0-4 points)
    if rotation_hot and rvol_hot:
        score += 4
        factors.append('✓ Excellent volume - high float rotation AND relative volume')
    elif rotation_hot or rvol_hot:
        score += 2
        factors.append('✓ Good volume activity')
    else:
        factors.append('⚠️ Low volume activity')

    # Sentiment analysis (0-3 points)
    if sentiment_metrics['total_articles'] > 0:
        if sentiment_metrics['overall_sentiment'] == 'Bullish':
            if sentiment_metrics['sentiment_strength'] == 'Strong':
                score += 3
                factors.append('✓ Strong bullish sentiment in news')
            else:
                score += 2
                factors.append('✓ Moderate bullish sentiment')
        elif sentiment_metrics['overall_sentiment'] == 'Bearish':
            factors.append('⚠️ Bearish sentiment - proceed with caution')
        else:
            score += 1
            factors.append('○ Neutral sentiment')
    else:
        factors.append('○ No recent news data')

    # Determine recommendation
    if score >= 8:
        recommendation = '🟢 STRONG BUY'
        rec_text = 'Excellent trade candidate - Multiple positive signals align'
        rec_color = '#10b981'
        rec_bg = '#d1fae5'
    elif score >= 6:
        recommendation = '🟡 GOOD CANDIDATE'
        rec_text = 'Decent trade setup - Consider entry with tight stops'
        rec_color = '#f59e0b'
        rec_bg = '#fef3c7'
    elif score >= 4:
        recommendation = '🟠 MARGINAL'
        rec_text = 'Mixed signals - Wait for better confirmation'
        rec_color = '#fb923c'
        rec_bg = '#fed7aa'
    else:
        recommendation = '🔴 AVOID'
        rec_text = 'Weak setup - Look for better opportunities'
        rec_color = '#ef4444'
        rec_bg = '#fee2e2'

    return html.Div([
        html.H2("🎯 Trade Recommendation", style={'marginBottom': '20px', 'color': '#1f2937'}),

        # Score bar
        html.Div([
            html.P("Trade Score", style={'fontSize': '14px', 'color': '#6b7280', 'marginBottom': '10px'}),
            html.Div([
                html.Div([
                    html.Div(style={
                        'width': f'{(score / 10) * 100}%',
                        'height': '100%',
                        'backgroundColor': rec_color,
                        'borderRadius': '8px',
                        'transition': 'width 0.5s ease'
                    })
                ], style={'width': '100%', 'height': '30px', 'backgroundColor': '#e5e7eb',
                          'borderRadius': '8px', 'overflow': 'hidden', 'marginBottom': '8px'}),
                html.P(f"{score}/10 points",
                       style={'fontSize': '16px', 'fontWeight': '600', 'color': rec_color, 'textAlign': 'center'})
            ])
        ], style={'marginBottom': '25px'}),

        # Recommendation banner
        html.Div([
            html.H3(recommendation,
                    style={'margin': '0', 'fontSize': '32px', 'fontWeight': '700', 'color': rec_color,
                           'textAlign': 'center', 'marginBottom': '10px'}),
            html.P(rec_text,
                   style={'margin': '0', 'fontSize': '16px', 'color': '#1f2937', 'textAlign': 'center'}),
        ], style={'backgroundColor': rec_bg, 'padding': '30px', 'borderRadius': '8px',
                  'border': f'2px solid {rec_color}', 'marginBottom': '25px'}),

        # Factors breakdown
        html.Div([
            html.H4("Analysis Factors:", style={'marginBottom': '15px', 'color': '#1f2937'}),
            html.Ul([
                html.Li(factor, style={'marginBottom': '8px', 'fontSize': '14px', 'color': '#4b5563'})
                for factor in factors
            ], style={'paddingLeft': '25px', 'margin': '0'}),
        ], style={'backgroundColor': '#f9fafb', 'padding': '20px', 'borderRadius': '8px',
                  'border': '1px solid #e5e7eb'}),

    ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '8px',
              'border': '1px solid #e5e7eb'})


