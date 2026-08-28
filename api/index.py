import os
from flask import Flask, render_template, request, send_from_directory

try:
    from api.stock_service import normalize_ticker, scan_bullish_stocks, analyze_stock
except ImportError:
    from stock_service import normalize_ticker, scan_bullish_stocks, analyze_stock

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


@app.route('/')
@app.route('/index')
@app.route('/api')
@app.route('/api/index')
@app.route('/api/index.py')
def index():
    raw_ticker_input = request.args.get('ticker', 'BBCA').strip()
    target_symbol, ticker_display = normalize_ticker(raw_ticker_input)
    
    avg_price = request.args.get('avg_price', type=float, default=0.0) or 0.0
    lots = request.args.get('lots', type=int, default=0) or 0

    bullish_stocks = scan_bullish_stocks()

    try:
        analysis = analyze_stock(target_symbol, raw_ticker_input, avg_price=avg_price, lots=lots)
        
        if not analysis.get('success', True):
            return render_template(
                'index.html',
                error_message=analysis.get('error_message'),
                ticker=raw_ticker_input.upper(),
                ticker_display=ticker_display,
                bullish_scanner=bullish_stocks,
                avg_price=avg_price,
                lots=lots
            )

        return render_template(
            'index.html',
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
            error_message=None
        )

    except Exception as e:
        return render_template(
            'index.html',
            error_message=f"Terjadi kesalahan saat memproses data: {str(e)}",
            ticker=raw_ticker_input.upper(),
            ticker_display=ticker_display,
            bullish_scanner=bullish_stocks,
            avg_price=avg_price,
            lots=lots
        )


@app.errorhandler(404)
def page_not_found(e):
    return index()


if __name__ == '__main__':
    app.run(debug=True, port=5000)