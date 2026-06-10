import os

from dotenv import load_dotenv
from alpaca.trading.client import TradingClient


def main() -> None:
    """Connect to Alpaca's paper environment and print account details."""
    load_dotenv()

    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        print(
            "Error: Missing Alpaca API keys. Add ALPACA_API_KEY and "
            "ALPACA_SECRET_KEY to your .env file."
        )
        return

    try:
        # paper=True is the important safety switch: this never connects to live trading.
        trading_client = TradingClient(api_key, secret_key, paper=True)
        account = trading_client.get_account()
    except Exception as exc:
        print(f"Error: Could not connect to the Alpaca paper account: {exc}")
        return

    print("Connected to Alpaca paper account.")
    print(f"Account status: {account.status}")
    print(f"Cash: {account.cash}")
    print(f"Buying power: {account.buying_power}")
    print(f"Portfolio value: {account.portfolio_value}")
    print("No orders were submitted.")


if __name__ == "__main__":
    main()
