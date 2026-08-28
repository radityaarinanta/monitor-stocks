import pandas as pd


def get_broker_summary(df: pd.DataFrame, ticker_display: str, current_price: float) -> dict:
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
        'status': period_1d.get('status', 'NEUTRAL'),
        'badge_class': period_1d.get('badge_class', 'bias-neutral'),
        'buyer_pct': period_1d.get('buyer_pct', 50.0),
        'seller_pct': period_1d.get('seller_pct', 50.0),
        'top_buyers': period_1d.get('top_buyers', []),
        'top_sellers': period_1d.get('top_sellers', [])
    }


def calc_foreign_flow(df: pd.DataFrame, ticker_display: str) -> dict:
    if df.empty or len(df) < 10:
        return {}
    slice_10d = df.iloc[-10:].copy()
    flow_bars = []
    total_net_val = 0.0
    
    for dt, row in slice_10d.iterrows():
        c, o, v = float(row['Close']), float(row['Open']), float(row['Volume'])
        delta = (c - o) / o if o > 0 else 0
        foreign_share = 0.30
        daily_foreign_val = (delta * v * c * foreign_share) / 1e9
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
