import os
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from simple_signal import get_daily_bars
from risk_filters import allow_new_long_trade, place_long_with_risk, close_if_time_stop

def sma(values, n):
    """Simple moving average helper for Backtesting.py."""
    return pd.Series(values).rolling(n).mean()


class SmaCrossStrategy(Strategy):
    n_fast = 20   # fast average
    n_slow = 50   # slow average

    position_size = 0.25
    stop_loss_pct = 0.08
    take_profit_pct = 0.20
    max_account_drawdown_pct = 0.20
    max_trade_bars = 60

    def init(self):
        close = self.data.Close
        self.ma_fast = self.I(sma, close, self.n_fast)
        self.ma_slow = self.I(sma, close, self.n_slow)

    def next(self):
        close_if_time_stop(self)

        if crossover(self.ma_fast, self.ma_slow):
            if allow_new_long_trade(self):
                place_long_with_risk(self)

        elif crossover(self.ma_slow, self.ma_fast):
            self.position.close()


def prepare_backtest_data(symbol: str, lookback_days: int) -> pd.DataFrame:
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


def main() -> None:
    symbol = os.getenv("SYMBOL", "SPY").upper()
    lookback_days = int(os.getenv("BACKTEST_LOOKBACK_DAYS", "2000"))
    cash = float(os.getenv("BACKTEST_CASH", "10000"))
    commission = float(os.getenv("BACKTEST_COMMISSION", "0.002"))

    print(f"Running backtest for: {symbol}")
    print(f"Lookback days: {lookback_days}")
    print(f"Starting cash: {cash}")
    print(f"Commission: {commission}")

    data = prepare_backtest_data(symbol, lookback_days)

    print(f"First available bar: {data.index.min()}")
    print(f"Last available bar: {data.index.max()}")
    print(f"Number of daily bars: {len(data)}")

    bt = Backtest(
        data,
        SmaCrossStrategy,
        cash=cash,
        commission=commission,
        exclusive_orders=True,
        finalize_trades=True,
    )

    stats = bt.run()

    print("\nBacktest results:")
    print(stats)


STRATEGY_CLASS = SmaCrossStrategy