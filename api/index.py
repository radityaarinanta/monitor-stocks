from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        # 1. Scanner Logic (Tetap Ada)
        bullish_stocks = []
        for symbol in WATCHLIST:
            s_data = yf.Ticker(symbol).history(period="1mo")
            if not s_data.empty:
                curr = s_data['Close'].iloc[-1]
                ma20 = s_data['Close'].rolling(window=20).mean().iloc[-1]
                if curr > ma20:
                    prev = s_data['Close'].iloc[-2]
                    change = ((curr - prev) / prev) * 100
                    bullish_stocks.append({'symbol': symbol.replace('.JK', ''), 'change': change})

        # 2. Main Analytics Core
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")
        info = stock.info
        current_price = df['Close'].iloc[-1]
        
        # --- PERHITUNGAN INDIKATOR (MA, RSI, BOLLINGER BANDS) ---
        # Moving Average
        df['MA20'] = df['Close'].rolling(window=20).mean()
        
        # Bollinger Bands (Standard Deviation 2)
        df['STD'] = df['Close'].rolling(window=20).std()
        df['Upper_Band'] = df['MA20'] + (df['STD'] * 2)
        df['Lower_Band'] = df['MA20'] - (df['STD'] * 2)

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        current_rsi = df['RSI'].iloc[-1]

        # Strength Score (0-100)
        strength = 50
        if current_price > df['MA20'].iloc[-1]: strength += 20
        if current_price < df['Lower_Band'].iloc[-1]: strength += 15 # Overextended down
        if current_rsi < 30: strength += 15
        if current_rsi > 70: strength -= 20

        # --- QUICK INSIGHT LOGIC ---
        if current_price > df['Upper_Band'].iloc[-1]:
            insight = "Harga menembus Batas Atas (Bollinger). Sangat kuat tapi rawan koreksi."
        elif current_price < df['Lower_Band'].iloc[-1]:
            insight = "Harga menyentuh Batas Bawah. Ada potensi pantulan naik (rebound)."
        elif current_rsi < 30:
            insight = "Indikator RSI menunjukkan harga sudah sangat murah (Oversold)."
        else:
            insight = "Harga bergerak stabil di dalam rentang normal."

        # Fundamental & News
        fundamental = {'pe': info.get('trailingPE', 'N/A'), 'eps': info.get('trailingEps', 'N/A'), 
                       'div': (info.get('dividendYield', 0) or 0) * 100, 'cap': (info.get('marketCap', 0) or 0) / 1e12}
        news_data = [{'title': n.get('title'), 'link': n.get('link'), 'pub': n.get('publisher')} for n in stock.news[:3]]

        # --- GRAFIK ADVANCED (Plotly Graph Objects) ---
        fig = go.Figure()
        # Area Bollinger
        fig.add_trace(go.Scatter(x=df.index[-30:], y=df['Upper_Band'][-30:], line=dict(color='rgba(255,255,255,0)'), showlegend=False))
        fig.add_trace(go.Scatter(x=df.index[-30:], y=df['Lower_Band'][-30:], fill='tonexty', fillcolor='rgba(34, 211, 238, 0.05)', line=dict(color='rgba(255,255,255,0)'), name='Bollinger Bands'))
        # Garis Harga & MA
        fig.add_trace(go.Scatter(x=df.index[-30:], y=df['Close'][-30:], line=dict(color='#22d3ee', width=3), name='Harga'))
        fig.add_trace(go.Scatter(x=df.index[-30:], y=df['MA20'][-30:], line=dict(color='#f59e0b', width=2, dash='dash'), name='MA20'))
        
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#f8fafc", margin=dict(l=0,r=0,t=0,b=0), height=400)
        graph_html = pio.to_html(fig, full_html=False, config={'displayModeBar': False})
        
        return render_template('index.html', plot=graph_html, ticker=ticker, current_price=current_price, 
                               profit_loss=(current_price-avg_price)*(lots*100) if avg_price>0 else 0,
                               rekomendasi="BULLISH" if strength > 50 else "BEARISH", 
                               warna_rekom="bg-info" if strength > 50 else "bg-secondary", 
                               current_rsi=current_rsi, strength=strength, news=news_data, fundamental=fundamental, 
                               bullish_scanner=bullish_stocks, insight=insight, avg_price=avg_price, lots=lots)
    except Exception as e:
        return f"Error: {e}"

app = app

if __name__ == '__main__':
    app.run(debug=True)