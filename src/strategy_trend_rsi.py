import pandas as pd
from backtesting import Strategy
from risk_filters import allow_new_long_trade, place_long_with_risk, close_if_time_stop

def sma(values, period: int):
    """Calculate simple moving average."""
    return pd.Series(values).rolling(period).mean().to_numpy()


def rsi(values, period: int = 14):
    """Calculate Relative Strength Index without external TA libraries."""
    series = pd.Series(values)

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    rs = avg_gain / avg_loss
    result = 100 - (100 / (1 + rs))

    return result.to_numpy()


class TrendRsiStrategy(Strategy):
    """
    Trend + RSI strategy.

    Buy condition:
    - Close > MA50 > MA200
    - RSI is between 50 and 70

    Exit condition:
    - Close falls below MA50
    - RSI falls below 45
    - RSI rises above 80
    """

    ma_fast_period = 50
    ma_slow_period = 200

    rsi_period = 14
    rsi_buy_min = 50
    rsi_buy_max = 70
    rsi_exit_low = 45
    rsi_exit_high = 80

    position_size = 0.25
    stop_loss_pct = 0.08
    take_profit_pct = 0.20
    max_account_drawdown_pct = 0.20
    max_trade_bars = 60

    def init(self):
        close = self.data.Close

        self.ma_fast = self.I(sma, close, self.ma_fast_period)
        self.ma_slow = self.I(sma, close, self.ma_slow_period)
        self.rsi = self.I(rsi, close, self.rsi_period)

    def next(self):
        close_if_time_stop(self)

        close = self.data.Close[-1]
        ma_fast = self.ma_fast[-1]
        ma_slow = self.ma_slow[-1]
        current_rsi = self.rsi[-1]

        if pd.isna(ma_fast) or pd.isna(ma_slow) or pd.isna(current_rsi):
            return

        in_uptrend = close > ma_fast > ma_slow
        healthy_momentum = self.rsi_buy_min < current_rsi < self.rsi_buy_max

        if not self.position and in_uptrend and healthy_momentum:
            if allow_new_long_trade(self):
                place_long_with_risk(self)

        elif self.position:
            trend_broken = close < ma_fast
            momentum_failed = current_rsi < self.rsi_exit_low
            too_overbought = current_rsi > self.rsi_exit_high

            if trend_broken or momentum_failed or too_overbought:
                self.position.close()


STRATEGY_CLASS = TrendRsiStrategy