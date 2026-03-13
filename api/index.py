from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__, template_folder='../templates')

WATCHLIST = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK', 'GOTO.JK', 'BBNI.JK', 'UNVR.JK', 'ICBP.JK', 'AMRT.JK']

@app.route('/')
def index():
    ticker = request.args.get('ticker', 'BBCA.JK').upper()
    if ".JK" not in ticker: ticker += ".JK"
    
    avg_price = request.args.get('avg_price', type=float, default=0)
    lots = request.args.get('lots', type=int, default=0)

    try:
        # 1. Scanner Logic
        bullish_stocks = []
        for symbol in WATCHLIST:
            s_data = yf.Ticker(symbol).history(period="1mo")
            if not s_data.empty:
                curr = s_data['Close'].iloc[-1]
                ma20 = s_data['Close'].rolling(window=20).mean().iloc[-1]
                if curr > ma20:
                    prev = s_data['Close'].iloc[-2]
                    change = ((curr - prev) / prev) * 100
                    bullish_stocks.append({'symbol': symbol.replace('.JK', ''), 'price': curr, 'change': change})

        # 2. Main Data Extraction
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")
        info = stock.info
        current_price = df['Close'].iloc[-1]
        
        # Technical Calc
        df['MA20'] = df['Close'].rolling(window=20).mean()
        ma20_last = df['MA20'].iloc[-1]

        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        current_rsi = df['RSI'].iloc[-1]

        # --- LOGIKA QUICK INSIGHT (FITUR GACOR BARU) ---
        if current_rsi < 30 and current_price > ma20_last:
            insight = "Sangat Bullish! Harga mulai naik dari area murah. Peluang beli tinggi."
        elif current_rsi < 30:
            insight = "Harga sudah murah (Oversold), tapi tren masih turun. Pantau tanda-tanda pembalikan arah."
        elif current_rsi > 70:
            insight = "Waspada! Harga sudah terlalu mahal (Overbought). Potensi aksi ambil untung (Profit Taking)."
        elif current_price > ma20_last:
            insight = "Tren Positif. Harga bergerak stabil di atas rata-rata 20 hari."
        else:
            insight = "Tren Negatif. Harga masih tertekan di bawah rata-rata. Wait and see."

        # Verdict
        if current_rsi < 30: rek, warna = "STRONG BUY", "bg-success"
        elif current_rsi > 70: rek, warna = "STRONG SELL", "bg-danger"
        elif current_price > ma20_last: rek, warna = "BULLISH", "bg-info"
        else: rek, warna = "BEARISH", "bg-secondary"

        # News & Fundamental
        fundamental = {
            'pe': info.get('trailingPE', 'N/A'),
            'eps': info.get('trailingEps', 'N/A'),
            'div': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            'cap': info.get('marketCap', 0) / 1e12
        }
        news_data = [{'title': n.get('title'), 'link': n.get('link'), 'pub': n.get('publisher')} for n in stock.news[:3]]

        # Chart
        fig = px.area(df.tail(30), x=df.tail(30).index, y=['Close', 'MA20'], color_discrete_map={'Close': '#22d3ee', 'MA20': '#f59e0b'})
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#f8fafc")
        graph_html = pio.to_html(fig, full_html=False, config={'displayModeBar': False})
        
        return render_template('index.html', plot=graph_html, ticker=ticker, current_price=current_price, 
                               profit_loss=(current_price - avg_price) * (lots * 100) if avg_price > 0 else 0,
                               avg_price=avg_price, lots=lots, rekomendasi=rek, warna_rekom=warna, 
                               current_rsi=current_rsi, ma20_last=ma20_last, news=news_data, 
                               fundamental=fundamental, bullish_scanner=bullish_stocks, insight=insight)
    except Exception as e:
        return f"Error: {e}"

app = app

if __name__ == '__main__':
    app.run(debug=True)