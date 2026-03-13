# 📈 StockPulse Elite Pro (V4.0) - Advanced AI Stock Analytics

**StockPulse** adalah platform *Decision Support System* (DSS) canggih berbasis web yang dirancang khusus untuk memantau pasar saham IHSG secara real-time. Versi **Elite Pro** ini mengintegrasikan analisis multi-indikator teknikal, data fundamental, dan algoritma *Quick Insight* untuk membantu investor mengambil keputusan berbasis data.

---

## 🚀 Fitur Unggulan (Elite Version)

* **Multi-Indicator Analytics**: Menggabungkan tiga indikator teknikal utama:
    * **RSI (Relative Strength Index)**: Mendeteksi area Jenuh Beli (Overbought) dan Jenuh Jual (Oversold).
    * **MA20 (Moving Average)**: Menentukan arah tren harga rata-rata 20 hari.
    * **Bollinger Bands**: Mengukur volatilitas harga dan menentukan batas atas (resisten) serta batas bawah (support).
* **Trend Strength Meter**: Meteran visual (0-100%) yang menghitung kekuatan akumulasi harga secara real-time.
* **AI Quick Insight**: Interpretasi data otomatis ke dalam bahasa manusia untuk memberikan saran cepat (Beli/Jual/Wait).
* **Bullish Trend Scanner**: Pemindaian otomatis terhadap 10 saham *Blue Chip* IHSG yang sedang dalam fase *Uptrend*.
* **Fundamental Scoreboard**: Ringkasan kesehatan finansial perusahaan (P/E Ratio, EPS, Div Yield, Market Cap).
* **Enterprise UI**: Desain *Glassmorphism* modern dengan kontras tinggi yang optimal untuk penggunaan jangka panjang (Dark Mode).

---

## 🛠️ Tech Stack

* **Engine**: Python 3.10+ (Flask Framework)
* **Analysis Library**: `yfinance` (Real-time Market Data), `pandas` (Data Manipulation)
* **Visualization**: Plotly Graph Objects (High-Performance Graphs)
* **Frontend**: HTML5, CSS3, Bootstrap 5 (Responsive Design)
* **Hosting**: Vercel (Serverless Edge Functions)

---

## 📖 Panduan Teknis Indikator

1.  **Bollinger Bands**: Jika harga menyentuh garis bawah transparan, ini sering menjadi sinyal **rebound**. Jika menembus garis atas, waspadai koreksi harga.
2.  **RSI (14)**: Fokus pada angka **30 (Beli)** dan **70 (Jual)**.
3.  **Trend Strength**: Skor di atas 50% menunjukkan dominasi pembeli (Bullish), di bawah 50% menunjukkan dominasi penjual (Bearish).

---

