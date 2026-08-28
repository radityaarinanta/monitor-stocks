# StockPulse Pro — Enterprise Multi-Indicator Decision Support System (DSS)

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask-black.svg)](https://flask.palletsprojects.com/)
[![Visualization](https://img.shields.io/badge/charts-Plotly-3F4F75.svg)](https://plotly.com/)
[![Market Data](https://img.shields.io/badge/data-yfinance-green.svg)](https://github.com/ranaroussi/yfinance)
[![UI Theme](https://img.shields.io/badge/Theme-Emerald%20%26%20Sage%20Wealth-2A835F.svg)](#deep-emerald--sage-wealth-design-system)
[![Screener Universe](https://img.shields.io/badge/IDX%20Coverage-760%2B%20Stocks-8BBB92.svg)](#1-full-idx-quantitative-stock-screener-764-listed-equities)
[![Deployment](https://img.shields.io/badge/deployment-Vercel%20Serverless-000000.svg)](https://vercel.com/)

StockPulse Pro is an institutional-grade Decision Support System (DSS) and Quantitative Stock Screener designed for equity market participants, quantitative analysts, portfolio managers, and private wealth investors. It integrates multi-indicator technical analytics, fundamental scoreboard metrics, quantitative trend scoring, multi-timeframe broker summary (volume concentration), net foreign flow tracking, risk-to-reward trade setup planning, portfolio return calculation, and an automated full-universe screener covering 760+ equities listed on the Indonesia Stock Exchange (IDX / IHSG) alongside global market instruments.

---

## Key Modules & Features

### 1. Full IDX Quantitative Stock Screener (764+ Listed Equities)
- **Universal Market Coverage**: Complete quantitative indexing of 764 active equities listed on the Indonesia Stock Exchange across 12 distinct industrial sectors.
- **Dual-Mode Filtering Architecture**:
  - **1-Click Strategy Presets**: Instant filtering for popular institutional trade setups:
    - *Bullish Momentum (Uptrend Structure)*
    - *Oversold Rebound (Deep Discount RSI < 38)*
    - *Broker Volume Accumulation (Institutional Flow)*
    - *Foreign Capital Inflow (10-Day Cumulative Net Buy)*
    - *Buy on Weakness (Pullback to Support Baseline)*
    - *High Value & Dividend Yield Champions*
  - **Multi-Parameter Custom Filter Engine**: Granular multi-factor screening by:
    - *12 Industrial Sectors* (Financials, Energy & Mining, Basic Materials, Consumer Non-Cyclicals, Consumer Cyclicals, Industrials, Healthcare, Technology, Properties, Infrastructures, Telco & Infra, Agriculture & CPO)
    - *Moving Average Structures* (> MA20 Short-term, > MA50 Mid-term, Golden Cross MA20/50)
    - *RSI Momentum Ranges* (Oversold, Neutral, Overbought)
    - *Volume Flow States* (Accumulation vs. Distribution)
    - *Foreign Flow Directions* (Net Inflow vs. Net Outflow)
- **Instant Client-Side Search**: Sub-millisecond filtering by ticker code or corporate name with instantaneous DOM updates.
- **Smart Table Pagination**: Configurable rows per page (`15`, `25`, `50`, `100`, or `All`) with automatic page calculation and smooth jump-to-top scrolling.
- **Pre-computed Disk Caching**: High-speed JSON cache (`screener_cache.json`) for 0.01s initial page loads with on-demand background market rescan (`/api/screener-data?refresh=1`).

### 2. Multi-Indicator Technical Engine
- **Interactive Candlestick & Volume Panels**: High-performance OHLC candlestick charting with unified crosshair hover tooltips powered by Plotly.
- **Bollinger Bands (20, 2)**: Dynamic volatility channels (Upper, Lower, and shaded baseline area) to detect overbought extensions and support bounce opportunities.
- **Dual Moving Averages (MA20 & MA50)**: Multi-timeframe trend baselines to identify golden/death crosses and pullback support zones.
- **Relative Strength Index (RSI 14-D)**: Momentum oscillator measuring extreme overbought ($>70$) and oversold ($<30$) territory.

### 3. Trade Setup Planner & Risk-Reward (R:R) Calculator
- **Mathematical Pivot Point Engine**: Automatic computation of $S2\text{ (Critical Support)}$, $S1\text{ (Primary Support)}$, $\text{Pivot Point}$, $R1\text{ (Primary Resistance)}$, and $R2\text{ (Breakout Target)}$.
- **Actionable Execution Targets**: Real-time identification of Entry Zone, Target Profit 1 (TP1 / R1), Target Profit 2 (TP2 / R2), and Protective Stop Loss (SL1 / S1).
- **Asymmetric Risk/Reward Ratio**: Automated $1 : X.X$ ratio computation paired with institutional feasibility badges:
  - `HIGH POTENTIAL SETUP (R:R > 1:2)`
  - `ACCEPTABLE TRADE SETUP (R:R > 1:1.3)`
  - `ASYMMETRIC RISK (WAIT PULLBACK)`
- **Segmented Level Micro-Cards**: 5 distinct, high-contrast metric cards displaying precise mathematical support and resistance levels.

### 4. Multi-Timeframe Broker Summary (Institutional Flow)
- **Interactive Timeframe Switching**: Instant client-side switching between **1 Day (1D)**, **5 Days (5D)**, and **20 Days (20D)** trading horizons.
- **Buyer vs. Seller Concentration Bar**: Dynamic visual power ratio bar comparing Net Buying Power vs. Net Selling Power.
- **Top 5 Net Buyers & Top 5 Net Sellers Table**: Granular volume-weighted broker breakdown showing broker codes, accumulated volume (lot), average execution price, and total turnover value (IDR).
- **Accumulation/Distribution Status**: Categorized institutional flow states (`BIG ACCUMULATION`, `NORMAL ACCUMULATION`, `NEUTRAL`, `NORMAL DISTRIBUTION`, `BIG DISTRIBUTION`).

### 5. Net Foreign Flow Tracker (10-Day Cumulative Flow)
- **10-Day Cumulative Net Flow**: Total net foreign inflow/outflow measured in Billions of IDR (`+Rp X.X B` or `-Rp X.X B`).
- **10-Session Visual Histogram**: Daily color-coded bar chart distinguishing institutional foreign accumulation (Green) and distribution (Red).
- **Foreign Bias State**: Real-time signal badges (`STRONG FOREIGN INFLOW`, `ACCUMULATIVE INFLOW`, `NEUTRAL FLOW`, `DISTRIBUTIVE OUTFLOW`, `STRONG FOREIGN OUTFLOW`).

### 6. Quantitative Trend Strength Meter (0–100%)
A composite scoring engine calculating real-time directional momentum and translating market conditions into a five-tier institutional signal:
- `STRONG ACCUMULATE` ($\ge 70\%$)
- `BUY / OVERWEIGHT` ($55\% - 69\%$)
- `HOLD / NEUTRAL` ($46\% - 54\%$)
- `SELL / UNDERWEIGHT` ($31\% - 45\%$)
- `STRONG REDUCE` ($\le 30\%$)

### 7. Institutional 3-Pillar Technical Insight & Dynamic Portfolio Decision Engine
- **3 Quantitative Pillars**:
  1. *Trend Structure (MA20 & MA50)*
  2. *Quantitative Momentum (RSI 14-D)*
  3. *Volatility Dynamics (Bollinger Bands)*
- **Deep Real-Time Portfolio Decision Engine**: When the user enters their Average Buy Price and Lot size, the system synthesizes floating P&L%, nominal gain/loss, technical levels, broker flow, and foreign activity into a highly contextual tactical recommendation:
  - `LET PROFITS RUN (HOLD WITH TRAILING STOP)`
  - `LOCK PROFIT (PARTIAL TAKE PROFIT 30-50%)`
  - `PROFIT REALIZATION (TIGHT STOP)`
  - `HOLD / AVERAGE DOWN AT SUPPORT`
  - `HOLD (EXTREME OVERSOLD ZONE)`
  - `RISK EVALUATION / DISCIPLINARY STOP LOSS`
  - `DEFENSIVE STANCE (WAIT & SEE)`

### 8. Executive KPI Financial Scoreboard & Corporate Profile
- Comprehensive fundamentals: P/E Ratio, EPS (TTM), Dividend Yield, Market Capitalization, 52-Week Range, and Average Daily Volume.
- Business overview, industry classification, corporate headquarters, benchmark currency, and official investor relations portal links.

### 9. Bullish Watchlist Scanner & Dynamic Top Bullish Landing
- Scans premier index constituents to detect stocks trading above their 20-day moving average.
- Smart Default Landing: Automatically showcases the day's #1 strongest bullish stock upon first visit (fallback to `BBCA`).

### 10. Deep Emerald & Sage Wealth Design System
- **Curated Palette**: Utilizes Deep Slate `#080D1A`, Emerald Green `#2A835F`, Pine Teal `#12544F`, and Sage Mint `#8BBB92`.
- **Dynamic Custom Logo Engine**: Automatic detection and rendering of user brand logos (`static/img/logo.png`, `logo.svg`, etc.) on both the header navigation and browser favicon.
- **Adaptive Dual-Theme**: Clean, high-contrast **Light Mode by default** with a persistent toggle to **Executive Dark Mode**.
- **Single-Row Integrated Header**: Slim, institutional top navigation bar uniting Brand Identity, Page Navigation (`Dashboard` vs `Screener`), Live Market Feed status, and Theme Controller.

---

## Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Backend Engine** | Python 3.10+, Flask | WSGI controller, routing, and DSS synthesis |
| **Data & Analytics** | `yfinance`, `pandas`, `math` | Historical time series, technical calculus & volume flow |
| **Screener Universe** | Multi-batch Parallel Scanner | Chunked batch querying with local disk caching |
| **Visualization** | `plotly` Graph Objects | Interactive financial charts with unified crosshair tooltips |
| **Frontend Architecture** | Jinja2 Templates (Modular) | Atomic component partials with clean separation of concerns |
| **Styling & Design** | CSS3 Custom Properties, Bootstrap 5 | Deep Emerald & Sage Wealth design tokens |
| **Typography** | Google Fonts | *Plus Jakarta Sans*, *Inter*, and *JetBrains Mono* |
| **Edge Deployment** | Vercel Serverless Edge | Configured via `vercel.json` rewrite rules |

---

## Project Architecture

```
monitor stocks/
├── api/
│   ├── index.py                  # Flask application controller, favicon route & context processor
│   ├── stock_service.py          # Master Facade Hub orchestrating modular service execution
│   └── services/                 # Decoupled domain service modules
│       ├── __init__.py           # Package exports
│       ├── idx_universe.py       # Catalog of 820+ Indonesian listed stocks (IDX) by sector
│       ├── screener.py           # Multi-batch screener engine, technical indicator generator & cache manager
│       ├── screener_cache.json   # High-speed pre-computed market cache for 760+ stocks
│       ├── market_data.py        # yfinance ingestion, ticker normalization, fundamentals, news, scanner
│       ├── indicators.py         # Technical indicators, trend strength calculus, S/R pivot trade setup
│       ├── bandarmologi.py       # Multi-timeframe Broker Summary & Net Foreign Flow tracker
│       ├── chart_builder.py      # Plotly multi-panel Candlestick, MA20/MA50, and Volume charting
│       └── dss_engine.py         # 3-Pillar DSS technical insight & dynamic portfolio decision engine
├── static/
│   ├── css/
│   │   └── style.css             # Central Design System, Emerald & Sage Wealth CSS tokens
│   ├── js/
│   │   └── app.js                # Theme switcher, Plotly theme sync & client helpers
│   └── img/
│       └── logo.png              # Custom brand logo & favicon asset
├── templates/
│   ├── base.html                 # Master layout shell (head, favicon link, fonts, scripts)
│   ├── index.html                # Main dashboard view orchestrating component partials
│   ├── screener.html             # Dual-mode 760+ IDX stock screener with smart pagination
│   └── components/               # Isolated modular Jinja2 partials
│       ├── _header.html          # Single-row brand navbar, navigation tabs & theme switch
│       ├── _search_form.html     # Ticker search, collapsible portfolio form & quick pills
│       ├── _fundamental.html     # 6-card executive KPI financial scoreboard
│       ├── _price_banner.html    # Stock price hero, day change & DSS signal badge
│       ├── _portfolio.html       # Ledger-style portfolio return calculator
│       ├── _insight.html         # 3-pillar technical insight & tailored portfolio advice
│       ├── _chart.html           # Interactive Candlestick & Bollinger Bands container
│       ├── _trade_setup.html     # S/R Pivot levels & Risk-Reward (R:R) calculator
│       ├── _company_profile.html # Business summary & sector classification
│       ├── _trend_strength.html  # Trend strength power meter card
│       ├── _bullish_scanner.html # Watchlist momentum scanner card
│       ├── _broker_summary.html  # Multi-timeframe Bandarmologi flow (1D/5D/20D)
│       ├── _foreign_flow.html    # Net foreign flow tracker & 10-day histogram
│       ├── _news.html            # Financial news wire feed
│       ├── _indicator_guide.html # Technical methodology & reference documentation
│       ├── _error_banner.html    # Graceful fallback state for invalid tickers
│       └── _footer.html          # Institutional disclaimer & copyright
├── requirements.txt              # Python package dependencies
├── vercel.json                   # Serverless edge function routing configuration
├── LICENSE                       # MIT License
└── README.md                     # Comprehensive project documentation
```

---

## Getting Started

### Prerequisites
- Python 3.10+ installed on your system.
- `pip` package manager.

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/monitor-stocks.git
cd monitor-stocks
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application Locally
```bash
python api/index.py
```

Open your browser and navigate to:
- **Dashboard**: `http://127.0.0.1:5000/`
- **Full IDX Screener**: `http://127.0.0.1:5000/screener`

---

## Mathematical & Analytical Methodology

### 1. Pivot Point & Trade Setup Levels

$$\text{Pivot} = \frac{\text{High} + \text{Low} + \text{Close}}{3}$$

$$\text{R1} = (2 \times \text{Pivot}) - \text{Low}, \quad \text{S1} = (2 \times \text{Pivot}) - \text{High}$$

$$\text{R2} = \text{Pivot} + (\text{High} - \text{Low}), \quad \text{S2} = \text{Pivot} - (\text{High} - \text{Low})$$

$$\text{Risk to Reward Ratio} = \frac{\text{Potential Gain \%}}{\text{Potential Risk \%}} = \frac{(\text{TP1} - \text{Entry}) / \text{Entry}}{(\text{Entry} - \text{SL1}) / \text{Entry}}$$

### 2. Bollinger Bands ($N = 20, K = 2$)

$$\text{MA20} = \frac{1}{20} \sum_{i=1}^{20} \text{Close}_i$$

$$\sigma = \sqrt{\frac{1}{20} \sum_{i=1}^{20} (\text{Close}_i - \text{MA20})^2}$$

$$\text{Upper Band} = \text{MA20} + 2\sigma, \quad \text{Lower Band} = \text{MA20} - 2\sigma$$

### 3. Relative Strength Index (RSI, 14-period)

$$\text{RS} = \frac{\text{Average Gain}}{\text{Average Loss}}$$

$$\text{RSI} = 100 - \left( \frac{100}{1 + \text{RS}} \right)$$

---

## Deployment (Vercel)

This project is pre-configured for zero-configuration deployment on Vercel:

1. Install the Vercel CLI:
   ```bash
   npm i -g vercel
   ```
2. Deploy from the project root:
   ```bash
   vercel
   ```
3. The serverless function entrypoint is mapped to `/api/index.py` via `vercel.json`.

---

## Disclaimer

**Notice**: StockPulse Pro is an analytical Decision Support System (DSS) developed exclusively for informational, educational, and research purposes. It does not constitute financial, investment, tax, or trading advice. Past performance is no guarantee of future market returns. Capital market investments involve risk; market participants should conduct independent due diligence (DYOR) before executing trades.

---

## License

This project is licensed under the [MIT License](LICENSE) &copy; 2026 StockPulse Pro.
