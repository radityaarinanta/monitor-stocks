# StockPulse Pro — Enterprise Multi-Indicator Decision Support System (DSS)

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask-black.svg)](https://flask.palletsprojects.com/)
[![Visualization](https://img.shields.io/badge/charts-Plotly-3F4F75.svg)](https://plotly.com/)
[![Market Data](https://img.shields.io/badge/data-yfinance-green.svg)](https://github.com/ranaroussi/yfinance)
[![UI Theme](https://img.shields.io/badge/UI-Dual--Mode%20(Dark%2FLight)-6366F1.svg)](#dual-theme-design-system)
[![Project Status](https://img.shields.io/badge/status-active%20development-orange.svg)](#development-status)
[![Deployment](https://img.shields.io/badge/deployment-Vercel%20Serverless-000000.svg)](https://vercel.com/)

StockPulse Pro is an institutional-grade Decision Support System (DSS) designed for equity market participants, analysts, and investors. It integrates multi-indicator technical analytics, fundamental metrics, quantitative trend scoring, portfolio return tracking, and AI-driven commentary to facilitate disciplined, data-backed financial decision-making.

Optimized for both the Indonesia Stock Exchange (IDX / IHSG) and Global Equities (US Markets, Commodities, Indexes).

> [!NOTE]
> **Development Status**: This project is currently under active, phased development. New analytics modules, model optimizations, and feature enhancements are continuously being deployed in progressive releases.

---

## Key Features

### 1. Multi-Indicator Technical Engine
- Interactive Candlestick Charts: High-performance OHLC candlestick charting with unified crosshair hover tooltips powered by Plotly.
- Bollinger Bands (20, 2): Dynamic volatility bands (Upper, Lower, and shaded channel area) to detect overbought extensions and support bounce opportunities.
- 20-Day Moving Average (MA20): Baseline short-term momentum and trendline filter.
- Relative Strength Index (RSI 14): Momentum oscillator measuring overbought ($>70$) and oversold ($<30$) market extremes.

### 2. Quantitative Trend Strength Meter (0–100%)
A composite scoring engine calculating real-time directional momentum and translating market conditions into a five-tier institutional signal:
- `STRONG ACCUMULATE` ($\ge 70\%$)
- `BUY / OVERWEIGHT` ($55\% - 69\%$)
- `HOLD / NEUTRAL` ($46\% - 54\%$)
- `SELL / UNDERWEIGHT` ($31\% - 45\%$)
- `STRONG REDUCE` ($\le 30\%$)

### 3. AI Executive Quick Insight
Automated natural language synthesis summarizing technical confluence, volatility positioning, and momentum states in plain language for rapid executive briefings.

### 4. Executive KPI Financial Scoreboard
Comprehensive financial overview displaying:
- P/E Ratio (Trailing / Forward)
- EPS (Earnings Per Share)
- Dividend Yield (%)
- Market Capitalization (Trillions, Billions, or Millions)
- 52-Week Range (High / Low bounds)
- Market Volume (Daily trading activity)

### 5. Corporate Profile & Sector Intelligence
Contextual business intelligence showing the company's operational summary, sector classification, industry group, domicile, benchmark currency, and direct links to official investor portals.

### 6. Bullish Watchlist Trend Scanner
Automated screener monitoring premier blue-chip constituents (e.g., `BBCA`, `BBRI`, `BMRI`, `BBNI`, `TLKM`, `ASII`, `ICBP`, `AMRT`, `UNTR`, `KLBF`, `ADRO`) trading above their 20-day moving average.

### 7. Portfolio Position & P/L Tracker
Ledger-style portfolio calculator computing invested capital, current asset value, unrealized gain/loss (nominal IDR/USD), and total percentage return based on purchase price and lot size.

### 8. Financial News Wire
Live market feed tracking issuer-specific corporate announcements, financial press releases, and macroeconomic news with publisher citations and timestamps.

### 9. Dual-Theme System (Dark & Light Mode)
- Executive Dark Mode: High-contrast deep slate and navy tones (`#080C14`, `#0F172A`) with monospaced financial typography.
- Clean Light Mode: Minimalist paper and crisp charcoal palette for daytime institutional reporting.
- Persistent client-side preference stored via `localStorage` with zero theme flickering.

---

## Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Backend Engine** | Python 3.10+, Flask | Lightweight WSGI controller & routing |
| **Data & Analytics** | `yfinance`, `pandas`, `math` | Historical time series & technical indicator calculus |
| **Visualization** | `plotly` Graph Objects | High-performance responsive financial charts |
| **Frontend Architecture** | Jinja2 Templates (Modular) | Atomic component partials with clean separation |
| **Styling & Design** | CSS3 Custom Properties, Bootstrap 5 | Pure vanilla CSS tokens for seamless dual-mode support |
| **Typography** | Google Fonts | *Plus Jakarta Sans*, *Inter*, and *JetBrains Mono* |
| **Edge Deployment** | Vercel Serverless Edge | Configured via `vercel.json` rewrite rules |

---

## Project Architecture

The codebase adheres to a modular, decoupled architecture separating business logic, static assets, and template partials:

```
monitor stocks/
├── api/
│   ├── index.py                  # Flask application controller & HTTP routing
│   └── stock_service.py          # Data ingestion, indicator calculus & charting engine
├── static/
│   ├── css/
│   │   └── style.css             # Central Design System & Dual-Theme CSS variables
│   └── js/
│       └── app.js                # Theme switcher & client interaction helpers
├── templates/
│   ├── base.html                 # Master layout shell (head, metadata, fonts, scripts)
│   ├── index.html                # Main dashboard view orchestrating component partials
│   └── components/               # Isolated modular Jinja2 partials
│       ├── _header.html          # Brand navbar, market indicator & theme switch
│       ├── _search_form.html     # Ticker search, portfolio inputs & quick pills
│       ├── _fundamental.html     # 6-card executive KPI financial scoreboard
│       ├── _price_banner.html    # Stock price hero, day change & DSS signal badge
│       ├── _company_profile.html # Business summary & sector classification
│       ├── _chart.html           # Interactive Candlestick & Bollinger Bands container
│       ├── _insight.html         # AI Decision Support insight commentary box
│       ├── _portfolio.html       # Ledger-style portfolio return calculator
│       ├── _trend_strength.html  # Trend strength power meter card
│       ├── _bullish_scanner.html # Watchlist momentum scanner card
│       ├── _news.html            # Financial news wire feed
│       ├── _indicator_guide.html # Technical methodology & reference documentation
│       ├── _error_banner.html    # Graceful fallback state for invalid tickers
│       └── _footer.html          # Institutional disclaimer & copyright
├── requirements.txt              # Python package dependencies
├── vercel.json                   # Serverless edge function routing configuration
└── README.md                     # Project documentation
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
```
http://127.0.0.1:5000
```

---

## Technical Indicator Methodology

### 1. Bollinger Bands ($N = 20, K = 2$)

$$\text{MA20} = \frac{1}{20} \sum_{i=1}^{20} \text{Close}_i$$

$$\sigma = \sqrt{\frac{1}{20} \sum_{i=1}^{20} (\text{Close}_i - \text{MA20})^2}$$

$$\text{Upper Band} = \text{MA20} + 2\sigma, \quad \text{Lower Band} = \text{MA20} - 2\sigma$$

### 2. Relative Strength Index (RSI, 14-period)

$$\text{RS} = \frac{\text{Average Gain}}{\text{Average Loss}}$$

$$\text{RSI} = 100 - \left( \frac{100}{1 + \text{RS}} \right)$$

### 3. Quantitative Trend Strength Algorithm

A composite multi-factor scoring model ($0\% \text{ to } 100\%$) evaluating three core technical dimensions:
- **Trend Baseline**: Price position relative to MA20 ($+20\% \text{ / } -15\%$).
- **Momentum Filter**: RSI oversold bounce reward ($+20\%$) vs. overbought extension penalty ($-20\%$).
- **Volatility Boundary**: Bollinger lower support proximity ($+10\%$) vs. upper resistance rejection ($-10\%$).

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

Notice: StockPulse Pro is an analytical Decision Support System (DSS) developed exclusively for informational and research purposes. It does not constitute financial, investment, or trading advice. Past performance is no guarantee of future market returns. Capital market investments involve risk; market participants should conduct independent due diligence before executing trades.

---

## License

This project is licensed under the [MIT License](LICENSE) &copy; 2026 StockPulse Pro.
