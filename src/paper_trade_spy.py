import os
from decimal import Decimal

from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from simple_signal import generate_signal


SYMBOL = "SPY"
QTY = 1


def main() -> None:
    load_dotenv()

    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    enable_orders = os.getenv("ENABLE_PAPER_ORDERS", "false").lower() == "true"

    if not api_key or not secret_key:
        raise RuntimeError("Missing Alpaca API keys in .env file.")

    trading_client = TradingClient(api_key, secret_key, paper=True)
    account = trading_client.get_account()

    print("Connected to Alpaca paper account.")
    print(f"Portfolio value: {account.portfolio_value}")
    print(f"Cash: {account.cash}")

    signal = generate_signal(SYMBOL)
    print(f"Signal: {signal}")

    if not enable_orders:
        print("ENABLE_PAPER_ORDERS=false, so no order was submitted.")
        return

    if not signal.startswith("STRONG BULLISH"):
        print("Signal is not STRONG BULLISH, so no order was submitted.")
        return

    # Tiny risk check. Do not let the paper bot go wild like a raccoon in a brokerage account.
    cash = Decimal(str(account.cash))
    if cash < Decimal("1000"):
        print("Cash is below $1,000. No order submitted.")
        return

    order = MarketOrderRequest(
        symbol=SYMBOL,
        qty=QTY,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
    )

    submitted_order = trading_client.submit_order(order)
    print("Paper order submitted.")
    print(f"Order ID: {submitted_order.id}")
    print(f"Symbol: {SYMBOL}")
    print(f"Quantity: {QTY}")
    print("Side: BUY")


if __name__ == "__main__":
    main()