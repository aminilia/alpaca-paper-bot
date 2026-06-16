import pandas as pd
from backtesting import Strategy
from backtesting.lib import crossover
from risk_filters import allow_new_long_trade, place_long_with_risk, close_if_time_stop


def ema(values, period: int):
    """Calculate exponential moving average."""
    return pd.Series(values).ewm(span=period, adjust=False).mean().to_numpy()


def macd_line(values, fast_period: int = 12, slow_period: int = 26):
    """Calculate MACD line: EMA fast - EMA slow."""
    series = pd.Series(values)

    fast_ema = series.ewm(span=fast_period, adjust=False).mean()
    slow_ema = series.ewm(span=slow_period, adjust=False).mean()

    return (fast_ema - slow_ema).to_numpy()


def macd_signal(values, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
    """Calculate MACD signal line."""
    line = macd_line(values, fast_period, slow_period)
    return pd.Series(line).ewm(span=signal_period, adjust=False).mean().to_numpy()


class MacdStrategy(Strategy):
    """
    Basic MACD crossover strategy.

    Buy when MACD line crosses above signal line.
    Sell/close when MACD line crosses below signal line.
    """

    fast_period = 12
    slow_period = 26
    signal_period = 9
    position_size = 0.25
    stop_loss_pct = 0.08
    take_profit_pct = 0.20
    max_account_drawdown_pct = 0.20
    max_trade_bars = 60

    def init(self):
        close = self.data.Close

        self.macd = self.I(
            macd_line,
            close,
            self.fast_period,
            self.slow_period,
        )

        self.signal = self.I(
            macd_signal,
            close,
            self.fast_period,
            self.slow_period,
            self.signal_period,
        )

    def next(self):
        close_if_time_stop(self)

        current_macd = self.macd[-1]
        current_signal = self.signal[-1]

        if pd.isna(current_macd) or pd.isna(current_signal):
            return

        if crossover(self.macd, self.signal):
            if allow_new_long_trade(self):
                place_long_with_risk(self)

        elif crossover(self.signal, self.macd):
            self.position.close()


STRATEGY_CLASS = MacdStrategy