from flask import Flask, render_template, request
import yfinance as yf
import plotly.express as px
import plotly.io as pio

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def index():
    # Mengambil input kode saham dari form (default: BBCA.JK)
    ticker = request.args.get('ticker', 'BBCA.JK').upper()
    if ".JK" not in ticker:
        ticker += ".JK"

    try:
        stock = yf.Ticker(ticker)
        # Ambil data 1 bulan terakhir
        df = stock.history(period="1mo")
        
        if df.empty:
            return f"Data untuk {ticker} tidak ditemukan. Pastikan kode benar (contoh: ASII atau TLKM)."

        # Membuat grafik garis menggunakan Plotly
        fig = px.line(df, x=df.index, y='Close', 
                     title=f'Harga Penutupan {ticker} (1 Bulan Terakhir)',
                     labels={'Close': 'Harga (IDR)', 'Date': 'Tanggal'})
        
        # Pengaturan agar grafik responsif
        fig.update_layout(template="plotly_dark", autosize=True)
        
        graph_html = pio.to_html(fig, full_html=False)
        return render_template('index.html', plot=graph_html, ticker=ticker)
    
    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}"

# Penting agar Vercel mengenali app Flask
app = app

if __name__ == '__main__':
    app.run(debug=True)