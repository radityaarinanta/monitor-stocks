import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


def create_stock_chart(df: pd.DataFrame, ticker_display: str) -> str:
    chart_df = df.iloc[-60:].copy() if len(df) >= 60 else df.copy()
    date_strings = [d.strftime('%d %b %Y') for d in chart_df.index]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.75, 0.25]
    )

    fig.add_trace(go.Scatter(
        x=date_strings,
        y=chart_df['Upper_Band'],
        mode='lines',
        line=dict(color='rgba(139, 187, 146, 0.55)', width=1, dash='dot'),
        name='Upper Band (BB)',
        hoverinfo='skip'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=date_strings,
        y=chart_df['Lower_Band'],
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(139, 187, 146, 0.05)',
        line=dict(color='rgba(139, 187, 146, 0.55)', width=1, dash='dot'),
        name='Lower Band (BB)',
        hoverinfo='skip'
    ), row=1, col=1)

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
            line=dict(color='#8BBB92', width=1.5),
            name='MA50',
            hoverinfo='name+y'
        ), row=1, col=1)

    vol_colors = ['#10b981' if c >= o else '#f43f5e' for c, o in zip(chart_df['Close'], chart_df['Open'])]
    fig.add_trace(go.Bar(
        x=date_strings,
        y=chart_df['Volume'],
        marker_color=vol_colors,
        opacity=0.65,
        name='Volume',
        hoverinfo='name+y'
    ), row=2, col=1)

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
