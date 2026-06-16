import os

from simple_signal import get_daily_bars


def get_symbols_from_env() -> list[str]:
    raw_symbols = os.getenv("SYMBOLS", "SPY")
    return [symbol.strip().upper() for symbol in raw_symbols.split(",") if symbol.strip()]


def main() -> None:
    symbols = get_symbols_from_env()
    lookback_days = int(os.getenv("HISTORY_LOOKBACK_DAYS", "4000"))

    print(f"Checking history using lookback_days={lookback_days}")

    for symbol in symbols:
        print("-" * 60)
        print(f"Symbol: {symbol}")

        try:
            bars = get_daily_bars(symbol, lookback_days=lookback_days)
        except RuntimeError as exc:
            print(f"Error: {exc}")
            continue

        print(f"First bar: {bars.index.min()}")
        print(f"Last bar: {bars.index.max()}")
        print(f"Number of bars: {len(bars)}")


if __name__ == "__main__":
    main()