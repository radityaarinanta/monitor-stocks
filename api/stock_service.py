import math
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio

# Watchlist Saham Blue-Chip Pilihan IHSG untuk Bullish Scanner (Fundamental & Likuiditas Kuat)
WATCHLIST = [
    'BBCA.JK',  # Bank Central Asia (Kapitalisasi Terbesar)
    'BBRI.JK',  # Bank Rakyat Indonesia (Perbankan Mikro & Dividen)
    'BMRI.JK',  # Bank Mandiri (Perbankan Korporasi)
    'BBNI.JK',  # Bank Negara Indonesia (Perbankan)
    'TLKM.JK',  # Telkom Indonesia (Telekomunikasi)
    'ASII.JK',  # Astra International (Konglomerasi & Otomotif)
    'ICBP.JK',  # Indofood CBP (Consumer Goods)
    'INDF.JK',  # Indofood Sukses Makmur (Consumer Goods)
    'AMRT.JK',  # Sumber Alfaria Trijaya / Alfamart (Retail)
    'UNTR.JK',  # United Tractors (Alat Berat & Tambang)
    'KLBF.JK',  # Kalbe Farma (Farmasi & Kesehatan)
    'ADRO.JK',  # Adaro Energy (Energi & Dividen)
]


def normalize_ticker(raw_ticker: str) -> tuple[str, str]:
    """
    Normalisasi ticker input:
    - Jika kosong: default ke BBCA.JK
    - Jika sudah ada titik (misal BBCA.JK) atau strip (misal BTC-USD): gunakan langsung
    - Jika huruf alfabet <= 4 karakter: prioritaskan .JK (IDX)
    Mengembalikan (symbol_with_suffix, display_name)
    """
    raw = (raw_ticker or '').strip().upper()
    if not raw:
        return 'BBCA.JK', 'BBCA'
    
    if '.' in raw or '-' in raw or '^' in raw:
        display = raw.replace('.JK', '')
        return raw, display
    
    # Saham Indonesia umumnya 4 huruf alfabet
    if len(raw) <= 4 and raw.isalpha():
        return f"{raw}.JK", raw
    
    return raw, raw


def fetch_google_news_rss(query_keyword: str) -> list[dict]:
    """Mengambil berita keuangan terkini via Google News RSS jika yfinance kosong (khususnya saham IHSG/Indonesia)."""
    import urllib.request
    import xml.etree.ElementTree as ET
    import urllib.parse
    
    encoded_q = urllib.parse.quote(f"saham {query_keyword}")
    rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=id&gl=ID&ceid=ID:id"
    req = urllib.request.Request(
        rss_url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    news_items = []
    try:
        with urllib.request.urlopen(req, timeout=4) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('.//item')[:4]:
                raw_title = item.find('title').text or ''
                link = item.find('link').text or '#'
                pub_date = (item.find('pubDate').text or '')
                
                # Ekstraksi judul dan nama media/publisher
                if ' - ' in raw_title:
                    title_part, pub_part = raw_title.rsplit(' - ', 1)
                else:
                    title_part = raw_title
                    pub_part = 'Berita Pasar'
                
                # Format tanggal singkat (misal: 28 Aug 2026)
                time_str = pub_date[5:16] if len(pub_date) >= 16 else pub_date[:10]
                
                news_items.append({
                    'title': title_part.strip(),
                    'link': link,
                    'pub': pub_part.strip(),
                    'time': time_str
                })
    except Exception:
        pass
    return news_items


def parse_news(stock, ticker_display: str = '', company_name: str = '') -> list[dict]:
    """Ekstraksi berita emiten: Prioritas yfinance, dengan pelengkap/fallback Google News RSS untuk saham Indonesia."""
    news_data = []
    try:
        raw_news = stock.news or []
        for n in raw_news[:4]:
            if not isinstance(n, dict):
                continue
            if 'content' in n and isinstance(n['content'], dict):
                content = n['content']
                title = content.get('title')
                link = (
                    content.get('canonicalUrl', {}).get('url')
                    or content.get('clickThroughUrl', {}).get('url')
                    or content.get('previewUrl')
                )
                pub = content.get('provider', {}).get('displayName', 'Market Wire')
                pub_date = content.get('pubDate', '')
            else:
                title = n.get('title')
                link = n.get('link')
                pub = n.get('publisher', 'Market Wire')
                pub_date = ''
            
            if title and link:
                news_data.append({
                    'title': title,
                    'link': link,
                    'pub': pub,
                    'time': pub_date[:10] if pub_date else ''
                })
    except Exception:
        pass

    # Jika berita dari yfinance kurang dari 3 (umum terjadi pada emiten BEI/IHSG), lengkapi dengan Google News RSS
    if len(news_data) < 3 and ticker_display:
        search_query = f"{ticker_display} {company_name}".strip() if company_name else ticker_display
        rss_news = fetch_google_news_rss(search_query)
        for r_item in rss_news:
            if len(news_data) >= 4:
                break
            if not any(r_item['title'].lower() in existing['title'].lower() for existing in news_data):
                news_data.append(r_item)

    return news_data


def get_fundamental_data(info: dict) -> dict:
    """Format metrik fundamental & profil eksekutif perusahaan."""
    if not isinstance(info, dict):
        info = {}
        
    pe_val = info.get('trailingPE') or info.get('forwardPE')
    pe_str = f"{pe_val:.2f}" if isinstance(pe_val, (int, float)) and not math.isnan(pe_val) else "N/A"

    eps_val = info.get('trailingEps') or info.get('forwardEps')
    eps_str = f"{eps_val:,.2f}" if isinstance(eps_val, (int, float)) and not math.isnan(eps_val) else "N/A"

    div_val = info.get('dividendYield')
    if isinstance(div_val, (int, float)) and not math.isnan(div_val):
        div_pct = div_val if div_val > 0.5 else (div_val * 100)
        div_str = f"{div_pct:.2f}%"
    else:
        div_str = "0.00%"

    cap_val = info.get('marketCap')
    if isinstance(cap_val, (int, float)) and cap_val > 0:
        if cap_val >= 1e12:
            cap_str = f"{cap_val / 1e12:,.2f} T"
        elif cap_val >= 1e9:
            cap_str = f"{cap_val / 1e9:,.2f} B"
        elif cap_val >= 1e6:
            cap_str = f"{cap_val / 1e6:,.2f} M"
        else:
            cap_str = f"{cap_val:,.0f}"
    else:
        cap_str = "N/A"

    high_52 = info.get('fiftyTwoWeekHigh')
    low_52 = info.get('fiftyTwoWeekLow')
    if isinstance(high_52, (int, float)) and isinstance(low_52, (int, float)):
        range_52 = f"{low_52:,.0f} - {high_52:,.0f}"
    else:
        range_52 = "N/A"

    vol_val = info.get('volume') or info.get('regularMarketVolume')
    if isinstance(vol_val, (int, float)) and vol_val > 0:
        if vol_val >= 1e6:
            vol_str = f"{vol_val / 1e6:,.1f}M"
        elif vol_val >= 1e3:
            vol_str = f"{vol_val / 1e3:,.1f}K"
        else:
            vol_str = f"{vol_val:,.0f}"
    else:
        vol_str = "N/A"

    # Data profil perusahaan
    sector = info.get('sector') or 'Financials & Enterprise'
    industry = info.get('industry') or 'General Industry'
    website = info.get('website') or ''
    country = info.get('country') or 'Indonesia'
    company_name = info.get('shortName') or info.get('longName') or 'Corporation'
    
    # Ringkasan bisnis
    summary = info.get('longBusinessSummary') or info.get('description') or ''
    if summary and len(summary) > 400:
        summary = summary[:400].rsplit(' ', 1)[0] + '...'

    return {
        'pe': pe_str,
        'eps': eps_str,
        'div': div_str,
        'cap': cap_str,
        'range_52': range_52,
        'volume': vol_str,
        'sector': sector,
        'industry': industry,
        'website': website,
        'country': country,
        'company_name': company_name,
        'summary': summary,
        'currency': info.get('currency', 'IDR')
    }


def scan_bullish_stocks() -> list[dict]:
    """Memindai saham watchlist berfundamental unggul yang sedang berada dalam tren Bullish (Close >= MA20)."""
    bullish_list = []
    for symbol in WATCHLIST:
        try:
            s_data = yf.Ticker(symbol).history(period="1mo")
            if not s_data.empty and len(s_data) >= 2:
                curr = float(s_data['Close'].iloc[-1])
                ma_window = min(20, len(s_data))
                ma_val = float(s_data['Close'].rolling(window=ma_window).mean().iloc[-1])
                prev = float(s_data['Close'].iloc[-2])
                change = ((curr - prev) / prev) * 100
                
                # Filter kriteria:
                # 1. Harga di atas MA20 (Uptrend Momentum)
                # 2. Menghindari saham gocap / non-likuid (harga > 100)
                if curr >= ma_val and curr > 100:
                    bullish_list.append({
                        'symbol': symbol.replace('.JK', ''),
                        'full_symbol': symbol,
                        'price': curr,
                        'change': change,
                        'is_positive': change >= 0
                    })
        except Exception:
            continue
            
    # Urutkan berdasarkan persentase perubahan performa terbaik di atas
    bullish_list.sort(key=lambda x: x['change'], reverse=True)
    return bullish_list[:6]


def create_stock_chart(df: pd.DataFrame, ticker_display: str) -> str:
    """Membuat grafik Candlestick formal & clean (kompatibel dual-mode dark/light)."""
    chart_df = df.iloc[-45:] if len(df) >= 45 else df
    
    fig = go.Figure()

    # 1. Bollinger Bands Area (Subtle institutional fill)
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['Upper_Band'],
        mode='lines',
        line=dict(color='rgba(14, 165, 233, 0.4)', width=1, dash='dot'),
        name='Upper Band (BB)',
        hoverinfo='x+y'
    ))
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['Lower_Band'],
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(14, 165, 233, 0.04)',
        line=dict(color='rgba(14, 165, 233, 0.4)', width=1, dash='dot'),
        name='Lower Band (BB)',
        hoverinfo='x+y'
    ))

    # 2. Candlestick Chart (Crisp Institutional Green/Red)
    fig.add_trace(go.Candlestick(
        x=chart_df.index,
        open=chart_df['Open'],
        high=chart_df['High'],
        low=chart_df['Low'],
        close=chart_df['Close'],
        increasing_line_color='#10b981',
        increasing_fillcolor='#10b981',
        decreasing_line_color='#f43f5e',
        decreasing_fillcolor='#f43f5e',
        name='Price'
    ))

    # 3. MA20 Line (Amber Trendline)
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['MA20'],
        mode='lines',
        line=dict(color='#f59e0b', width=2),
        name='MA20 Trend'
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans, Inter, sans-serif', size=11),
        margin=dict(l=10, r=10, t=20, b=10),
        height=430,
        xaxis=dict(
            rangeslider=dict(visible=False),
            gridcolor='rgba(148, 163, 184, 0.08)',
            type='date',
            tickfont=dict(size=10, family='JetBrains Mono, monospace')
        ),
        yaxis=dict(
            gridcolor='rgba(148, 163, 184, 0.08)',
            side='right',
            tickformat=",",
            tickfont=dict(size=10, family='JetBrains Mono, monospace')
        ),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=10, family='Plus Jakarta Sans, sans-serif')
        )
    )

    return pio.to_html(fig, full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})


def analyze_stock(target_symbol: str, raw_ticker_input: str, avg_price: float = 0.0, lots: int = 0) -> dict:
    """Melakukan analisis teknikal, fundamental, profil perusahaan, portofolio, dan sinyal DSS."""
    stock = yf.Ticker(target_symbol)
    df = stock.history(period="6mo")

    ticker_display = raw_ticker_input.upper().replace('.JK', '')

    # Fallback jika target dengan .JK tidak ditemukan
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

    # Indikator Teknikal
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['STD'] = df['Close'].rolling(window=20).std()
    df['Upper_Band'] = df['MA20'] + (df['STD'] * 2)
    df['Lower_Band'] = df['MA20'] - (df['STD'] * 2)

    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-9)
    df['RSI'] = 100.0 - (100.0 / (1.0 + rs))

    latest_rsi = float(df['RSI'].iloc[-1]) if pd.notnull(df['RSI'].iloc[-1]) else 50.0
    latest_ma20 = float(df['MA20'].iloc[-1]) if pd.notnull(df['MA20'].iloc[-1]) else current_price
    latest_upper = float(df['Upper_Band'].iloc[-1]) if pd.notnull(df['Upper_Band'].iloc[-1]) else current_price * 1.05
    latest_lower = float(df['Lower_Band'].iloc[-1]) if pd.notnull(df['Lower_Band'].iloc[-1]) else current_price * 0.95

    # Trend Strength Score (0 - 100)
    strength = 50
    if current_price > latest_ma20:
        strength += 20
    else:
        strength -= 15

    if latest_rsi < 30:
        strength += 20
    elif latest_rsi > 70:
        strength -= 20
    elif latest_rsi > 50:
        strength += 10
    else:
        strength -= 10

    if current_price <= latest_lower:
        strength += 10
    elif current_price >= latest_upper:
        strength -= 10

    strength = max(10, min(95, strength))

    # Sinyal Rekomendasi Formal & Styling Kelas Meter
    if strength >= 70:
        rekomendasi = "STRONG ACCUMULATE"
        badge_style = "signal-strong-buy"
        strength_badge_class = "bg-success-subtle text-success border border-success border-opacity-25"
        strength_bar_class = "bg-success"
    elif strength >= 55:
        rekomendasi = "BUY / OVERWEIGHT"
        badge_style = "signal-buy"
        strength_badge_class = "bg-primary-subtle text-primary border border-primary border-opacity-25"
        strength_bar_class = "bg-success"
    elif strength <= 30:
        rekomendasi = "STRONG REDUCE"
        badge_style = "signal-strong-sell"
        strength_badge_class = "bg-danger-subtle text-danger border border-danger border-opacity-25"
        strength_bar_class = "bg-danger"
    elif strength <= 45:
        rekomendasi = "SELL / UNDERWEIGHT"
        badge_style = "signal-sell"
        strength_badge_class = "bg-warning-subtle text-warning border border-warning border-opacity-25"
        strength_bar_class = "bg-warning"
    else:
        rekomendasi = "HOLD / NEUTRAL"
        badge_style = "signal-neutral"
        strength_badge_class = "bg-secondary bg-opacity-10 text-secondary border border-color"
        strength_bar_class = "bg-warning"

    # AI Executive Insight
    insights = []
    if current_price > latest_upper:
        insights.append("Harga menembus Batas Atas Bollinger Band. Terjadi dorongan beli yang signifikan, namun berpotensi menghadapi tekanan ambil untung jangka pendek.")
    elif current_price < latest_lower:
        insights.append("Harga menyentuh Batas Bawah Bollinger Band. Tekanan jual berada di zona jenuh, membuka peluang teknikal rebound.")
    else:
        insights.append("Harga bergerak stabil di dalam kanal normal volatilitas Bollinger Bands.")

    if latest_rsi < 30:
        insights.append(f"Indikator momentum RSI ({latest_rsi:.1f}) mengonfirmasi status Jenuh Jual (Oversold).")
    elif latest_rsi > 70:
        insights.append(f"Indikator momentum RSI ({latest_rsi:.1f}) mengonfirmasi status Jenuh Beli (Overbought).")
    else:
        insights.append(f"Momentum RSI berada pada level seimbang ({latest_rsi:.1f}).")

    if current_price > latest_ma20:
        insights.append("Posisi harga di atas MA20 mempertahankan struktur tren jangka pendek yang konstruktif.")
    else:
        insights.append("Posisi harga di bawah MA20 mengindikasikan fase konsolidasi atau koreksi.")

    insight_text = " ".join(insights)

    # Data Fundamental & Berita
    info = stock.info if hasattr(stock, 'info') else {}
    fundamental = get_fundamental_data(info)
    news_data = parse_news(stock, ticker_display=ticker_display, company_name=fundamental.get('company_name', ''))

    # Kalkulasi Portofolio
    portfolio = None
    if avg_price > 0 and lots > 0:
        shares = lots * 100
        total_invested = avg_price * shares
        current_val = current_price * shares
        pl_nominal = current_val - total_invested
        pl_pct = ((current_price - avg_price) / avg_price) * 100
        portfolio = {
            'invested': total_invested,
            'current_value': current_val,
            'pl_nominal': pl_nominal,
            'pl_pct': pl_pct,
            'is_profit': pl_nominal >= 0
        }

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
        'insight': insight_text,
        'portfolio': portfolio,
        'error_message': None
    }
