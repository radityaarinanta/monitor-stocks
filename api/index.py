from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def index():
    ticker = request.args.get('ticker', 'BBCA.JK').upper()
    if ".JK" not in ticker: ticker += ".JK"
    
    avg_price = request.args.get('avg_price', type=float, default=0)
    lots = request.args.get('lots', type=int, default=0)

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")
        
        if df.empty:
            return f"Kesalahan: Data untuk {ticker} tidak ditemukan."

        current_price = df['Close'].iloc[-1]
        
        # Analisis Teknikal
        df['MA20'] = df['Close'].rolling(window=20).mean()
        ma20_last = df['MA20'].iloc[-1]

        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        current_rsi = df['RSI'].iloc[-1]

        # Verdict
        if current_rsi < 30:
            rekomendasi, warna_rekom = "OVERSOLD (Potensi Rebound)", "bg-success"
        elif current_rsi > 70:
            rekomendasi, warna_rekom = "OVERBOUGHT (Hati-hati Koreksi)", "bg-danger"
        elif current_price > ma20_last:
            rekomendasi, warna_rekom = "UPTREND (Kuat)", "bg-info"
        else:
            rekomendasi, warna_rekom = "DOWNTREND (Lemah)", "bg-secondary"

        # Kalkulator Profit
        profit_loss = 0
        status_cuan = "Netral"
        if avg_price > 0 and lots > 0:
            profit_loss = (current_price - avg_price) * (lots * 100)
            status_cuan = "CUAN" if profit_loss > 0 else "BONCOS"

        # Berita
        raw_news = stock.news
        news_data = []
        if raw_news:
            for n in raw_news[:4]:
                news_data.append({
                    'title': n.get('title', 'Judul Tidak Tersedia'),
                    'link': n.get('link', '#'),
                    'publisher': n.get('publisher', 'Sumber Anonim')
                })

        # Grafik
        df_plot = df.tail(30)
        fig = px.area(df_plot, x=df_plot.index, y=['Close', 'MA20'], 
                     title=f'Analisis Market: {ticker}',
                     color_discrete_map={'Close': '#22d3ee', 'MA20': '#f59e0b'})
        
        fig.update_layout(
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color="#cbd5e1",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        graph_html = pio.to_html(fig, full_html=False, config={'displayModeBar': False})
        
        return render_template('index.html', 
                               plot=graph_html, ticker=ticker, 
                               current_price=current_price, profit_loss=profit_loss,
                               status_cuan=status_cuan, avg_price=avg_price, lots=lots,
                               rekomendasi=rekomendasi, warna_rekom=warna_rekom,
                               current_rsi=current_rsi, ma20_last=ma20_last,
                               news=news_data)
    
    except Exception as e:
        return f"System Error: {str(e)}"

app = app

if __name__ == '__main__':
    app.run(debug=True)