# Beginner Alpaca Paper Trading Project

This small Python project safely introduces the Alpaca API. It connects only to
an Alpaca **paper trading** account, reads account information, and downloads
SPY daily market data from the IEX feed.

It does **not** submit orders and contains no live-trading code.

## What is included

- `src/check_alpaca.py`: verifies the paper-account connection and displays a
  few account values.
- `src/simple_signal.py`: downloads SPY daily bars from IEX, calculates the
  20-day and 50-day moving averages, and prints a descriptive signal.

## Prerequisites

- Python 3.10 or newer
- An Alpaca paper trading account
- Paper API keys from the Alpaca dashboard

Use paper-account keys only. Do not use live-account credentials.

## Setup

From this project directory, create and activate a virtual environment.

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then replace the placeholders with your Alpaca
paper API keys:

```env
ALPACA_API_KEY=your_paper_api_key_here
ALPACA_SECRET_KEY=your_paper_secret_key_here
```

The `.env` file is ignored by Git. Never commit or share it.

## Run the safe scripts

Verify the paper-account connection:

```powershell
python src/check_alpaca.py
```

Calculate SPY's 20-day and 50-day moving averages using the IEX data feed:

```powershell
python src/simple_signal.py
```

The signal output is educational information only. Neither script creates,
modifies, or submits an order.

## Safety choices

- API keys are loaded from `.env`, never hard-coded.
- `TradingClient` is created with `paper=True`.
- Stock bars explicitly use `DataFeed.IEX` for free paper-data compatibility.
- There are no order-submission calls in this project.
