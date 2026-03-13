from flask import Flask, render_template, request
import yfinance as yf
import plotly.express as px
import plotly.io as pio

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def index():
    ticker = request.args.get('ticker', 'BBCA.JK').upper()
    if ".JK" not in ticker:
        ticker += ".JK"
        
    avg_price = request.args.get('avg_price', type=float, default=0)
    lots = request.args.get('lots', type=int, default=0)

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        
        if df.empty:
            return f"Ticker {ticker} tidak ditemukan. Gunakan kode seperti BBRI, TLKM, atau ASII."

        current_price = df['Close'].iloc[-1]
        
        # Logika Kalkulator
        profit_loss = 0
        status_cuan = "Netral"
        if avg_price > 0 and lots > 0:
            profit_loss = (current_price - avg_price) * (lots * 100)
            status_cuan = "CUAN" if profit_loss > 0 else "BONCOS"

        # Grafik Plotly dengan warna Cyan
        fig = px.area(df, x=df.index, y='Close', 
                     title=f'Market Performance: {ticker}',
                     labels={'Close': 'Price (IDR)', 'Date': 'Date'})
        
        fig.update_traces(line_color='#22d3ee', fillcolor='rgba(34, 211, 238, 0.1)')
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="#cbd5e1",
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        graph_html = pio.to_html(fig, full_html=False, config={'displayModeBar': False})
        
        return render_template('index.html', 
                               plot=graph_html, 
                               ticker=ticker, 
                               current_price=current_price,
                               profit_loss=profit_loss,
                               status_cuan=status_cuan,
                               avg_price=avg_price,
                               lots=lots)
    
    except Exception as e:
        return f"System Error: {str(e)}"

app = app

if __name__ == '__main__':
    app.run(debug=True)