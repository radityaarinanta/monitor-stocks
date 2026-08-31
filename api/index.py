import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
API_DIR = os.path.dirname(os.path.abspath(__file__))
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from flask import Flask, render_template, request, send_from_directory, jsonify

try:
    from api.stock_service import normalize_ticker, scan_bullish_stocks, analyze_stock, get_screener_data
except (ImportError, ModuleNotFoundError):
    from stock_service import normalize_ticker, scan_bullish_stocks, analyze_stock, get_screener_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    static_url_path='/static'
)


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)


@app.route('/favicon.ico')
def favicon():
    img_dir = os.path.join(STATIC_DIR, 'img')
    if os.path.exists(img_dir):
        if os.path.exists(os.path.join(img_dir, 'favicon.png')):
            return send_from_directory(img_dir, 'favicon.png')
        for ext in ['png', 'svg', 'ico', 'webp', 'jpg']:
            filename = f"logo.{ext}"
            if os.path.exists(os.path.join(img_dir, filename)):
                return send_from_directory(img_dir, filename)
    return ('', 204)


@app.context_processor
def inject_custom_logo():
    img_dir = os.path.join(STATIC_DIR, 'img')
    custom_logo = None
    custom_favicon = None
    if os.path.exists(img_dir):
        if os.path.exists(os.path.join(img_dir, 'favicon.png')):
            custom_favicon = 'img/favicon.png'
        for ext in ['svg', 'png', 'webp', 'jpg', 'jpeg']:
            filename = f"logo.{ext}"
            if os.path.exists(os.path.join(img_dir, filename)):
                custom_logo = f"img/{filename}"
                if not custom_favicon:
                    custom_favicon = f"img/{filename}"
                break
    return {'custom_logo': custom_logo, 'custom_favicon': custom_favicon}


@app.route('/')
@app.route('/index')
@app.route('/api')
@app.route('/api/index')
@app.route('/api/index.py')
def index():
    bullish_stocks = scan_bullish_stocks()

    raw_ticker_param = request.args.get('ticker')
    if raw_ticker_param and raw_ticker_param.strip():
        raw_ticker_input = raw_ticker_param.strip()
    else:
        if bullish_stocks and len(bullish_stocks) > 0:
            raw_ticker_input = bullish_stocks[0]['symbol']
        else:
            raw_ticker_input = 'BBCA'

    target_symbol, ticker_display = normalize_ticker(raw_ticker_input)
    
    avg_price = request.args.get('avg_price', type=float, default=0.0) or 0.0
    lots = request.args.get('lots', type=int, default=0) or 0

    try:
        analysis = analyze_stock(target_symbol, raw_ticker_input, avg_price=avg_price, lots=lots)
        
        if not analysis.get('success', True):
            return render_template(
                'index.html',
                active_page='dashboard',
                error_message=analysis.get('error_message'),
                ticker=raw_ticker_input.upper(),
                ticker_display=ticker_display,
                bullish_scanner=bullish_stocks,
                avg_price=avg_price,
                lots=lots
            )

        return render_template(
            'index.html',
            active_page='dashboard',
            plot=analysis['plot'],
            ticker=analysis['ticker'],
            ticker_display=analysis['ticker_display'],
            current_price=analysis['current_price'],
            day_change=analysis['day_change'],
            price_change_nominal=analysis.get('price_change_nominal', 0),
            rekomendasi=analysis['rekomendasi'],
            badge_style=analysis.get('badge_style', 'signal-neutral'),
            current_rsi=analysis['current_rsi'],
            strength=analysis['strength'],
            strength_badge_class=analysis.get('strength_badge_class', 'bg-secondary bg-opacity-10 text-secondary border border-color'),
            strength_bar_class=analysis.get('strength_bar_class', 'bg-warning'),
            news=analysis['news'],
            fundamental=analysis['fundamental'],
            bullish_scanner=bullish_stocks,
            insight=analysis['insight'],
            avg_price=avg_price,
            lots=lots,
            portfolio=analysis['portfolio'],
            broker_summary=analysis.get('broker_summary'),
            trade_setup=analysis.get('trade_setup'),
            foreign_flow=analysis.get('foreign_flow'),
            condition_detail=analysis.get('condition_detail'),
            error_message=None
        )

    except Exception as e:
        return render_template(
            'index.html',
            active_page='dashboard',
            error_message=f"Terjadi kesalahan saat memproses data: {str(e)}",
            ticker=raw_ticker_input.upper(),
            ticker_display=ticker_display,
            bullish_scanner=bullish_stocks,
            avg_price=avg_price,
            lots=lots
        )


@app.route('/screener')
def screener_page():
    stocks = get_screener_data()
    return render_template('screener.html', stocks=stocks, active_page='screener')


@app.route('/api/screener-data')
def api_screener_data():
    force = request.args.get('refresh', '0') == '1'
    stocks = get_screener_data(force_refresh=force)
    return jsonify({'success': True, 'count': len(stocks), 'data': stocks})


@app.errorhandler(404)
def page_not_found(e):
    return index()


if __name__ == '__main__':
    app.run(debug=True, port=5000)