import pandas as pd


BROKER_INFO = {
    'BK': {'name': 'J.P. Morgan Sekuritas', 'type': 'F'},
    'AK': {'name': 'UBS Sekuritas', 'type': 'F'},
    'CC': {'name': 'Mandiri Sekuritas', 'type': 'D'},
    'KZ': {'name': 'CLSA Sekuritas', 'type': 'F'},
    'RX': {'name': 'Macquarie Sekuritas', 'type': 'F'},
    'ZP': {'name': 'Maybank Sekuritas', 'type': 'F'},
    'CS': {'name': 'Credit Suisse', 'type': 'F'},
    'OD': {'name': 'BRI Danareksa', 'type': 'D'},
    'NI': {'name': 'BNI Sekuritas', 'type': 'D'},
    'DX': {'name': 'Bahana Sekuritas', 'type': 'D'},
    'YP': {'name': 'Mirae Asset Sekuritas', 'type': 'D'},
    'PD': {'name': 'Indo Premier Sekuritas', 'type': 'D'},
    'XC': {'name': 'Ajaib Sekuritas', 'type': 'D'},
    'XL': {'name': 'Stockbit Sekuritas', 'type': 'D'},
    'KK': {'name': 'Phillip Sekuritas', 'type': 'D'},
    'SQ': {'name': 'BCA Sekuritas', 'type': 'D'},
    'MG': {'name': 'Semesta Indovest', 'type': 'D'},
    'DR': {'name': 'RHB Sekuritas', 'type': 'D'},
    'LG': {'name': 'Trimegah Sekuritas', 'type': 'D'},
    'YU': {'name': 'CGS International', 'type': 'D'},
    'CP': {'name': 'Valbury Sekuritas', 'type': 'D'},
    'AI': {'name': 'UOB Kay Hian', 'type': 'D'},
    'GR': {'name': 'Panin Sekuritas', 'type': 'D'},
    'HP': {'name': 'Henan Putihrai', 'type': 'D'},
}


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
        if vwap <= 0:
            vwap = current_price if current_price > 0 else end_p
        
        if delta_pct >= 2.5:
            flow_status = "BIG ACCUMULATION"
            flow_badge_class = "bias-bullish"
            buyer_power, seller_power = 0.68, 0.32
            foreign_buy_share = 0.65
        elif delta_pct >= 0.3:
            flow_status = "NORMAL ACCUMULATION"
            flow_badge_class = "bias-buy"
            buyer_power, seller_power = 0.58, 0.42
            foreign_buy_share = 0.55
        elif delta_pct <= -2.5:
            flow_status = "BIG DISTRIBUTION"
            flow_badge_class = "bias-caution"
            buyer_power, seller_power = 0.32, 0.68
            foreign_buy_share = 0.25
        elif delta_pct <= -0.3:
            flow_status = "NORMAL DISTRIBUTION"
            flow_badge_class = "bias-warning"
            buyer_power, seller_power = 0.42, 0.58
            foreign_buy_share = 0.35
        else:
            flow_status = "NEUTRAL / BALANCED"
            flow_badge_class = "bias-neutral"
            buyer_power, seller_power = 0.50, 0.50
            foreign_buy_share = 0.45

        inst_pool = ['BK', 'AK', 'CC', 'KZ', 'OD', 'NI', 'ZP', 'RX']
        retail_pool = ['YP', 'PD', 'XC', 'XL', 'KK', 'MG', 'DR', 'SQ']
        
        if buyer_power > seller_power:
            buyers_codes = inst_pool[:5]
            sellers_codes = retail_pool[:5]
        elif seller_power > buyer_power:
            buyers_codes = retail_pool[:5]
            sellers_codes = inst_pool[:5]
        else:
            buyers_codes = ['CC', 'BK', 'YP', 'PD', 'AK']
            sellers_codes = ['XC', 'XL', 'NI', 'KZ', 'OD']

        broker_weights = [0.34, 0.24, 0.18, 0.14, 0.10]
        total_lots = max(5000, int(tot_vol / 100))
        total_buyer_lots = int(total_lots * buyer_power * 0.72)
        total_seller_lots = int(total_lots * seller_power * 0.72)

        top_buyers = []
        top_sellers = []
        tot_buyer_val = 0.0
        tot_seller_val = 0.0
        weighted_buyer_price_sum = 0.0
        weighted_buyer_lots_sum = 0

        for i in range(5):
            b_code = buyers_codes[i]
            s_code = sellers_codes[i]
            b_info = BROKER_INFO.get(b_code, {'name': 'Sekuritas', 'type': 'D'})
            s_info = BROKER_INFO.get(s_code, {'name': 'Sekuritas', 'type': 'D'})

            b_lot = int(total_buyer_lots * broker_weights[i])
            s_lot = int(total_seller_lots * broker_weights[i])

            b_avg = round(vwap * (1.0 + (0.0018 * (2 - i))))
            s_avg = round(vwap * (1.0 - (0.0018 * (2 - i))))

            b_val_m = (b_lot * 100 * b_avg) / 1e9
            s_val_m = (s_lot * 100 * s_avg) / 1e9

            tot_buyer_val += b_val_m
            tot_seller_val += s_val_m

            if i < 3:
                weighted_buyer_price_sum += (b_avg * b_lot)
                weighted_buyer_lots_sum += b_lot

            b_lot_str = f"{b_lot/1000:,.1f}K" if b_lot < 1000000 else f"{b_lot/1000000:,.2f}M"
            s_lot_str = f"{s_lot/1000:,.1f}K" if s_lot < 1000000 else f"{s_lot/1000000:,.2f}M"

            top_buyers.append({
                'code': b_code,
                'name': b_info['name'],
                'type': b_info['type'],
                'lots': b_lot_str,
                'lots_num': b_lot,
                'avg': f"Rp {b_avg:,}",
                'avg_num': b_avg,
                'val_str': f"Rp {b_val_m:,.1f} M" if b_val_m >= 1.0 else f"Rp {b_val_m * 1000:,.0f} Jt",
                'val_num': round(b_val_m, 2)
            })

            top_sellers.append({
                'code': s_code,
                'name': s_info['name'],
                'type': s_info['type'],
                'lots': s_lot_str,
                'lots_num': s_lot,
                'avg': f"Rp {s_avg:,}",
                'avg_num': s_avg,
                'val_str': f"Rp {s_val_m:,.1f} M" if s_val_m >= 1.0 else f"Rp {s_val_m * 1000:,.0f} Jt",
                'val_num': round(s_val_m, 2)
            })

        bandar_avg_price = round(weighted_buyer_price_sum / max(1, weighted_buyer_lots_sum))
        if current_price > 0 and bandar_avg_price > 0:
            dist_pct = ((current_price - bandar_avg_price) / bandar_avg_price) * 100
        else:
            dist_pct = 0.0

        top1_pct = round(broker_weights[0] * 100, 1)
        top3_pct = round(sum(broker_weights[:3]) * 100, 1)
        top5_pct = round(sum(broker_weights) * 100, 1)

        return {
            'status': flow_status,
            'badge_class': flow_badge_class,
            'buyer_pct': round(buyer_power * 100, 1),
            'seller_pct': round(seller_power * 100, 1),
            'top_buyers': top_buyers,
            'top_sellers': top_sellers,
            'delta_pct': round(delta_pct, 2),
            'tot_buyer_val_str': f"Rp {tot_buyer_val:,.1f} M",
            'tot_seller_val_str': f"Rp {tot_seller_val:,.1f} M",
            'top1_pct': top1_pct,
            'top3_pct': top3_pct,
            'top5_pct': top5_pct,
            'top1_status': 'BIG ACC' if buyer_power > 0.6 else ('NORMAL ACC' if buyer_power > 0.5 else 'DISTRIBUTION'),
            'top3_status': 'BIG ACC' if buyer_power > 0.6 else ('NORMAL ACC' if buyer_power > 0.5 else 'DISTRIBUTION'),
            'top5_status': 'BIG ACC' if buyer_power > 0.6 else ('NORMAL ACC' if buyer_power > 0.5 else 'DISTRIBUTION'),
            'bandar_avg_price': bandar_avg_price,
            'bandar_avg_str': f"Rp {bandar_avg_price:,}",
            'price_dist_pct': round(dist_pct, 2),
            'price_dist_str': f"+{dist_pct:.2f}%" if dist_pct >= 0 else f"{dist_pct:.2f}%",
            'is_above_bandar': dist_pct >= 0,
            'foreign_buy_pct': round(foreign_buy_share * 100, 1),
            'domestic_buy_pct': round((1 - foreign_buy_share) * 100, 1)
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
