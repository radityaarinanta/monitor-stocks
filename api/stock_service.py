import os
import sys
import pandas as pd
import yfinance as yf

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

try:
    from api.services.market_data import (
        WATCHLIST,
        normalize_ticker,
        fetch_google_news_rss,
        parse_news,
        get_fundamental_data,
        scan_bullish_stocks,
    )
    from api.services.indicators import (
        calculate_technical_indicators,
        calculate_trend_strength,
        calc_trade_setup,
    )
    from api.services.bandarmologi import (
        get_broker_summary,
        calc_foreign_flow,
    )
    from api.services.chart_builder import (
        create_stock_chart,
    )
    from api.services.dss_engine import (
        generate_dss_insights,
        generate_portfolio_decision,
    )
except (ImportError, ModuleNotFoundError):
    from services.market_data import (
        WATCHLIST,
        normalize_ticker,
        fetch_google_news_rss,
        parse_news,
        get_fundamental_data,
        scan_bullish_stocks,
    )
    from services.indicators import (
        calculate_technical_indicators,
        calculate_trend_strength,
        calc_trade_setup,
    )
    from services.bandarmologi import (
        get_broker_summary,
        calc_foreign_flow,
    )
    from services.chart_builder import (
        create_stock_chart,
    )
    from services.dss_engine import (
        generate_dss_insights,
        generate_portfolio_decision,
    )


def analyze_stock(target_symbol: str, raw_ticker_input: str, avg_price: float = 0.0, lots: int = 0) -> dict:
    stock = yf.Ticker(target_symbol)
    df = stock.history(period="6mo")

    ticker_display = raw_ticker_input.upper().replace('.JK', '')

    if df.empty and target_symbol.endswith('.JK'):
        fallback_symbol = target_symbol.replace('.JK', '')
        stock_fallback = yf.Ticker(fallback_symbol)
        df_fallback = stock_fallback.history(period="6mo")
        if not df_fallback.empty:
            stock = stock_fallback
            df = df_fallback
            target_symbol = fallback_symbol
            ticker_display = fallback_symbol

    if df.empty or len(df) < 2:
        return {
            'success': False,
            'error_message': f"Data pasar untuk instrumen '{raw_ticker_input}' tidak ditemukan atau sedang tidak diperdagangkan.",
            'ticker': raw_ticker_input.upper(),
            'ticker_display': ticker_display
        }

    current_price = float(df['Close'].iloc[-1])
    prev_price = float(df['Close'].iloc[-2])
    day_change = ((current_price - prev_price) / prev_price) * 100
    price_change_nominal = current_price - prev_price

    df = calculate_technical_indicators(df)

    latest_rsi = float(df['RSI'].iloc[-1]) if pd.notnull(df['RSI'].iloc[-1]) else 50.0
    latest_ma20 = float(df['MA20'].iloc[-1]) if pd.notnull(df['MA20'].iloc[-1]) else current_price
    latest_ma50 = float(df['MA50'].iloc[-1]) if 'MA50' in df.columns and pd.notnull(df['MA50'].iloc[-1]) else current_price
    latest_upper = float(df['Upper_Band'].iloc[-1]) if pd.notnull(df['Upper_Band'].iloc[-1]) else current_price * 1.05
    latest_lower = float(df['Lower_Band'].iloc[-1]) if pd.notnull(df['Lower_Band'].iloc[-1]) else current_price * 0.95

    strength, rekomendasi, badge_style, strength_badge_class, strength_bar_class = calculate_trend_strength(
        current_price, latest_ma20, latest_rsi, latest_upper, latest_lower
    )

    insight_data = generate_dss_insights(
        df, current_price, latest_ma20, latest_ma50, latest_rsi, latest_upper, latest_lower
    )

    broker_summary = get_broker_summary(df, ticker_display, current_price)
    trade_setup = calc_trade_setup(df, current_price)
    foreign_flow = calc_foreign_flow(df, ticker_display)

    portfolio, portfolio_advice, portfolio_action_tag = generate_portfolio_decision(
        avg_price, lots, current_price, latest_rsi, latest_upper, latest_lower, latest_ma20, latest_ma50, broker_summary, trade_setup
    )

    insight_data['portfolio_advice'] = portfolio_advice
    insight_data['portfolio_action_tag'] = portfolio_action_tag

    info = stock.info if hasattr(stock, 'info') else {}
    fundamental = get_fundamental_data(info)
    news_data = parse_news(stock, ticker_display=ticker_display, company_name=fundamental.get('company_name', ''))

    chart_html = create_stock_chart(df, ticker_display)

    return {
        'success': True,
        'plot': chart_html,
        'ticker': target_symbol,
        'ticker_display': ticker_display,
        'current_price': current_price,
        'day_change': day_change,
        'price_change_nominal': price_change_nominal,
        'rekomendasi': rekomendasi,
        'badge_style': badge_style,
        'current_rsi': latest_rsi,
        'strength': strength,
        'strength_badge_class': strength_badge_class,
        'strength_bar_class': strength_bar_class,
        'news': news_data,
        'fundamental': fundamental,
        'insight': insight_data,
        'portfolio': portfolio,
        'broker_summary': broker_summary,
        'trade_setup': trade_setup,
        'foreign_flow': foreign_flow,
        'error_message': None
    }
