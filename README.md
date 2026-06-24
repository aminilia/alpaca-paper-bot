# Alpaca Paper Bot

A Python and Docker-based paper-trading sandbox for testing stock-market signals, strategy backtests, and basic risk controls using the Alpaca API.

This project is designed as an educational framework for learning how algorithmic trading systems are structured before risking real money. It connects to an Alpaca paper trading account, downloads historical daily stock data, generates simple trading signals, runs strategy backtests, and can optionally submit paper orders only when explicitly enabled.

> **Important:** This project is for education, research, and software-development practice only. It is not financial advice and it is not a live-trading system.

---

## Features

* Connects to Alpaca paper trading accounts
* Downloads daily stock market data using Alpaca's IEX-compatible data feed
* Generates simple moving-average trend signals
* Runs backtests using `backtesting.py`
* Supports multiple strategy modules
* Includes basic risk filters
* Saves backtest summaries and trade logs to CSV
* Supports Docker and Docker Compose
* Keeps API keys outside the repository using a `.env` file

---

## Project Structure

```text id="vfjrds"
alpaca-paper-bot/
│
├── src/
│   ├── check_alpaca.py
│   ├── simple_signal.py
│   ├── paper_trade_spy.py
│   ├── history_check.py
│   ├── backtest_strategy.py
│   ├── risk_filters.py
│   ├── strategy_ma.py
│   ├── strategy_macd.py
│   ├── strategy_rsi.py
│   └── strategy_trend_rsi.py
│
├── logs/
│
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── .gitignore
├── .dockerignore
└── README.md
```

---

## Main Scripts

### `check_alpaca.py`

Checks whether the Alpaca API credentials are working and confirms that the project can connect to the paper trading account.

It prints:

* Account status
* Cash
* Buying power
* Portfolio value

No orders are submitted by this script.

---

### `simple_signal.py`

Downloads daily stock data and calculates a simple moving-average signal using:

* Latest close price
* 20-day moving average
* 50-day moving average

The script classifies the symbol into basic signal categories such as:

* `STRONG BULLISH`
* `WEAK BULLISH`
* `BEARISH`
* `WEAK BEARISH`
* `HOLD`

This script is informational only and does not submit orders.

---

### `history_check.py`

Checks how much historical daily data is available for one or more stock symbols.

This is useful before running backtests because some strategies require longer lookback periods, especially those using slow moving averages such as MA200.

---

### `paper_trade_spy.py`

A controlled paper-order test for SPY.

By default, this script does **not** submit orders. Paper orders are only allowed when:

```text id="kigopz"
ENABLE_PAPER_ORDERS=true
```

Even then, the script only submits a small paper buy order if the signal condition is strong enough.

---

### `backtest_strategy.py`

Runs a backtest for a selected strategy and stock symbol.

Supported strategy names:

```text id="g845o2"
ma
rsi
macd
trend_rsi
```

Recommended starting strategies:

```text id="xhh8fr"
ma
macd
trend_rsi
```

Backtest results are printed in the terminal and saved to CSV files in the `logs/` folder.

---

## Strategy Modules

### Moving Average Strategy

**File:** `strategy_ma.py`

A simple moving-average crossover strategy.

Default logic:

* Buy when the fast moving average crosses above the slow moving average
* Close the position when the slow moving average crosses above the fast moving average

Default moving averages:

```text id="ydv01r"
Fast MA: 20
Slow MA: 50
```

---

### MACD Strategy

**File:** `strategy_macd.py`

A basic MACD crossover strategy.

Default logic:

* Buy when the MACD line crosses above the signal line
* Close the position when the signal line crosses above the MACD line

Default MACD parameters:

```text id="m75foi"
Fast EMA: 12
Slow EMA: 26
Signal EMA: 9
```

---

### Trend + RSI Strategy

**File:** `strategy_trend_rsi.py`

A trend-following strategy combined with RSI momentum filtering.

Default buy condition:

```text id="yn2b1x"
Close > MA50 > MA200
RSI between 50 and 70
```

Default exit conditions:

```text id="j1fqml"
Close falls below MA50
RSI falls below 45
RSI rises above 80
```

This is currently the most complete strategy structure in the repository.

---

## Risk Filters

The project includes a shared `risk_filters.py` module used by the strategy files.

Default risk controls include:

```text id="xt79ps"
Position size: 25% of equity
Stop loss: 8%
Take profit: 20%
Maximum account drawdown: 20%
Maximum trade duration: 60 bars
```

These values are experimental defaults and should be adjusted carefully before testing new strategies.

---

## Installation

### Option 1: Run locally with Python

Create and activate a virtual environment:

```bash id="gek8us"
python -m venv .venv
```

On Windows PowerShell:

```bash id="lr8vl9"
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash id="tdurdi"
source .venv/bin/activate
```

Install dependencies:

```bash id="sirzrk"
pip install -r requirements.txt
```

---

### Option 2: Run with Docker

Build and run scripts using Docker Compose:

```bash id="xl4a6q"
docker compose build
```

---

## Environment Variables

Create a `.env` file in the root folder:

```text id="jden0n"
ALPACA_API_KEY=your_paper_api_key_here
ALPACA_SECRET_KEY=your_paper_secret_key_here

ENABLE_PAPER_ORDERS=false

SYMBOL=SPY
SYMBOLS=SPY,QQQ,AAPL

STRATEGY=trend_rsi
BACKTEST_LOOKBACK_DAYS=2000
BACKTEST_CASH=10000
BACKTEST_COMMISSION=0.002
```

Never commit your `.env` file to GitHub.

The repository is already configured to ignore `.env`, but always double-check before pushing. Accidentally publishing API keys is one of those small disasters that makes computers feel smug.

---

## Usage

### Check Alpaca paper account connection

Local Python:

```bash id="t3chz8"
python src/check_alpaca.py
```

Docker Compose:

```bash id="tx98td"
docker compose run --rm alpaca-check
```

---

### Generate a simple signal

Local Python:

```bash id="bfskmk"
python src/simple_signal.py
```

Docker Compose:

```bash id="ch5vdh"
docker compose run --rm signal-spy
```

To check multiple symbols, edit `.env`:

```text id="l2jpwo"
SYMBOLS=SPY,QQQ,AAPL
```

---

### Check historical data availability

Local Python:

```bash id="soow1a"
python src/history_check.py
```

Docker Compose:

```bash id="uzmg24"
docker compose run --rm history-check
```

---

### Run a backtest

Local Python:

```bash id="d62r9b"
python src/backtest_strategy.py
```

Docker Compose:

```bash id="m0vzlp"
docker compose run --rm backtest-strategy
```

Run a specific strategy and symbol:

```bash id="hgjaka"
docker compose run --rm -e SYMBOL=SPY -e STRATEGY=trend_rsi backtest-strategy
```

Other strategy examples:

```bash id="muwkak"
docker compose run --rm -e SYMBOL=SPY -e STRATEGY=ma backtest-strategy
docker compose run --rm -e SYMBOL=SPY -e STRATEGY=macd backtest-strategy
```

---

### Run the controlled paper-order test

By default, no paper order is submitted:

```bash id="x2wr3w"
docker compose run --rm paper-trade-spy
```

To allow paper orders, set this in `.env`:

```text id="c7q7jr"
ENABLE_PAPER_ORDERS=true
```

This still does not guarantee that an order will be submitted. The script only submits a small paper order if the signal condition passes.

---

## Backtest Outputs

Backtest results are saved in the `logs/` folder.

Typical outputs:

```text id="ec1leb"
logs/backtest_summary.csv
logs/trades_SPY_trend_rsi.csv
```

The summary file includes fields such as:

* Symbol
* Strategy
* Starting cash
* Commission
* Return
* Buy-and-hold return
* Sharpe ratio
* Max drawdown
* Number of trades
* Win rate
* Profit factor

---

## Current Dependencies

Main Python packages:

```text id="bafz3a"
alpaca-py
python-dotenv
pandas
backtesting
```

---

## Safety Notes

This project is intentionally designed around paper trading.

Current safety choices:

* Uses Alpaca paper mode
* Stores credentials in `.env`
* Keeps `.env` out of Git
* Does not submit orders unless explicitly enabled
* Includes simple cash and signal checks before paper orders
* Uses basic risk filters in backtests

This project should not be connected to live trading without major review, testing, logging, monitoring, and additional risk management.

---

## Limitations

This is an educational prototype, not a production trading system.

Current limitations include:

* Strategies are simple and experimental
* Backtests use daily data only
* Transaction cost modeling is basic
* No slippage model beyond commission settings
* No portfolio optimization
* No live monitoring dashboard
* No news, earnings, macro, or options data
* No production-grade order management
* No automated deployment pipeline
* Strategy performance is not evidence of future profitability

---

## Future Improvements

Possible next steps:

* Add an `.env.example` file
* Add unit tests for signal and strategy logic
* Add plots for equity curves and drawdowns
* Add strategy parameter optimization
* Add walk-forward validation
* Add paper-trading logs
* Add portfolio-level risk controls
* Add support for multiple symbols in backtesting
* Add scheduled paper-trading runs
* Add GitHub Actions for basic code checks
* Add a dashboard using Streamlit or Plotly Dash
* Add Dockerized notebooks for research
* Add documentation for strategy assumptions

---

## Suggested Repository Description

```text id="c2yl0r"
Python/Docker paper-trading and backtesting sandbox using Alpaca API, IEX data, moving-average, RSI, MACD strategies, and basic risk filters.
```

---

## Suggested GitHub Topics

```text id="qz55zx"
python
alpaca
alpaca-api
paper-trading
algorithmic-trading
trading-bot
backtesting
quantitative-finance
stock-market
docker
docker-compose
risk-management
moving-average
rsi
macd
```

---

## Author

**Amin Ilia**

This project is part of a broader portfolio in Python automation, data analysis, scientific computing, Docker-based workflows, and applied algorithmic trading research.
