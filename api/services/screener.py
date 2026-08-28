import os
import json
import time
import pandas as pd
import yfinance as yf

try:
    from api.services.idx_universe import FULL_IDX_CATALOG
except (ImportError, ModuleNotFoundError):
    from services.idx_universe import FULL_IDX_CATALOG

SCREENER_UNIVERSE = FULL_IDX_CATALOG

_DIR = os.path.dirname(os.path.abspath(__file__))
_CACHE_FILE = os.path.join(_DIR, 'screener_cache.json')

_CACHE = {
    'data': [],
    'timestamp': 0
}


def _load_cache_from_disk() -> list[dict]:
    if os.path.exists(_CACHE_FILE):
        try:
            with open(_CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'data' in data:
                    _CACHE['data'] = data['data']
                    _CACHE['timestamp'] = data.get('timestamp', time.time())
                    return _CACHE['data']
        except Exception:
            pass
    return []


def _save_cache_to_disk(results: list[dict]):
    try:
        with open(_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': time.time(), 'count': len(results), 'data': results}, f, ensure_ascii=False)
    except Exception:
        pass


def scan_all_ihsg_stocks() -> list[dict]:
    symbols = [item['symbol'] for item in FULL_IDX_CATALOG]
    chunk_size = 150
    chunks = [symbols[i:i + chunk_size] for i in range(0, len(symbols), chunk_size)]

    all_results = []
    symbol_map = {item['symbol']: item for item in FULL_IDX_CATALOG}

    for c in chunks:
        try:
            data = yf.download(' '.join(c), period='1mo', group_by='ticker', threads=True, progress=False)
        except Exception:
            continue

        for sym in c:
            item = symbol_map.get(sym)
            if not item:
                continue
            try:
                if sym in data.columns.levels[0]:
                    df = data[sym].dropna(how='all')
                else:
                    continue

                if df.empty or len(df) < 5:
                    continue

                close_series = df['Close'].dropna()
                if close_series.empty or len(close_series) < 3:
                    continue

                current_price = float(close_series.iloc[-1])
                if current_price <= 0:
                    continue

                prev_price = float(close_series.iloc[-2]) if len(close_series) >= 2 else current_price
                change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0.0

                ma20_val = float(close_series.rolling(20, min_periods=3).mean().iloc[-1])
                ma50_val = float(close_series.rolling(50, min_periods=5).mean().iloc[-1])

                std_val = float(close_series.rolling(20, min_periods=3).std().iloc[-1]) if len(close_series) >= 3 else 0.0
                if pd.isna(std_val):
                    std_val = 0.0
                upper_val = ma20_val + (std_val * 2)
                lower_val = ma20_val - (std_val * 2)

                delta = close_series.diff()
                gain = delta.clip(lower=0).rolling(14, min_periods=1).mean()
                loss = -delta.clip(upper=0).rolling(14, min_periods=1).mean()
                rs = gain / loss.replace(0, 1e-9)
                rsi_series = 100.0 - (100.0 / (1.0 + rs))
                latest_rsi = float(rsi_series.iloc[-1]) if pd.notnull(rsi_series.iloc[-1]) else 50.0

                vol_series = df['Volume'].dropna() if 'Volume' in df.columns else pd.Series()
                total_net_val = 0.0
                if not vol_series.empty and len(df) >= 3:
                    slice_tail = df.iloc[-min(10, len(df)):].copy()
                    for dt, row in slice_tail.iterrows():
                        try:
                            c_p = float(row['Close'])
                            o_p = float(row['Open'])
                            v_p = float(row['Volume'])
                            del_c = (c_p - o_p) / o_p if o_p > 0 else 0
                            total_net_val += (del_c * v_p * c_p * 0.30) / 1e9
                        except Exception:
                            pass

                if total_net_val >= 0.5:
                    foreign_status = 'NET BUY ASING'
                    foreign_badge = 'bias-bullish'
                    foreign_tag = 'net_buy'
                elif total_net_val <= -0.5:
                    foreign_status = 'NET SELL ASING'
                    foreign_badge = 'bias-caution'
                    foreign_tag = 'net_sell'
                else:
                    foreign_status = 'NETRAL'
                    foreign_badge = 'bias-neutral'
                    foreign_tag = 'neutral'

                if change_pct >= 0.5:
                    broksum_status = 'AKUMULASI'
                    broksum_badge = 'bias-buy'
                    broksum_tag = 'accumulation'
                elif change_pct <= -0.5:
                    broksum_status = 'DISTRIBUSI'
                    broksum_badge = 'bias-warning'
                    broksum_tag = 'distribution'
                else:
                    broksum_status = 'NETRAL'
                    broksum_badge = 'bias-neutral'
                    broksum_tag = 'neutral'

                if current_price >= ma20_val and latest_rsi >= 52 and latest_rsi <= 72:
                    dss_signal = 'BULLISH CONTINUATION'
                    dss_badge = 'bias-bullish'
                elif current_price < ma20_val and current_price >= ma50_val and latest_rsi >= 40:
                    dss_signal = 'BUY ON WEAKNESS'
                    dss_badge = 'bias-buy'
                elif latest_rsi < 36 or current_price <= lower_val:
                    dss_signal = 'OVERSOLD REBOUND'
                    dss_badge = 'bias-rebound'
                elif latest_rsi > 72 or current_price >= upper_val:
                    dss_signal = 'PROFIT TAKING'
                    dss_badge = 'bias-warning'
                elif current_price < ma20_val and current_price < ma50_val:
                    dss_signal = 'BEARISH CAUTION'
                    dss_badge = 'bias-caution'
                else:
                    dss_signal = 'NETRAL CONSOLIDATION'
                    dss_badge = 'bias-neutral'

                preset_tags = []
                if current_price >= ma20_val and latest_rsi >= 48 and latest_rsi <= 75:
                    preset_tags.append('bullish')
                if latest_rsi < 38 or current_price <= lower_val:
                    preset_tags.append('oversold')
                if broksum_tag == 'accumulation':
                    preset_tags.append('big_acc')
                if total_net_val >= 0.3:
                    preset_tags.append('foreign_inflow')
                if current_price < ma20_val and current_price >= ma50_val:
                    preset_tags.append('bow')
                if item['sector'] in ['Financials', 'Energy & Mining', 'Consumer Non-Cyclicals', 'Industrials'] and current_price >= 200:
                    preset_tags.append('dividend')

                all_results.append({
                    'code': item['code'],
                    'symbol': item['symbol'],
                    'name': item['name'],
                    'sector': item['sector'],
                    'price': round(current_price),
                    'price_str': f'Rp {round(current_price):,}',
                    'change_pct': round(change_pct, 2),
                    'change_str': f'+{change_pct:.2f}%' if change_pct >= 0 else f'{change_pct:.2f}%',
                    'is_positive': change_pct >= 0,
                    'rsi': round(latest_rsi, 1),
                    'ma20': round(ma20_val),
                    'ma50': round(ma50_val),
                    'above_ma20': current_price >= ma20_val,
                    'above_ma50': current_price >= ma50_val,
                    'is_golden_cross': ma20_val >= ma50_val,
                    'foreign_status': foreign_status,
                    'foreign_badge': foreign_badge,
                    'foreign_tag': foreign_tag,
                    'foreign_10d_m': round(total_net_val, 2),
                    'foreign_10d_str': f'+Rp {total_net_val:,.1f} M' if total_net_val >= 0 else f'-Rp {abs(total_net_val):,.1f} M',
                    'broksum_status': broksum_status,
                    'broksum_badge': broksum_badge,
                    'broksum_tag': broksum_tag,
                    'dss_signal': dss_signal,
                    'dss_badge': dss_badge,
                    'preset_tags': preset_tags
                })
            except Exception:
                continue

    all_results.sort(key=lambda x: x['code'])
    _CACHE['data'] = all_results
    _CACHE['timestamp'] = time.time()
    _save_cache_to_disk(all_results)
    return all_results


def get_screener_data(force_refresh: bool = False) -> list[dict]:
    now = time.time()
    if not force_refresh and _CACHE['data'] and (now - _CACHE['timestamp'] < 600):
        return _CACHE['data']

    if not force_refresh:
        disk_data = _load_cache_from_disk()
        if disk_data:
            return disk_data

    return scan_all_ihsg_stocks()
