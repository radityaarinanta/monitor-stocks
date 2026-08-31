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


# ---------------------------------------------------------------------------
# Helper: Classify raw values into discrete categorical states
# ---------------------------------------------------------------------------

def _classify_profit_tier(pl_pct: float) -> str:
    """
    large_profit  : >= +15%
    profit        : >= +5%
    small_profit  : >= +1%
    breakeven     : -1% to +1%
    loss          : -1% to -10%
    deep_loss     : <= -10%
    critical_loss : <= -20%
    """
    if pl_pct >= 15.0:
        return 'large_profit'
    elif pl_pct >= 5.0:
        return 'profit'
    elif pl_pct >= 1.0:
        return 'small_profit'
    elif pl_pct >= -1.0:
        return 'breakeven'
    elif pl_pct >= -10.0:
        return 'loss'
    elif pl_pct >= -20.0:
        return 'deep_loss'
    else:
        return 'critical_loss'


def _classify_trend_state(current_price: float, ma20: float, ma50: float) -> str:
    """
    bullish_strong : price >= ma20 AND ma20 >= ma50  (Golden Cross structure)
    bullish_weak   : price >= ma20 AND ma20 < ma50
    pullback       : price < ma20 AND price >= ma50  (healthy pullback)
    bearish        : price < ma20 AND price < ma50   (double bearish)
    death_cross    : price < ma50 AND ma20 < ma50    (Death Cross confirmed)
    """
    if current_price >= ma20 and ma20 >= ma50:
        return 'bullish_strong'
    elif current_price >= ma20 and ma20 < ma50:
        return 'bullish_weak'
    elif current_price < ma20 and current_price >= ma50:
        return 'pullback'
    elif current_price < ma20 and ma20 < ma50:
        return 'death_cross'
    else:
        return 'bearish'


def _classify_rsi_zone(rsi: float) -> str:
    if rsi < 25.0:
        return 'deep_oversold'
    elif rsi < 35.0:
        return 'oversold'
    elif rsi <= 50.0:
        return 'neutral_weak'
    elif rsi <= 65.0:
        return 'neutral_strong'
    elif rsi <= 80.0:
        return 'overbought'
    else:
        return 'extreme_overbought'


def _classify_bb_position(current_price: float, upper: float, lower: float, ma20: float) -> str:
    mid = ma20
    band_width = upper - lower
    if band_width <= 0:
        return 'mid'
    if current_price > upper:
        return 'breakout_upper'
    elif current_price >= upper - band_width * 0.12:
        return 'near_upper'
    elif current_price < lower:
        return 'breakout_lower'
    elif current_price <= lower + band_width * 0.12:
        return 'near_lower'
    elif current_price >= mid:
        return 'mid_upper'
    else:
        return 'mid_lower'


def _classify_volume(current_volume: float, vol_ma20: float) -> str:
    if vol_ma20 <= 0:
        return 'normal'
    ratio = current_volume / vol_ma20
    if ratio >= 3.0:
        return 'extreme_spike'
    elif ratio >= 2.0:
        return 'high_spike'
    elif ratio >= 1.4:
        return 'high'
    elif ratio >= 0.7:
        return 'normal'
    else:
        return 'low'


def _classify_bandar_bias(status: str) -> str:
    """Normalize raw broker summary status string into short key."""
    s = (status or '').upper()
    if 'BIG ACCUMULATION' in s:
        return 'big_acc'
    elif 'NORMAL ACCUMULATION' in s or 'ACCUMULATION' in s:
        return 'acc'
    elif 'BIG DISTRIBUTION' in s:
        return 'big_dist'
    elif 'NORMAL DISTRIBUTION' in s or 'DISTRIBUTION' in s:
        return 'dist'
    else:
        return 'neutral'


# ---------------------------------------------------------------------------
# Main: Multi-Factor Portfolio Decision Engine
# ---------------------------------------------------------------------------

def generate_portfolio_decision(
    avg_price: float,
    lots: int,
    current_price: float,
    latest_rsi: float,
    latest_upper: float,
    latest_lower: float,
    latest_ma20: float,
    latest_ma50: float,
    broker_summary: dict,
    trade_setup: dict,
    df: pd.DataFrame = None
) -> tuple[dict | None, str | None, str | None, dict | None]:
    """
    Returns: (portfolio_dict, portfolio_advice_short, portfolio_action_tag, condition_detail_dict)
    """
    if avg_price <= 0 or lots <= 0:
        return None, None, None, None

    # --- P&L Calculation ---
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

    # --- Classify all 8 factors ---
    profit_tier = _classify_profit_tier(pl_pct)
    trend_state = _classify_trend_state(current_price, latest_ma20, latest_ma50)
    rsi_zone    = _classify_rsi_zone(latest_rsi)
    bb_pos      = _classify_bb_position(current_price, latest_upper, latest_lower, latest_ma20)

    # Volume: use last row of df if available
    current_volume = 0.0
    vol_ma20_val   = 0.0
    vol_state      = 'normal'
    vol_ratio      = 1.0
    if df is not None and not df.empty:
        try:
            current_volume = float(df['Volume'].iloc[-1])
            vol_ma20_val   = float(df['Vol_MA20'].iloc[-1]) if 'Vol_MA20' in df.columns and pd.notnull(df['Vol_MA20'].iloc[-1]) else 0.0
            vol_state      = _classify_volume(current_volume, vol_ma20_val)
            vol_ratio      = round(current_volume / vol_ma20_val, 2) if vol_ma20_val > 0 else 1.0
        except Exception:
            pass

    # Bandar bias 1D & 5D
    bandar_1d_raw  = broker_summary.get('1D', {}).get('status', 'NEUTRAL') if broker_summary else 'NEUTRAL'
    bandar_5d_raw  = broker_summary.get('5D', {}).get('status', 'NEUTRAL') if broker_summary else 'NEUTRAL'
    bandar_1d      = _classify_bandar_bias(bandar_1d_raw)
    bandar_5d      = _classify_bandar_bias(bandar_5d_raw)

    # Bandar cost vs current price
    bandar_avg     = broker_summary.get('1D', {}).get('bandar_avg_price', 0) if broker_summary else 0
    above_bandar   = (current_price >= bandar_avg) if bandar_avg > 0 else None
    bandar_dist_pct = broker_summary.get('1D', {}).get('price_dist_pct', 0.0) if broker_summary else 0.0
    bandar_dist_str = broker_summary.get('1D', {}).get('price_dist_str', 'N/A') if broker_summary else 'N/A'
    bandar_avg_str  = broker_summary.get('1D', {}).get('bandar_avg_str', 'N/A') if broker_summary else 'N/A'

    # Foreign flow (narrative only, no logic branching)
    foreign_flow_str = None
    if broker_summary and broker_summary.get('1D', {}).get('foreign_buy_pct'):
        foreign_pct = broker_summary.get('1D', {}).get('foreign_buy_pct', 0)
        foreign_flow_str = f"{foreign_pct:.1f}% volume dikuasai asing (1D)"

    # Trade setup refs
    tp1 = trade_setup.get('tp1', f"Rp {round(current_price * 1.05):,}") if trade_setup else f"Rp {round(current_price * 1.05):,}"
    tp2 = trade_setup.get('tp2', f"Rp {round(current_price * 1.08):,}") if trade_setup else f"Rp {round(current_price * 1.08):,}"
    s1  = trade_setup.get('s1',  f"Rp {round(current_price * 0.97):,}") if trade_setup else f"Rp {round(current_price * 0.97):,}"
    s2  = trade_setup.get('s2',  f"Rp {round(current_price * 0.95):,}") if trade_setup else f"Rp {round(current_price * 0.95):,}"

    ma20_str  = f"Rp {latest_ma20:,.0f}"
    ma50_str  = f"Rp {latest_ma50:,.0f}"
    rsi_str   = f"{latest_rsi:.1f}"

    # Detect signal divergence between 1D and 5D bandar
    bandar_divergence = (
        (bandar_1d in ('big_acc', 'acc') and bandar_5d in ('dist', 'big_dist')) or
        (bandar_1d in ('dist', 'big_dist') and bandar_5d in ('big_acc', 'acc'))
    )

    # -----------------------------------------------------------------------
    # DECISION MATRIX — 15+ Tags
    # Each branch sets: action_tag (str), short_advice (str)
    # -----------------------------------------------------------------------

    action_tag   = "DEFENSIVE STANCE — PANTAU DAN TUNGGU"
    short_advice = (
        f"Posisi Anda mencatat Floating Loss {pl_pct_str} ({pl_nom_str}). "
        f"Kondisi pasar belum menunjukkan sinyal arah yang tegas. "
        f"Pertahankan posisi, pantau level support {s1} dan resistensi {tp1}, "
        f"serta hindari penambahan modal sebelum terkonfirmasi sinyal reversal yang valid."
    )

    # ==================== PROFIT ZONE ====================

    if profit_tier in ('large_profit', 'profit', 'small_profit'):

        # Overbought + distribusi institusional = realisasi mendesak
        if rsi_zone in ('extreme_overbought', 'overbought') and bandar_1d in ('big_dist', 'dist') and bb_pos in ('breakout_upper', 'near_upper'):
            action_tag = "REALISASI PROFIT MENDESAK — RSI + BANDAR DISTRIBUSI"
            short_advice = (
                f"Posisi Anda membukukan Floating Profit {pl_pct_str} ({pl_nom_str}), "
                f"namun tiga sinyal peringatan terdeteksi secara bersamaan: RSI {rsi_str} memasuki zona jenuh beli, "
                f"harga mendekati Upper Bollinger Band (Rp {latest_upper:,.0f}), dan Bandar 1D terdeteksi dalam mode {bandar_1d_raw}. "
                f"Sangat disarankan merealisasikan setidaknya 50-70% posisi pada area {tp1} sebelum tekanan jual institusional mengakselerasi."
            )

        # Profit besar + overbought saja (tanpa bandar confirm distribusi)
        elif profit_tier == 'large_profit' and rsi_zone in ('extreme_overbought', 'overbought'):
            action_tag = "LOCK PROFIT SEBAGIAN — TRAILING STOP KETAT (RSI OVERBOUGHT)"
            short_advice = (
                f"Posisi Anda membukukan Floating Profit signifikan {pl_pct_str} ({pl_nom_str}). "
                f"RSI {rsi_str} berada di zona jenuh beli, meningkatkan probabilitas aksi ambil untung pasar. "
                f"Disarankan mengamankan 30-50% posisi pada {tp1}, dan sisanya dipasangi Trailing Stop di level MA20 ({ma20_str})."
            )

        # Volume spike bearish + profit — distribusi oleh volume besar
        elif vol_state in ('high_spike', 'extreme_spike') and bandar_1d in ('dist', 'big_dist'):
            action_tag = "REALISASI PROFIT — DISTRIBUSI VOLUME TINGGI TERDETEKSI"
            short_advice = (
                f"Posisi Anda mencatat Floating Profit {pl_pct_str} ({pl_nom_str}). "
                f"Volume hari ini mencapai {vol_ratio:.1f}x Vol MA20 disertai sinyal distribusi institusional ({bandar_1d_raw}). "
                f"Kombinasi ini mengindikasikan aksi jual terorganisir. "
                f"Pertimbangkan merealisasikan profit secara bertahap di area {tp1} sebelum tekanan berlanjut."
            )

        # Profit + harga mulai break bawah MA20 (tren melemah)
        elif current_price < latest_ma20 and trend_state in ('pullback', 'bearish', 'death_cross'):
            action_tag = "REALISASI PROFIT / TIGHT STOP — TREN MULAI MELEMAH"
            short_advice = (
                f"Posisi Anda masih mencatat profit {pl_pct_str} ({pl_nom_str}), namun harga telah bergerak di bawah MA20 ({ma20_str}), "
                f"mengindikasikan pelemahan tren jangka pendek. "
                f"Pertimbangkan merealisasikan profit atau pasang Stop Loss ketat di {s1} untuk memproteksi keuntungan."
            )

        # Profit + bullish kuat + bandar akumulasi = hold dan biarkan profit berjalan
        elif trend_state == 'bullish_strong' and bandar_1d in ('big_acc', 'acc') and rsi_zone in ('neutral_strong', 'overbought'):
            lock_floor = max(1.0, pl_pct - 3.0)
            action_tag = "LET PROFITS RUN — HOLD DENGAN TRAILING STOP (BULLISH + BANDAR AKUMULASI)"
            short_advice = (
                f"Posisi Anda membukukan Floating Profit {pl_pct_str} ({pl_nom_str}) dengan struktur tren Bullish primer yang solid "
                f"(harga di atas MA20 dan MA50) serta dikonfirmasi sinyal {bandar_1d_raw} dari bandar institusional. "
                f"Pertahankan posisi (Hold) dengan Trailing Stop pengaman di MA20 ({ma20_str}) untuk mengunci minimal +{lock_floor:.1f}%, "
                f"sambil membidik target kenaikan lanjutan di {tp1} dan {tp2}."
            )

        # Profit + divergensi sinyal bandar 1D vs 5D
        elif bandar_divergence:
            action_tag = "WASPADA — DIVERGENSI SINYAL INSTITUSIONAL (1D vs 5D)"
            short_advice = (
                f"Posisi Anda mencatat profit {pl_pct_str} ({pl_nom_str}). "
                f"Terdeteksi divergensi sinyal bandar: arah 1 Hari ({bandar_1d_raw}) bertentangan dengan arah 5 Hari ({bandar_5d_raw}). "
                f"Kondisi ini menandakan ketidakpastian arah institusional jangka pendek. "
                f"Disarankan menahan aksi tambah/kurang posisi hingga sinyal konvergen, serta pertahankan Stop Loss di {s1}."
            )

        # Default profit scenario
        else:
            lock_floor = max(1.0, pl_pct - 2.5)
            action_tag = "LET PROFITS RUN — HOLD DENGAN TRAILING STOP"
            short_advice = (
                f"Posisi Anda mencatat Floating Profit {pl_pct_str} ({pl_nom_str}) dengan kondisi pasar yang relatif konstruktif. "
                f"Pertahankan posisi (Hold) dengan Trailing Stop di MA20 ({ma20_str}) untuk mengunci minimal +{lock_floor:.1f}%, "
                f"sambil membidik target berikutnya di {tp1}."
            )

    # ==================== BREAKEVEN ZONE ====================

    elif profit_tier == 'breakeven':

        if trend_state == 'bullish_strong' and bandar_1d in ('big_acc', 'acc') and vol_state in ('high', 'high_spike', 'extreme_spike'):
            action_tag = "AKUMULASI DI KEKUATAN — SETUP KONSTRUKTIF TERKONFIRMASI"
            short_advice = (
                f"Posisi Anda berada di zona breakeven {pl_pct_str} ({pl_nom_str}). "
                f"Namun kondisi pasar sangat konstruktif: tren Bullish primer, volume {vol_ratio:.1f}x di atas rata-rata, "
                f"dan Bandar 1D terdeteksi {bandar_1d_raw}. "
                f"Ini adalah peluang untuk memperkuat posisi secara terukur di sekitar harga saat ini dengan Stop Loss di {s1}."
            )
        elif trend_state in ('bearish', 'death_cross') and bandar_1d in ('dist', 'big_dist'):
            action_tag = "WASPADAI PENURUNAN — PERTIMBANGKAN KURANGI POSISI"
            short_advice = (
                f"Posisi Anda berada di zona breakeven {pl_pct_str} ({pl_nom_str}), namun kondisi teknikal memburuk: "
                f"struktur tren {trend_state.replace('_', ' ').upper()} dengan Bandar 1D dalam mode {bandar_1d_raw}. "
                f"Pertimbangkan pengurangan posisi sebagian untuk melindungi modal sebelum harga berpotensi koreksi lebih dalam dari {s1}."
            )
        else:
            action_tag = "HOLD — MONITOR BREAKOUT ARAH TREN"
            short_advice = (
                f"Posisi Anda berada di zona breakeven {pl_pct_str} ({pl_nom_str}). "
                f"Belum ada sinyal direksi yang tegas. "
                f"Pantau penembusan di atas MA20 ({ma20_str}) sebagai konfirmasi bullish, "
                f"atau breakdown di bawah {s1} sebagai sinyal exit terdisiplin."
            )

    # ==================== LOSS ZONE ====================

    else:
        # RSI deep oversold + volume spike + dekat Lower BB = potensi rebound kuat
        if rsi_zone == 'deep_oversold' and bb_pos in ('breakout_lower', 'near_lower') and vol_state in ('high_spike', 'extreme_spike'):
            action_tag = "REBOUND SPEKULATIF — RSI EXTREME OVERSOLD + VOLUME SPIKE"
            short_advice = (
                f"Posisi Anda mengalami Floating Loss {pl_pct_str} ({pl_nom_str}). "
                f"Terdeteksi kondisi teknikal ekstrem: RSI {rsi_str} di zona Oversold dalam, "
                f"harga menyentuh batas bawah Bollinger Band, dan volume {vol_ratio:.1f}x di atas rata-rata — "
                f"kombinasi yang sering mendahului technical rebound. "
                f"Hindari panic selling saat ini. Pantau target rebound pertama ke {tp1} (level MA20). "
                f"Pasang batas risiko di bawah {s2} jika pola gagal terkonfirmasi."
            )

        # RSI oversold + Bandar akumulasi = hold dengan keyakinan institusional
        elif rsi_zone in ('deep_oversold', 'oversold') and bandar_1d in ('big_acc', 'acc'):
            action_tag = "HOLD KUAT — OVERSOLD + AKUMULASI INSTITUSIONAL TERDETEKSI"
            short_advice = (
                f"Posisi Anda mengalami Floating Loss {pl_pct_str} ({pl_nom_str}). "
                f"Meskipun tertekan, RSI {rsi_str} mengindikasikan kondisi jenuh jual, "
                f"dan Bandar 1D terdeteksi dalam mode {bandar_1d_raw} — sinyal bahwa institusi sedang memanfaatkan harga rendah. "
                f"Hindari panic selling. Fokus pada peluang technical rebound menuju MA20 ({ma20_str}) sebagai area evaluasi posisi."
            )

        # Loss sedang + Bandar distribusi + bearish = cut loss disiplin
        elif profit_tier in ('deep_loss', 'critical_loss') and trend_state in ('bearish', 'death_cross') and bandar_1d in ('big_dist', 'dist'):
            action_tag = "DISIPLIN CUT LOSS — RISIKO KUMULATIF TINGGI"
            short_advice = (
                f"Posisi Anda mengalami penurunan signifikan {pl_pct_str} ({pl_nom_str}) dengan kondisi yang memburuk secara bersamaan: "
                f"struktur tren {trend_state.replace('_', ' ').upper()}, RSI {rsi_str} tidak menunjukkan sinyal oversold yang meyakinkan, "
                f"dan Bandar 1D terdeteksi {bandar_1d_raw}. "
                f"Jika harga menembus support kritis {s2}, sangat disarankan menerapkan Cut Loss terdisiplin "
                f"untuk menghentikan erosi modal lebih lanjut dan mengalokasikan dana ke instrumen dengan momentum lebih sehat."
            )

        # Critical loss + semua faktor bearish = exit darurat
        elif profit_tier == 'critical_loss' and rsi_zone not in ('deep_oversold', 'oversold') and bandar_1d in ('big_dist', 'dist'):
            action_tag = "EXIT DARURAT — MULTI-RISIKO TERDETEKSI"
            short_advice = (
                f"Posisi Anda mengalami kerugian kritis {pl_pct_str} ({pl_nom_str}). "
                f"RSI {rsi_str} belum memasuki zona oversold, mengindikasikan tekanan jual masih berlanjut tanpa indikasi kelelahan seller. "
                f"Bandar 1D dalam mode {bandar_1d_raw} mengkonfirmasi distribusi institusional aktif. "
                f"Evaluasi exit total untuk menghentikan pendarahan modal dan pindahkan ke instrumen yang lebih sehat secara teknikal."
            )

        # Harga di atas modal bandar meski loss — sinyal harga yang masih terlindungi
        elif above_bandar is True and profit_tier == 'loss' and trend_state in ('pullback', 'bullish_weak'):
            action_tag = "HOLD — HARGA DI ATAS MODAL BANDAR (TERPROTEKSI)"
            short_advice = (
                f"Posisi Anda mencatat Floating Loss {pl_pct_str} ({pl_nom_str}), namun harga saat ini masih berada "
                f"{bandar_dist_str} di atas Modal Bandar ({bandar_avg_str}). "
                f"Kondisi ini mengindikasikan area harga masih dalam zona akumulasi institusional yang relatif aman. "
                f"Pertahankan posisi (Hold) dengan batas risiko di level {s1} dan pantau peluang pemulihan ke {tp1}."
            )

        # Loss + harga di bawah modal bandar + distribusi = posisi lemah
        elif above_bandar is False and bandar_1d in ('dist', 'big_dist'):
            action_tag = "CAUTION — DI BAWAH MODAL BANDAR + DISTRIBUSI AKTIF"
            short_advice = (
                f"Posisi Anda mengalami Floating Loss {pl_pct_str} ({pl_nom_str}), "
                f"dengan harga saat ini berada {bandar_dist_str} di bawah Modal Bandar ({bandar_avg_str}). "
                f"Kondisi ini menunjukkan posisi yang lemah — harga di bawah rata-rata biaya institusi disertai tekanan distribusi {bandar_1d_raw}. "
                f"Evaluasi ketat: pertahankan Stop Loss di {s2} dan hindari averaging down di kondisi ini."
            )

        # Divergensi bandar pada kondisi loss
        elif bandar_divergence:
            action_tag = "WASPADA — DIVERGENSI SINYAL INSTITUSIONAL SAAT RUGI"
            short_advice = (
                f"Posisi Anda mengalami Floating Loss {pl_pct_str} ({pl_nom_str}). "
                f"Sinyal bandar menunjukkan divergensi: 1 Hari ({bandar_1d_raw}) vs 5 Hari ({bandar_5d_raw}). "
                f"Kondisi yang kontradiktif ini mempersulit proyeksi arah jangka pendek. "
                f"Hindari keputusan besar hingga sinyal lebih jelas; pertahankan Stop Loss di {s1}."
            )

        # Loss ringan + pullback sehat di atas MA50 + bandar netral = averaging down terukur
        elif profit_tier == 'loss' and trend_state == 'pullback' and bandar_1d != 'big_dist':
            action_tag = "AVERAGING DOWN TERUKUR — PULLBACK DI ATAS MA50"
            short_advice = (
                f"Posisi Anda mengalami koreksi {pl_pct_str} ({pl_nom_str}). "
                f"Tren jangka menengah masih terjaga di atas MA50 ({ma50_str}), "
                f"dan tidak terdeteksi tekanan distribusi institusional besar. "
                f"Anda dapat mempertimbangkan averaging down bertahap di sekitar {s1} dengan batas risiko jika harga breakdown di bawah {s2}."
            )

        # Deep loss + pullback masih di atas MA50 = averaging berisiko
        elif profit_tier in ('deep_loss', 'critical_loss') and trend_state == 'pullback':
            action_tag = "AVERAGING DOWN BERISIKO — EVALUASI ULANG THESIS"
            short_advice = (
                f"Posisi Anda mengalami penurunan {pl_pct_str} ({pl_nom_str}) dengan harga masih di atas MA50 ({ma50_str}). "
                f"Meskipun tren menengah belum rusak, kerugian yang sudah dalam mengindikasikan perlunya evaluasi ulang tesis investasi. "
                f"Jika fundamental emiten masih solid, pertahankan dengan Stop Loss ketat di {s2}. "
                f"Averaging down hanya dilakukan secara sangat selektif dan bertahap."
            )

        # Default loss scenario
        else:
            action_tag = "DEFENSIVE STANCE — PANTAU DAN TUNGGU"
            short_advice = (
                f"Posisi Anda mengalami Floating Loss {pl_pct_str} ({pl_nom_str}). "
                f"Kondisi teknikal dan institusional belum memberikan sinyal arah yang meyakinkan. "
                f"Pertahankan posisi saat ini, pantau level support kritis di {s1}, "
                f"dan hindari penambahan modal agresif sebelum terkonfirmasi sinyal pembalikan tren yang valid."
            )

    # -----------------------------------------------------------------------
    # Build condition_detail dict (for 2-layer UI — no emoji, use text badges)
    # -----------------------------------------------------------------------

    # Trend label
    trend_label_map = {
        'bullish_strong': 'BULLISH KUAT (Golden Cross)',
        'bullish_weak'  : 'BULLISH LEMAH (MA20 > Harga, MA20 < MA50)',
        'pullback'      : 'PULLBACK — Di Atas MA50',
        'bearish'       : 'BEARISH BIAS',
        'death_cross'   : 'BEARISH KUAT (Death Cross)',
    }
    rsi_label_map = {
        'deep_oversold'      : f'RSI {rsi_str} — OVERSOLD DALAM (< 25)',
        'oversold'           : f'RSI {rsi_str} — OVERSOLD (< 35)',
        'neutral_weak'       : f'RSI {rsi_str} — NETRAL LEMAH (35-50)',
        'neutral_strong'     : f'RSI {rsi_str} — NETRAL KUAT (50-65)',
        'overbought'         : f'RSI {rsi_str} — OVERBOUGHT (> 65)',
        'extreme_overbought' : f'RSI {rsi_str} — EXTREME OVERBOUGHT (> 80)',
    }
    bb_label_map = {
        'breakout_upper': f'BB: Breakout Atas (Rp {latest_upper:,.0f})',
        'near_upper'    : f'BB: Dekat Upper Band (Rp {latest_upper:,.0f})',
        'mid_upper'     : f'BB: Tengah Atas (Normal)',
        'mid_lower'     : f'BB: Tengah Bawah (Normal)',
        'near_lower'    : f'BB: Dekat Lower Band (Rp {latest_lower:,.0f})',
        'breakout_lower': f'BB: Breakout Bawah (Rp {latest_lower:,.0f})',
    }
    vol_label_map = {
        'extreme_spike': f'Volume: SPIKE EKSTREM ({vol_ratio:.1f}x Vol MA20)',
        'high_spike'   : f'Volume: SPIKE TINGGI ({vol_ratio:.1f}x Vol MA20)',
        'high'         : f'Volume: TINGGI ({vol_ratio:.1f}x Vol MA20)',
        'normal'       : f'Volume: Normal ({vol_ratio:.1f}x Vol MA20)',
        'low'          : f'Volume: Rendah ({vol_ratio:.1f}x Vol MA20)',
    }

    # Signal sentiment for UI badge coloring (positive / neutral / negative / warning)
    def trend_sentiment(t):
        return 'positive' if t in ('bullish_strong',) else ('neutral' if t in ('bullish_weak', 'pullback') else 'negative')

    def rsi_sentiment(r):
        return 'warning' if r in ('deep_oversold', 'oversold') else ('negative' if r in ('overbought', 'extreme_overbought') else 'neutral')

    def bb_sentiment(b):
        return 'negative' if b in ('breakout_upper', 'near_upper') else ('warning' if b in ('breakout_lower', 'near_lower') else 'neutral')

    def vol_sentiment(v):
        return 'positive' if v in ('high', 'high_spike', 'extreme_spike') else ('neutral' if v == 'normal' else 'warning')

    def bandar_sentiment(b):
        return 'positive' if b in ('big_acc', 'acc') else ('negative' if b in ('big_dist', 'dist') else 'neutral')

    def above_bandar_sentiment(a):
        if a is True: return 'positive'
        if a is False: return 'negative'
        return 'neutral'

    # Bandar labels
    bandar_1d_label = f"Bandar 1D: {bandar_1d_raw}"
    bandar_5d_label = f"Bandar 5D: {bandar_5d_raw}"
    bandar_cost_label = (
        f"Modal Bandar: {bandar_avg_str} — Harga {bandar_dist_str} {'DI ATAS' if above_bandar else 'DI BAWAH'} modal"
        if bandar_avg > 0 else "Modal Bandar: Data tidak tersedia"
    )

    condition_detail = {
        'items': [
            {
                'label': trend_label_map.get(trend_state, trend_state.upper()),
                'sentiment': trend_sentiment(trend_state),
            },
            {
                'label': rsi_label_map.get(rsi_zone, f'RSI {rsi_str}'),
                'sentiment': rsi_sentiment(rsi_zone),
            },
            {
                'label': bb_label_map.get(bb_pos, 'BB: Normal'),
                'sentiment': bb_sentiment(bb_pos),
            },
            {
                'label': vol_label_map.get(vol_state, f'Volume: Normal'),
                'sentiment': vol_sentiment(vol_state),
            },
            {
                'label': bandar_1d_label,
                'sentiment': bandar_sentiment(bandar_1d),
            },
            {
                'label': bandar_5d_label,
                'sentiment': bandar_sentiment(bandar_5d),
            },
            {
                'label': bandar_cost_label,
                'sentiment': above_bandar_sentiment(above_bandar),
            },
        ],
        'divergence_warning': bandar_divergence,
        'foreign_flow_note': foreign_flow_str,
    }

    return portfolio, short_advice, action_tag, condition_detail
