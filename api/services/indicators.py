import pandas as pd


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
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
    return df


def calculate_trend_strength(current_price: float, latest_ma20: float, latest_rsi: float, latest_upper: float, latest_lower: float) -> tuple[int, str, str, str, str]:
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

    return strength, rekomendasi, badge_style, strength_badge_class, strength_bar_class


def calc_trade_setup(df: pd.DataFrame, current_price: float) -> dict:
    if df.empty or len(df) < 5:
        return {}
    recent = df.iloc[-1]
    h, l, c = float(recent['High']), float(recent['Low']), float(recent['Close'])
    pivot = (h + l + c) / 3.0
    r1 = (2 * pivot) - l
    r2 = pivot + (h - l)
    s1 = (2 * pivot) - h
    s2 = pivot - (h - l)
    
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
