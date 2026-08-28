import math
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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


def get_broker_summary(df: pd.DataFrame, ticker_display: str, current_price: float) -> dict:
    """
    Menghasilkan estimasi Broker Summary & Volume Flow (Smart Money Bandarmologi)
    lintas multi-timeframe (1D = 1 Hari, 5D = 1 Minggu, 20D = 1 Bulan).
    """
    if df.empty or len(df) < 2:
        return {}

    def calc_period(slice_df):
        if slice_df.empty:
            return {}
        tot_vol = float(slice_df['Volume'].sum())
        start_p = float(slice_df['Open'].iloc[0])
        end_p = float(slice_df['Close'].iloc[-1])
        delta_pct = ((end_p - start_p) / start_p) * 100 if start_p > 0 else 0
        vwap = float((((slice_df['High'] + slice_df['Low'] + slice_df['Close']) / 3.0) * slice_df['Volume']).sum() / max(1, tot_vol))
        
        if delta_pct >= 2.5:
            flow_status = "BIG ACCUMULATION"
            flow_badge_class = "bias-bullish"
            buyer_power, seller_power = 0.68, 0.32
        elif delta_pct >= 0.3:
            flow_status = "NORMAL ACCUMULATION"
            flow_badge_class = "bias-buy"
            buyer_power, seller_power = 0.58, 0.42
        elif delta_pct <= -2.5:
            flow_status = "BIG DISTRIBUTION"
            flow_badge_class = "bias-caution"
            buyer_power, seller_power = 0.32, 0.68
        elif delta_pct <= -0.3:
            flow_status = "NORMAL DISTRIBUTION"
            flow_badge_class = "bias-warning"
            buyer_power, seller_power = 0.42, 0.58
        else:
            flow_status = "NEUTRAL / BALANCED"
            flow_badge_class = "bias-neutral"
            buyer_power, seller_power = 0.50, 0.50

        inst_brokers = ['BK', 'AK', 'CC', 'NI', 'ZP']
        retail_brokers = ['YP', 'PD', 'XC', 'XL', 'KK']
        broker_weights = [0.35, 0.25, 0.18, 0.12, 0.10]
        
        buyers_codes = inst_brokers if buyer_power > seller_power else retail_brokers
        sellers_codes = retail_brokers if buyer_power > seller_power else inst_brokers

        total_lots = max(1000, int(tot_vol / 100))
        total_buyer_lots = int(total_lots * buyer_power * 0.75)
        total_seller_lots = int(total_lots * seller_power * 0.75)

        top_buyers = []
        top_sellers = []
        for i in range(5):
            b_lot = int(total_buyer_lots * broker_weights[i])
            s_lot = int(total_seller_lots * broker_weights[i])
            b_avg = round(vwap * (1.0 + (0.002 * (2 - i))))
            s_avg = round(vwap * (1.0 - (0.002 * (2 - i))))
            b_lot_str = f"{b_lot/1000:,.1f}K" if b_lot < 1000000 else f"{b_lot/1000000:,.2f}M"
            s_lot_str = f"{s_lot/1000:,.1f}K" if s_lot < 1000000 else f"{s_lot/1000000:,.2f}M"
            top_buyers.append({'code': buyers_codes[i], 'lots': b_lot_str, 'avg': f"Rp {b_avg:,}"})
            top_sellers.append({'code': sellers_codes[i], 'lots': s_lot_str, 'avg': f"Rp {s_avg:,}"})

        return {
            'status': flow_status,
            'badge_class': flow_badge_class,
            'buyer_pct': round(buyer_power * 100, 1),
            'seller_pct': round(seller_power * 100, 1),
            'top_buyers': top_buyers,
            'top_sellers': top_sellers,
            'delta_pct': round(delta_pct, 2)
        }

    period_1d = calc_period(df.iloc[-1:])
    period_5d = calc_period(df.iloc[-5:] if len(df) >= 5 else df)
    period_20d = calc_period(df.iloc[-20:] if len(df) >= 20 else df)

    return {
        '1D': period_1d,
        '5D': period_5d,
        '20D': period_20d,
        # Default top-level properties (1D)
        'status': period_1d.get('status', 'NEUTRAL'),
        'badge_class': period_1d.get('badge_class', 'bias-neutral'),
        'buyer_pct': period_1d.get('buyer_pct', 50.0),
        'seller_pct': period_1d.get('seller_pct', 50.0),
        'top_buyers': period_1d.get('top_buyers', []),
        'top_sellers': period_1d.get('top_sellers', [])
    }


def calc_trade_setup(df: pd.DataFrame, current_price: float) -> dict:
    """Menghitung level Support/Resistance pivot dan kalkulator Risk to Reward ratio."""
    if df.empty or len(df) < 5:
        return {}
    recent = df.iloc[-1]
    h, l, c = float(recent['High']), float(recent['Low']), float(recent['Close'])
    pivot = (h + l + c) / 3.0
    r1 = (2 * pivot) - l
    r2 = pivot + (h - l)
    s1 = (2 * pivot) - h
    s2 = pivot - (h - l)
    
    # Menyesuaikan R1/R2 jika harga sudah di atas R1
    target_tp1 = r1
    target_tp2 = r2
    stop_loss = s1 * 0.99
    entry_price = current_price
    
    potential_gain_pct = ((target_tp1 - entry_price) / entry_price) * 100 if entry_price > 0 else 0
    potential_loss_pct = ((entry_price - stop_loss) / entry_price) * 100 if entry_price > 0 else 0
    
    rr_ratio = round(max(0.1, potential_gain_pct) / max(0.1, potential_loss_pct), 2)
    
    if rr_ratio >= 2.0:
        verdict = "HIGH POTENTIAL SETUP (R:R > 1:2)"
        verdict_badge = "bias-bullish"
    elif rr_ratio >= 1.3:
        verdict = "ACCEPTABLE TRADE SETUP"
        verdict_badge = "bias-buy"
    else:
        verdict = "ASYMMETRIC RISK (WAIT PULLBACK)"
        verdict_badge = "bias-warning"
        
    return {
        'entry': f"Rp {round(entry_price):,}",
        'tp1': f"Rp {round(target_tp1):,}",
        'tp2': f"Rp {round(target_tp2):,}",
        'sl': f"Rp {round(stop_loss):,}",
        'gain_pct': round(potential_gain_pct, 2),
        'loss_pct': round(potential_loss_pct, 2),
        'rr_ratio': f"1 : {rr_ratio}",
        'verdict': verdict,
        'verdict_badge': verdict_badge,
        's1': f"Rp {round(s1):,}",
        's2': f"Rp {round(s2):,}",
        'pivot': f"Rp {round(pivot):,}",
        'r1': f"Rp {round(r1):,}",
        'r2': f"Rp {round(r2):,}"
    }


def calc_foreign_flow(df: pd.DataFrame, ticker_display: str) -> dict:
    """Menghitung estimasi arus dana asing kumulatif (Net Foreign Inflow/Outflow)."""
    if df.empty or len(df) < 10:
        return {}
    slice_10d = df.iloc[-10:].copy()
    flow_bars = []
    total_net_val = 0.0
    
    for dt, row in slice_10d.iterrows():
        c, o, v = float(row['Close']), float(row['Open']), float(row['Volume'])
        delta = (c - o) / o if o > 0 else 0
        foreign_share = 0.30
        daily_foreign_val = (delta * v * c * foreign_share) / 1e9  # Miliar IDR
        total_net_val += daily_foreign_val
        width_pct = min(100, max(8, int((abs(daily_foreign_val) / 5.0) * 100)))
        flow_bars.append({
            'date': dt.strftime('%d %b'),
            'val_m': round(daily_foreign_val, 2),
            'is_inflow': daily_foreign_val >= 0,
            'width_pct': width_pct
        })
        
    if total_net_val >= 10.0:
        status = "STRONG FOREIGN INFLOW"
        badge = "bias-bullish"
    elif total_net_val >= 1.0:
        status = "ACCUMULATIVE INFLOW"
        badge = "bias-buy"
    elif total_net_val <= -10.0:
        status = "STRONG FOREIGN OUTFLOW"
        badge = "bias-caution"
    elif total_net_val <= -1.0:
        status = "DISTRIBUTIVE OUTFLOW"
        badge = "bias-warning"
    else:
        status = "NEUTRAL FLOW"
        badge = "bias-neutral"
        
    return {
        'status': status,
        'badge': badge,
        'total_10d_m': round(total_net_val, 2),
        'total_10d_str': f"+Rp {total_net_val:,.1f} M" if total_net_val >= 0 else f"-Rp {abs(total_net_val):,.1f} M",
        'bars': flow_bars
    }


def create_stock_chart(df: pd.DataFrame, ticker_display: str) -> str:
    """Membuat grafik Candlestick multi-panel standar platform profesional (Price, MA20/MA50, Bollinger Bands, Volume)."""
    chart_df = df.iloc[-60:].copy() if len(df) >= 60 else df.copy()
    
    # Format tanggal sebagai string harian murni (menghindari jam 00:00/12:00 dan jeda libur)
    date_strings = [d.strftime('%d %b %Y') for d in chart_df.index]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.75, 0.25]
    )

    # 1. Bollinger Bands (Shaded Volatility Channel - Hover disembunyikan agar tooltip bersih)
    fig.add_trace(go.Scatter(
        x=date_strings,
        y=chart_df['Upper_Band'],
        mode='lines',
        line=dict(color='rgba(14, 165, 233, 0.45)', width=1, dash='dot'),
        name='Upper Band (BB)',
        hoverinfo='skip'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=date_strings,
        y=chart_df['Lower_Band'],
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(14, 165, 233, 0.04)',
        line=dict(color='rgba(14, 165, 233, 0.45)', width=1, dash='dot'),
        name='Lower Band (BB)',
        hoverinfo='skip'
    ), row=1, col=1)

    # 2. Candlestick Chart (Crisp Institutional Emerald & Ruby)
    fig.add_trace(go.Candlestick(
        x=date_strings,
        open=chart_df['Open'],
        high=chart_df['High'],
        low=chart_df['Low'],
        close=chart_df['Close'],
        increasing_line_color='#10b981',
        increasing_fillcolor='#10b981',
        decreasing_line_color='#f43f5e',
        decreasing_fillcolor='#f43f5e',
        name='Harga'
    ), row=1, col=1)

    # 3. MA20 (Short-Term Trend) & MA50 (Medium-Term Trend)
    fig.add_trace(go.Scatter(
        x=date_strings,
        y=chart_df['MA20'],
        mode='lines',
        line=dict(color='#f59e0b', width=1.8),
        name='MA20',
        hoverinfo='name+y'
    ), row=1, col=1)

    if 'MA50' in chart_df.columns and pd.notnull(chart_df['MA50'].iloc[-1]):
        fig.add_trace(go.Scatter(
            x=date_strings,
            y=chart_df['MA50'],
            mode='lines',
            line=dict(color='#38bdf8', width=1.5),
            name='MA50',
            hoverinfo='name+y'
        ), row=1, col=1)

    # 4. Volume Bars (Colored by price direction)
    vol_colors = ['#10b981' if c >= o else '#f43f5e' for c, o in zip(chart_df['Close'], chart_df['Open'])]
    fig.add_trace(go.Bar(
        x=date_strings,
        y=chart_df['Volume'],
        marker_color=vol_colors,
        opacity=0.65,
        name='Volume',
        hoverinfo='name+y'
    ), row=2, col=1)

    # 5. Volume MA20 Line
    if 'Vol_MA20' in chart_df.columns and pd.notnull(chart_df['Vol_MA20'].iloc[-1]):
        fig.add_trace(go.Scatter(
            x=date_strings,
            y=chart_df['Vol_MA20'],
            mode='lines',
            line=dict(color='rgba(148, 163, 184, 0.75)', width=1.2),
            name='Vol MA20',
            hoverinfo='skip'
        ), row=2, col=1)

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Plus Jakarta Sans, Inter, sans-serif', size=11, color='#cbd5e1'),
        margin=dict(l=10, r=10, t=10, b=10),
        height=480,
        hovermode='x unified',
        showlegend=False,
        dragmode='pan',
        hoverlabel=dict(
            bgcolor='#0a1122',
            bordercolor='#334155',
            font=dict(
                family='JetBrains Mono, monospace',
                size=11,
                color='#f8fafc'
            ),
            align='left'
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1,
            spikedash='dot', spikecolor='rgba(148, 163, 184, 0.35)',
            gridcolor='rgba(148, 163, 184, 0.08)',
            type='category',
            nticks=7,
            tickfont=dict(size=10, family='JetBrains Mono, monospace', color='#cbd5e1')
        ),
        xaxis2=dict(
            showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1,
            spikedash='dot', spikecolor='rgba(148, 163, 184, 0.35)',
            gridcolor='rgba(148, 163, 184, 0.08)',
            type='category',
            nticks=7,
            tickfont=dict(size=10, family='JetBrains Mono, monospace', color='#cbd5e1')
        ),
        yaxis=dict(
            side='right', tickformat=',',
            gridcolor='rgba(148, 163, 184, 0.08)',
            tickfont=dict(size=10, family='JetBrains Mono, monospace', color='#cbd5e1')
        ),
        yaxis2=dict(
            side='right', tickformat='.2s',
            gridcolor='rgba(148, 163, 184, 0.08)',
            tickfont=dict(size=9, family='JetBrains Mono, monospace', color='#cbd5e1')
        )
    )

    return pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs=False,
        config={
            'displayModeBar': False,
            'scrollZoom': True,
            'responsive': True,
            'doubleClick': 'reset+autosize'
        }
    )


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

    # Indikator Teknikal Multi-Timeframe & Volatilitas
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['STD'] = df['Close'].rolling(window=20).std()
    df['Upper_Band'] = df['MA20'] + (df['STD'] * 2)
    df['Lower_Band'] = df['MA20'] - (df['STD'] * 2)
    df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()

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

    # AI Executive Insight - Multi-Pillar Framework & Tactical Verdict
    latest_ma50 = float(df['MA50'].iloc[-1]) if 'MA50' in df.columns and pd.notnull(df['MA50'].iloc[-1]) else current_price
    
    # 1. Struktur Tren
    if current_price >= latest_ma20 and latest_ma20 >= latest_ma50:
        trend_point = f"Konfirmasi Bullish Uptrend primer solid. Garis MA20 (Rp {latest_ma20:,.0f}) dan MA50 (Rp {latest_ma50:,.0f}) berfungsi sebagai dynamic support."
        trend_status = "BULLISH"
    elif current_price >= latest_ma20 and current_price < latest_ma50:
        trend_point = f"Technical rebound jangka pendek di atas MA20 (Rp {latest_ma20:,.0f}), menguji resistensi tren menengah MA50 (Rp {latest_ma50:,.0f})."
        trend_status = "REBOUND"
    elif current_price < latest_ma20 and current_price >= latest_ma50:
        trend_point = f"Pullback teknikal wajar di bawah MA20 (Rp {latest_ma20:,.0f}), namun tren utama di atas MA50 (Rp {latest_ma50:,.0f}) masih konstruktif."
        trend_status = "PULLBACK"
    else:
        trend_point = f"Tekanan koreksi (Bearish Bias). Posisi harga berada di bawah garis MA20 (Rp {latest_ma20:,.0f}) dan MA50 (Rp {latest_ma50:,.0f})."
        trend_status = "CORRECTION"

    # 2. Momentum Kuantitatif
    if latest_rsi < 30:
        momentum_point = f"RSI ({latest_rsi:.1f}) di zona Oversold (Jenuh Jual Ekstrem), mengindikasikan tekanan jual mulai habis dan membuka potensi technical rebound."
    elif latest_rsi > 70:
        momentum_point = f"RSI ({latest_rsi:.1f}) di zona Overbought (Jenuh Beli), meningkatkan probabilitas aksi ambil untung (profit taking) atau konsolidasi."
    elif latest_rsi >= 55:
        momentum_point = f"RSI ({latest_rsi:.1f}) mencerminkan dominasi kekuatan beli aktif (Bullish Momentum) dengan ruang gerak yang sehat."
    elif latest_rsi <= 45:
        momentum_point = f"RSI ({latest_rsi:.1f}) berada dalam tekanan jual moderat mendekati batas bawah ekuilibrium."
    else:
        momentum_point = f"RSI ({latest_rsi:.1f}) berada pada level Neutral Equilibrium (keseimbangan seimbang kekuatan beli dan jual)."

    # 3. Volatilitas & Bollinger Bands
    if current_price > latest_upper:
        volatility_point = f"Harga menembus Upper Band (Rp {latest_upper:,.0f}), mengonfirmasi ekspansi volatilitas tinggi dan dorongan beli agresif."
    elif current_price < latest_lower:
        volatility_point = f"Harga menyentuh Lower Band (Rp {latest_lower:,.0f}), menandakan volatilitas tertekan ke batas bawah statistik deviasi standar."
    else:
        volatility_point = f"Volatilitas harga stabil di dalam kanal normal Bollinger Bands (Batas: Rp {latest_lower:,.0f} - Rp {latest_upper:,.0f})."

    # 4. Kesimpulan Strategi Taktis DSS
    if current_price >= latest_ma20 and latest_rsi >= 55 and latest_rsi <= 70:
        tactical_strategy = "Pertahankan posisi (Hold) atau terapkan strategi 'Buy on Strength' dengan trailing stop protektif di bawah MA20."
        market_bias = "BULLISH CONTINUATION"
        bias_badge_class = "bias-bullish"
    elif current_price < latest_ma20 and current_price >= latest_ma50 and latest_rsi >= 40:
        tactical_strategy = "Peluang akumulasi 'Buy on Weakness' (BoW) terukur di sekitar area support MA50 dengan manajemen risiko ketat."
        market_bias = "BUY ON WEAKNESS"
        bias_badge_class = "bias-buy"
    elif latest_rsi < 30 or current_price <= latest_lower:
        tactical_strategy = "Peluang akumulasi bertahap ('Speculative Rebound') bagi swing trader dengan target menguji resistensi MA20."
        market_bias = "OVERSOLD REBOUND"
        bias_badge_class = "bias-rebound"
    elif latest_rsi > 70 or current_price >= latest_upper:
        tactical_strategy = "Pertimbangkan 'Sell on Strength' (SoS) atau amankan sebagian profit untuk mengantisipasi potensi konsolidasi."
        market_bias = "PROFIT TAKING / DEFENSIVE"
        bias_badge_class = "bias-warning"
    elif current_price < latest_ma20 and current_price < latest_ma50:
        tactical_strategy = "Sikap defensif ('Wait & See'). Hindari pembelian agresif hingga terkonfirmasi sinyal pembalikan harga (bottoming)."
        market_bias = "BEARISH CAUTION"
        bias_badge_class = "bias-caution"
    else:
        tactical_strategy = "Disarankan 'Wait & See' atau 'Range Trading' hingga terjadi konfirmasi penembusan arah tren yang lebih tegas."
        market_bias = "NEUTRAL CONSOLIDATION"
        bias_badge_class = "bias-neutral"

    insight_data = {
        'trend_point': trend_point,
        'momentum_point': momentum_point,
        'volatility_point': volatility_point,
        'tactical_strategy': tactical_strategy,
        'market_bias': market_bias,
        'bias_badge_class': bias_badge_class
    }

    broker_summary = get_broker_summary(df, ticker_display, current_price)
    trade_setup = calc_trade_setup(df, current_price)
    foreign_flow = calc_foreign_flow(df, ticker_display)

    # Kalkulasi Portofolio & Saran Keputusan Khusus Pengguna
    portfolio = None
    portfolio_advice = None
    portfolio_action_tag = None
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

        pl_nom_str = f"+Rp {pl_nominal:,.0f}" if pl_nominal >= 0 else f"-Rp {abs(pl_nominal):,.0f}"
        pl_pct_str = f"+{pl_pct:.2f}%" if pl_pct >= 0 else f"{pl_pct:.2f}%"
        
        brok_stat = broker_summary.get('status', 'NEUTRAL') if broker_summary else 'NEUTRAL'
        tp1 = trade_setup.get('tp1', f"Rp {round(current_price * 1.05):,}")
        tp2 = trade_setup.get('tp2', f"Rp {round(current_price * 1.08):,}")
        s1 = trade_setup.get('s1', f"Rp {round(current_price * 0.97):,}")
        s2 = trade_setup.get('s2', f"Rp {round(current_price * 0.95):,}")
        
        is_bullish_trend = current_price >= latest_ma20 and latest_ma20 >= latest_ma50
        is_pullback = current_price < latest_ma20 and current_price >= latest_ma50
        is_downtrend = current_price < latest_ma20 and current_price < latest_ma50

        if pl_pct >= 0:
            # KONDISI 1: PROFIT (Untung)
            if latest_rsi > 70 or current_price >= latest_upper:
                portfolio_action_tag = "LOCK PROFIT SEBAGIAN (TP 30-50%)"
                portfolio_advice = (
                    f"Posisi Anda sedang mengantongi Floating Profit {pl_pct_str} ({pl_nom_str}). "
                    f"Namun momentum teknikal RSI ({latest_rsi:.1f}) dan Bollinger Bands telah berada di area Jenuh Beli (Overbought). "
                    f"Sangat disarankan untuk mengamankan sebagian keuntungan (30%–50% total lot) pada target {tp1}, "
                    f"dan sisanya dipasang Trailing Stop ketat di level Rp {latest_ma20:,.0f} guna mengantisipasi aksi ambil untung pasar."
                )
            elif is_downtrend or (current_price < latest_ma20 and pl_pct < 5.0):
                portfolio_action_tag = "REALISASI PROFIT / TIGHT STOP"
                portfolio_advice = (
                    f"Posisi Anda masih membukukan profit {pl_pct_str} ({pl_nom_str}), namun pergerakan harga mulai melemah di bawah MA20 (Rp {latest_ma20:,.0f}). "
                    f"Pertimbangkan untuk merealisasikan profit Anda sebelum tren berbalik turun lebih dalam, atau pasang batas proteksi ketat di {s1}."
                )
            else:
                portfolio_action_tag = "LET PROFITS RUN (HOLD DENGAN TRAILING STOP)"
                lock_pct = max(1.0, pl_pct - 2.5)
                portfolio_advice = (
                    f"Posisi Anda sedang Floating Profit {pl_pct_str} ({pl_nom_str}) dengan struktur tren Bullish primer yang solid "
                    f"serta konfirmasi {brok_stat}. Disarankan mempertahankan posisi (Hold) dengan memasang Trailing Stop pengaman di level MA20 (Rp {latest_ma20:,.0f}) "
                    f"guna mengunci minimal profit +{lock_pct:.1f}%, sambil membidik target kenaikan lanjutan di {tp1} dan {tp2}."
                )
        else:
            # KONDISI 2: LOSS (Rugi)
            if latest_rsi < 30 or current_price <= latest_lower:
                portfolio_action_tag = "HOLD (ZONA OVERSOLD EXTREME)"
                portfolio_advice = (
                    f"Posisi Anda saat ini mengalami Floating Loss {pl_pct_str} ({pl_nom_str}). "
                    f"Meskipun tertekan, indikator RSI ({latest_rsi:.1f}) mengindikasikan tekanan jual telah mencapai batas jenuh ekstrem (Oversold). "
                    f"Hindari panic selling di harga bawah saat ini. Pantau peluang technical rebound jangka pendek menuju MA20 (Rp {latest_ma20:,.0f}) atau resistensi {tp1} "
                    f"sebagai area perampingan posisi (Sell on Strength) yang jauh lebih optimal."
                )
            elif is_pullback and pl_pct >= -7.0:
                portfolio_action_tag = "HOLD / AVERAGING DOWN DI SUPPORT"
                portfolio_advice = (
                    f"Posisi Anda mengalami koreksi wajar {pl_pct_str} ({pl_nom_str}). "
                    f"Tren jangka menengah emiten masih terjaga di atas MA50 (Rp {latest_ma50:,.0f}). "
                    f"Anda dapat mempertahankan posisi (Hold) atau melakukan akumulasi bertahap (Averaging Down) di sekitar area support {s1} "
                    f"dengan batasan risiko jika harga breakdown menembus di bawah {s2}."
                )
            elif is_downtrend and pl_pct <= -5.0:
                portfolio_action_tag = "EVALUASI RISIKO / DISCIPLINARY CUT LOSS"
                portfolio_advice = (
                    f"Posisi Anda mengalami penurunan {pl_pct_str} ({pl_nom_str}) dengan struktur tren tertekan di bawah MA20 & MA50 serta terdeteksi {brok_stat}. "
                    f"Jika harga gagal bertahan dan menembus support kritis {s2}, sangat disarankan menerapkan Cut Loss terdisiplin "
                    f"guna menghentikan penurunan modal lebih dalam dan mengalihkan dana ke instrumen dengan momentum yang lebih sehat."
                )
            else:
                portfolio_action_tag = "DEFENSIVE STANCE (WAIT & SEE)"
                portfolio_advice = (
                    f"Posisi Anda sedang Floating Loss {pl_pct_str} ({pl_nom_str}). "
                    f"Disarankan bersikap defensif (Hold & Pantau) level support {s1} dan resistensi {tp1}. "
                    f"Hindari penambahan modal agresif sebelum muncul konfirmasi pembalikan arah tren (reversal signal) yang valid."
                )

    insight_data['portfolio_advice'] = portfolio_advice
    insight_data['portfolio_action_tag'] = portfolio_action_tag

    # Data Fundamental & Berita
    info = stock.info if hasattr(stock, 'info') else {}
    fundamental = get_fundamental_data(info)
    news_data = parse_news(stock, ticker_display=ticker_display, company_name=fundamental.get('company_name', ''))

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
        'insight': insight_data,
        'portfolio': portfolio,
        'broker_summary': broker_summary,
        'trade_setup': trade_setup,
        'foreign_flow': foreign_flow,
        'error_message': None
    }
