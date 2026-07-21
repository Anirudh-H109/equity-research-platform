# AI Equity Research Platform

An AI-powered equity research tool that analyzes US-listed stocks and generates 
professional research reports using financial data and a custom scoring engine.

## How It Works

1. Enter a stock ticker (e.g. AAPL, MSFT, NVDA)
2. The platform pulls live financial data via yfinance
3. A custom scoring engine evaluates 7 key metrics
4. An AI model generates a structured research report

## Scoring Engine

The platform scores companies across 7 metrics weighted by importance:

| Metric | Weight |
|--------|--------|
| Gross Margin | 1.5x |
| Net Margin | 1.5x |
| P/E Ratio | 1.5x |
| EV/EBITDA | 1.5x |
| ROE | 1x |
| Revenue Growth | 1x |
| Debt/Equity | 1x |

**Maximum score: 18 | Buy > 12 | Hold 6-12 | Sell < 6**

## Tech Stack

- Python
- yfinance (financial data)
- pandas (data processing)
- Groq API / LLaMA 3.3 70B (report generation)
- Streamlit (frontend)

## Limitations (v1)

- Supports US-listed equities only
- Scoring thresholds are universal (not sector-adjusted)
- No DCF/intrinsic valuation module

## Roadmap

- v2: Sector-specific scoring via sector.py
- v2: DCF valuation module
- v3: Portfolio tracker integration
- v3: Multi-stock comparison

```
GROQ_API_KEY = "your-key-here"
```
