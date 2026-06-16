def get_starting_equity(strategy):
    """
    Store starting equity the first time the strategy runs.
    """
    if not hasattr(strategy, "_starting_equity"):
        strategy._starting_equity = strategy.equity

    return strategy._starting_equity


def account_drawdown_exceeded(strategy) -> bool:
    """
    Stop new trades if account equity falls too much from starting equity.
    """
    starting_equity = get_starting_equity(strategy)
    max_drawdown_pct = getattr(strategy, "max_account_drawdown_pct", 0.20)

    min_allowed_equity = starting_equity * (1 - max_drawdown_pct)

    return strategy.equity <= min_allowed_equity


def close_if_time_stop(strategy) -> None:
    """
    Close trades that have been open too long.
    """
    max_trade_bars = getattr(strategy, "max_trade_bars", None)

    if max_trade_bars is None:
        return

    current_bar = len(strategy.data.Close) - 1

    for trade in strategy.trades:
        bars_held = current_bar - trade.entry_bar

        if bars_held >= max_trade_bars:
            trade.close()


def allow_new_long_trade(strategy) -> bool:
    """
    Decide whether a new long trade is allowed.
    """
    if account_drawdown_exceeded(strategy):
        if strategy.position:
            strategy.position.close()

        return False

    if strategy.position:
        return False

    return True


def place_long_with_risk(strategy):
    """
    Place a long order with position size, stop-loss, and take-profit.
    """
    close = float(strategy.data.Close[-1])

    position_size = getattr(strategy, "position_size", 0.25)
    stop_loss_pct = getattr(strategy, "stop_loss_pct", 0.08)
    take_profit_pct = getattr(strategy, "take_profit_pct", 0.20)

    stop_loss_price = close * (1 - stop_loss_pct) if stop_loss_pct > 0 else None
    take_profit_price = close * (1 + take_profit_pct) if take_profit_pct > 0 else None

    return strategy.buy(
        size=position_size,
        sl=stop_loss_price,
        tp=take_profit_price,
    )