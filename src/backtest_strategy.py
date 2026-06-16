import os
import csv
import importlib
from datetime import datetime, timezone
from pathlib import Path

from backtesting import Backtest, Strategy

from simple_signal import get_daily_bars


STRATEGY_MODULES = {
    "ma": "strategy_ma",
    "rsi": "strategy_rsi",
    "macd": "strategy_macd",
    "trend_rsi": "strategy_trend_rsi",
}


def prepare_backtest_data(symbol: str, lookback_days: int):
    bars = get_daily_bars(symbol, lookback_days=lookback_days)

    data = bars.rename(
        columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
    )

    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    data = data[required_columns].dropna()

    return data


def load_strategy(strategy_name: str):
    strategy_name = strategy_name.strip().lower()

    if strategy_name not in STRATEGY_MODULES:
        valid = ", ".join(STRATEGY_MODULES.keys())
        raise ValueError(f"Unknown strategy '{strategy_name}'. Valid options: {valid}")

    module_name = STRATEGY_MODULES[strategy_name]
    module = importlib.import_module(module_name)
    strategy_class = getattr(module, "STRATEGY_CLASS", None)

    if not isinstance(strategy_class, type) or not issubclass(strategy_class, Strategy):
        raise TypeError(
            f"Strategy module '{module_name}' must expose STRATEGY_CLASS as a "
            "backtesting.Strategy subclass"
        )

    return strategy_class


def get_log_dir() -> Path:
    log_dir = Path(os.getenv("LOG_DIR", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def clean_stat_value(value):
    """
    Convert Backtesting.py / pandas / numpy values into CSV-safe values.
    Because apparently numbers now need emotional support before entering a file.
    """
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    if value is None:
        return ""

    return str(value)


def append_row_to_csv(csv_path: Path, row: dict) -> None:
    file_exists = csv_path.exists()

    with csv_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


def save_backtest_summary(
    symbol: str,
    strategy_name: str,
    lookback_days: int,
    cash: float,
    commission: float,
    stats,
) -> None:
    log_dir = get_log_dir()
    csv_path = log_dir / "backtest_summary.csv"

    row = {
        "run_time_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "strategy": strategy_name,
        "lookback_days": lookback_days,
        "starting_cash": cash,
        "commission": commission,
        "start": clean_stat_value(stats.get("Start")),
        "end": clean_stat_value(stats.get("End")),
        "duration": clean_stat_value(stats.get("Duration")),
        "exposure_time_pct": clean_stat_value(stats.get("Exposure Time [%]")),
        "equity_final": clean_stat_value(stats.get("Equity Final [$]")),
        "equity_peak": clean_stat_value(stats.get("Equity Peak [$]")),
        "return_pct": clean_stat_value(stats.get("Return [%]")),
        "buy_hold_return_pct": clean_stat_value(stats.get("Buy & Hold Return [%]")),
        "return_ann_pct": clean_stat_value(stats.get("Return (Ann.) [%]")),
        "cagr_pct": clean_stat_value(stats.get("CAGR [%]")),
        "sharpe_ratio": clean_stat_value(stats.get("Sharpe Ratio")),
        "sortino_ratio": clean_stat_value(stats.get("Sortino Ratio")),
        "max_drawdown_pct": clean_stat_value(stats.get("Max. Drawdown [%]")),
        "num_trades": clean_stat_value(stats.get("# Trades")),
        "win_rate_pct": clean_stat_value(stats.get("Win Rate [%]")),
        "best_trade_pct": clean_stat_value(stats.get("Best Trade [%]")),
        "worst_trade_pct": clean_stat_value(stats.get("Worst Trade [%]")),
        "avg_trade_pct": clean_stat_value(stats.get("Avg. Trade [%]")),
        "profit_factor": clean_stat_value(stats.get("Profit Factor")),
    }

    append_row_to_csv(csv_path, row)
    print(f"Saved backtest summary to: {csv_path}")


def save_backtest_trades(symbol: str, strategy_name: str, stats) -> None:
    log_dir = get_log_dir()
    csv_path = log_dir / f"trades_{symbol}_{strategy_name}.csv"

    trades = stats.get("_trades")

    if trades is None or trades.empty:
        print("No trades to save.")
        return

    trades = trades.copy()
    trades.insert(0, "run_time_utc", datetime.now(timezone.utc).isoformat())
    trades.insert(1, "symbol", symbol)
    trades.insert(2, "strategy", strategy_name)

    trades.to_csv(csv_path, index=False)
    print(f"Saved trade details to: {csv_path}")


def main() -> None:
    symbol = os.getenv("SYMBOL", "SPY").upper()
    strategy_name = os.getenv("STRATEGY", "trend_rsi").lower()
    lookback_days = int(os.getenv("BACKTEST_LOOKBACK_DAYS", "2000"))
    cash = float(os.getenv("BACKTEST_CASH", "10000"))
    commission = float(os.getenv("BACKTEST_COMMISSION", "0.002"))

    print(f"Running backtest for: {symbol}")
    print(f"Strategy: {strategy_name}")
    print(f"Lookback days: {lookback_days}")
    print(f"Starting cash: {cash}")
    print(f"Commission: {commission}")

    strategy_class = load_strategy(strategy_name)
    data = prepare_backtest_data(symbol, lookback_days)

    print(f"First available bar: {data.index.min()}")
    print(f"Last available bar: {data.index.max()}")
    print(f"Number of daily bars: {len(data)}")

    bt = Backtest(
        data,
        strategy_class,
        cash=cash,
        commission=commission,
        exclusive_orders=True,
        finalize_trades=True,
    )

    stats = bt.run()

    print("\nBacktest results:")
    print(stats)

    save_backtest_summary(
       symbol=symbol,
       strategy_name=strategy_name,
       lookback_days=lookback_days,
       cash=cash,
       commission=commission,
       stats=stats,
    )

    save_backtest_trades(
       symbol=symbol,
       strategy_name=strategy_name,
       stats=stats,
)

if __name__ == "__main__":
    main()
