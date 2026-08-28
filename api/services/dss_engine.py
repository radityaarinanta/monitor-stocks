import pandas as pd


def generate_dss_insights(df: pd.DataFrame, current_price: float, latest_ma20: float, latest_ma50: float, latest_rsi: float, latest_upper: float, latest_lower: float) -> dict:
    if current_price >= latest_ma20 and latest_ma20 >= latest_ma50:
        trend_point = f"Konfirmasi Bullish Uptrend primer solid. Garis MA20 (Rp {latest_ma20:,.0f}) dan MA50 (Rp {latest_ma50:,.0f}) berfungsi sebagai dynamic support."
    elif current_price >= latest_ma20 and current_price < latest_ma50:
        trend_point = f"Technical rebound jangka pendek di atas MA20 (Rp {latest_ma20:,.0f}), menguji resistensi tren menengah MA50 (Rp {latest_ma50:,.0f})."
    elif current_price < latest_ma20 and current_price >= latest_ma50:
        trend_point = f"Pullback teknikal wajar di bawah MA20 (Rp {latest_ma20:,.0f}), namun tren utama di atas MA50 (Rp {latest_ma50:,.0f}) masih konstruktif."
    else:
        trend_point = f"Tekanan koreksi (Bearish Bias). Posisi harga berada di bawah garis MA20 (Rp {latest_ma20:,.0f}) dan MA50 (Rp {latest_ma50:,.0f})."

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

    if current_price > latest_upper:
        volatility_point = f"Harga menembus Upper Band (Rp {latest_upper:,.0f}), mengonfirmasi ekspansi volatilitas tinggi dan dorongan beli agresif."
    elif current_price < latest_lower:
        volatility_point = f"Harga menyentuh Lower Band (Rp {latest_lower:,.0f}), menandakan volatilitas tertekan ke batas bawah statistik deviasi standar."
    else:
        volatility_point = f"Volatilitas harga stabil di dalam kanal normal Bollinger Bands (Batas: Rp {latest_lower:,.0f} - Rp {latest_upper:,.0f})."

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

    return {
        'trend_point': trend_point,
        'momentum_point': momentum_point,
        'volatility_point': volatility_point,
        'tactical_strategy': tactical_strategy,
        'market_bias': market_bias,
        'bias_badge_class': bias_badge_class
    }


def generate_portfolio_decision(avg_price: float, lots: int, current_price: float, latest_rsi: float, latest_upper: float, latest_lower: float, latest_ma20: float, latest_ma50: float, broker_summary: dict, trade_setup: dict) -> tuple[dict | None, str | None, str | None]:
    if avg_price <= 0 or lots <= 0:
        return None, None, None

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
    
    is_pullback = current_price < latest_ma20 and current_price >= latest_ma50
    is_downtrend = current_price < latest_ma20 and current_price < latest_ma50

    if pl_pct >= 0:
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

    return portfolio, portfolio_advice, portfolio_action_tag
