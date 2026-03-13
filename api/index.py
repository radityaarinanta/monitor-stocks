from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def index():
    # Ambil parameter input
    ticker = request.args.get('ticker', 'BBCA.JK').upper()
    if ".JK" not in ticker: ticker += ".JK"
    
    avg_price = request.args.get('avg_price', type=float, default=0)
    lots = request.args.get('lots', type=int, default=0)

    try:
        stock = yf.Ticker(ticker)
        # Ambil data 3 bulan untuk akurasi MA20 dan RSI
        df = stock.history(period="3mo")
        
        if df.empty:
            return f"Kesalahan: Data untuk {ticker} tidak ditemukan."

        current_price = df['Close'].iloc[-1]
        
        # --- LOGIKA ANALISIS TEKNIKAL ---
        # 1. Moving Average 20 Hari
        df['MA20'] = df['Close'].rolling(window=20).mean()
        ma20_last = df['MA20'].iloc[-1]

        # 2. RSI 14 Hari
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        current_rsi = df['RSI'].iloc[-1]

        # 3. Verdict Analisis
        if current_rsi < 30:
            rekomendasi = "OVERSOLD (Potensi Rebound)"
            warna_rekom = "bg-success"
        elif current_rsi > 70:
            rekomendasi = "OVERBOUGHT (Hati-hati Koreksi)"
            warna_rekom = "bg-danger"
        elif current_price > ma20_last:
            rekomendasi = "UPTREND (Bullish)"
            warna_rekom = "bg-info"
        else:
            rekomendasi = "DOWNTREND (Bearish)"
            warna_rekom = "bg-secondary"

        # --- KALKULATOR PROFIT ---
        profit_loss = 0
        status_cuan = "Netral"
        if avg_price > 0 and lots > 0:
            profit_loss = (current_price - avg_price) * (lots * 100)
            status_cuan = "CUAN" if profit_loss > 0 else "BONCOS"

        # --- VISUALISASI GRAFIK ---
        df_plot = df.tail(30) # Tampilkan 30 hari terakhir di chart
        fig = px.area(df_plot, x=df_plot.index, y=['Close', 'MA20'], 
                     title=f'Market Analysis: {ticker}',
                     color_discrete_map={'Close': '#22d3ee', 'MA20': '#f59e0b'})
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        graph_html = pio.to_html(fig, full_html=False, config={'displayModeBar': False})
        
        return render_template('index.html', 
                               plot=graph_html, ticker=ticker, 
                               current_price=current_price, profit_loss=profit_loss,
                               status_cuan=status_cuan, avg_price=avg_price, lots=lots,
                               rekomendasi=rekomendasi, warna_rekom=warna_rekom,
                               current_rsi=current_rsi, ma20_last=ma20_last)
    
    except Exception as e:
        return f"System Error: {str(e)}"

# Jalankan Flask app
app = app

if __name__ == '__main__':
    app.run(debug=True)