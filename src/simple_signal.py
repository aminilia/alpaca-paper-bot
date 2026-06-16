import os
from datetime import datetime, timedelta, timezone

import pandas as pd
from dotenv import load_dotenv
from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame


def get_daily_bars(symbol: str, lookback_days: int = 120) -> pd.DataFrame:
    """Fetch daily stock bars from Alpaca's free-compatible IEX feed."""
    load_dotenv()

    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        raise RuntimeError("Missing Alpaca API keys in .env file.")

    client = StockHistoricalDataClient(api_key, secret_key)

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)

    request = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        feed=DataFeed.IEX,
    )

    try:
        bars = client.get_stock_bars(request).df
    except Exception as exc:
        raise RuntimeError(f"Could not fetch IEX market data for {symbol}: {exc}") from exc

    if bars.empty:
        raise RuntimeError(f"No market data returned for {symbol}.")

    # Alpaca usually returns a MultiIndex: symbol, timestamp
    if isinstance(bars.index, pd.MultiIndex):
        bars = bars.xs(symbol)

    return bars


def generate_signal(symbol: str) -> str:
    """Calculate moving averages and return a descriptive, non-trading signal."""
    bars = get_daily_bars(symbol)
    bars["ma20"] = bars["close"].rolling(20).mean()
    bars["ma50"] = bars["close"].rolling(50).mean()

    latest = bars.iloc[-1]

    close = latest["close"]
    ma20 = latest["ma20"]
    ma50 = latest["ma50"]

    print(f"Symbol: {symbol}")
    print(f"Latest close: {close:.2f}")
    print(f"MA20: {ma20:.2f}")
    print(f"MA50: {ma50:.2f}")

    if pd.isna(ma20) or pd.isna(ma50):
        return "HOLD: not enough data"

    if close > ma20 > ma50:
        return "STRONG BULLISH: close > MA20 > MA50"

    if ma20 > ma50 and close < ma20:
        return "WEAK BULLISH: MA20 > MA50, but price is below MA20"

    if close < ma20 < ma50:
        return "BEARISH: close < MA20 < MA50"

    if close < ma50:
        return "WEAK BEARISH: price is below MA50"

    return "HOLD: unclear trend"


def get_symbols_from_env() -> list[str]:
    raw_symbols = os.getenv("SYMBOLS", "SPY")
    return [symbol.strip().upper() for symbol in raw_symbols.split(",") if symbol.strip()]


def main() -> None:
    symbols = get_symbols_from_env()

    for symbol in symbols:
        print("-" * 50)

        try:
            signal = generate_signal(symbol)
        except RuntimeError as exc:
            print(f"Error for {symbol}: {exc}")
            continue

        print(f"Signal: {signal}")

    print("-" * 50)
    print("Informational only. No orders were submitted.")


if __name__ == "__main__":
    main()