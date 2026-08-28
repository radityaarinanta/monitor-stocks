import math
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import yfinance as yf

WATCHLIST = [
    'BBCA.JK',
    'BBRI.JK',
    'BMRI.JK',
    'BBNI.JK',
    'TLKM.JK',
    'ASII.JK',
    'ICBP.JK',
    'INDF.JK',
    'AMRT.JK',
    'UNTR.JK',
    'KLBF.JK',
    'ADRO.JK',
]


def normalize_ticker(raw_ticker: str) -> tuple[str, str]:
    raw = (raw_ticker or '').strip().upper()
    if not raw:
        return 'BBCA.JK', 'BBCA'
    
    if '.' in raw or '-' in raw or '^' in raw:
        display = raw.replace('.JK', '')
        return raw, display
    
    if len(raw) <= 4 and raw.isalpha():
        return f"{raw}.JK", raw
    
    return raw, raw


def fetch_google_news_rss(query_keyword: str) -> list[dict]:
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
                
                if ' - ' in raw_title:
                    title_part, pub_part = raw_title.rsplit(' - ', 1)
                else:
                    title_part = raw_title
                    pub_part = 'Berita Pasar'
                
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

    sector = info.get('sector') or 'Financials & Enterprise'
    industry = info.get('industry') or 'General Industry'
    website = info.get('website') or ''
    country = info.get('country') or 'Indonesia'
    company_name = info.get('shortName') or info.get('longName') or 'Corporation'
    
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
            
    bullish_list.sort(key=lambda x: x['change'], reverse=True)
    return bullish_list[:6]
