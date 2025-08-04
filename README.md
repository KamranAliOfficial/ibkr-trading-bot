IBKR Stateful Trading Bot
This is an optimized, asynchronous trading bot built with Python, Quart, and ib_insync to interact with Interactive Brokers (IBKR) for automated trading. It supports webhook-based trade signals, maintains a trade journal in SQLite, and provides a web dashboard for monitoring account status and trade logs.
Features

Asynchronous Architecture: Uses Quart and aiosqlite for non-blocking operations, improving performance.
Trade Journal: Stores trade details (symbol, signal, position size, entry/exit prices, take-profit, stop-loss) in a SQLite database.
Webhook Support: Accepts JSON-based trade signals to open or close positions.
Interactive Brokers Integration: Places market, take-profit, and stop-loss orders via IBKR's API.
Dashboard: Displays account values, open positions, and trade logs via a web interface.
Trade Logic: Prevents re-entry after take-profit, supports position reversals, and ensures one active trade per symbol.
Error Handling: Includes retry logic for IBKR connections and robust exception management.

Prerequisites

Python 3.8+
Interactive Brokers Trader Workstation (TWS) or IB Gateway running locally
Required Python packages:pip install quart aiosqlite ib_insync



Setup

Clone the Repository:
git clone <repository-url>
cd ibkr-trading-bot


Install Dependencies:
pip install -r requirements.txt

Create a requirements.txt with:
quart
aiosqlite
ib_insync


Configure IBKR TWS/IB Gateway:

Enable API access in TWS/IB Gateway settings.
Set the API port (default: 7497 for TWS paper trading).
Allow connections from 127.0.0.1.


Create the Dashboard Template:

Ensure an index.html file exists in a templates/ directory. A basic example:<!DOCTYPE html>
<html>
<head>
    <title>Trading Bot Dashboard</title>
</head>
<body>
    <h1>Trading Bot Dashboard</h1>
    <h2>Status: {{ dashboard_data.status }}</h2>
    <h3>Account Values</h3>
    <ul>
        {% for key, value in dashboard_data.account.items() %}
        <li>{{ key }}: {{ value }}</li>
        {% endfor %}
    </ul>
    <h3>Positions</h3>
    <ul>
        {% for pos in dashboard_data.positions %}
        <li>{{ pos.symbol }}: {{ pos.position }} @ {{ pos.avgCost }}</li>
        {% endfor %}
    </ul>
    <h3>Trade Log</h3>
    <ul>
        {% for log in trade_log %}
        <li>{{ log.timestamp }} - {{ log.symbol }} - {{ log.action }}: {{ log.details }}</li>
        {% endfor %}
    </ul>
</body>
</html>




Initialize the Database:

The bot automatically creates a trade_state.db SQLite database on first run.



Usage

Run the Bot:
python trading_bot.py --flask-host 0.0.0.0 --flask-port 5001 --ib-host 127.0.0.1 --ib-port 7497 --ib-client-id 1


--flask-host: Host for the Quart web server (default: 0.0.0.0).
--flask-port: Port for the web server (default: 5001).
--ib-host: IBKR TWS/IB Gateway host (default: 127.0.0.1).
--ib-port: IBKR API port (default: 7497 for TWS paper trading).
--ib-client-id: Unique client ID for IBKR API (default: 1).


Access the Dashboard:

Open a browser and navigate to http://localhost:5001 to view account status, positions, and trade logs.


Send Trade Signals:

Send POST requests to http://localhost:5001/webhook with JSON payloads. Examples:
Open a position:{
  "action": "open",
  "symbol": "EURUSD",
  "side": "buy",
  "quantity": 10000,
  "tp": 1.20,
  "sl": 1.18
}


Close a position:{
  "action": "close",
  "symbol": "EURUSD"
}







Trade Logic

One Trade at a Time: Only one active trade per symbol is allowed.
Re-entry Protection: Prevents re-entering the same side after a take-profit is hit.
Reversals: Opposite signals close the current trade and open a new one.
Take-Profit/Stop-Loss: Optional TP/SL orders are placed with market orders.
Trade Journal: All trades are logged in the SQLite database with entry/exit prices, TP/SL, and status.

Database Schema
The trades table in trade_state.db includes:

id: Unique trade ID (auto-incremented).
timestamp: When the trade was opened.
symbol: Trading symbol (e.g., EURUSD, AAPL).
signal: Trade direction (buy or sell).
position_size: Trade quantity.
entry_order_id: IBKR order ID for the entry.
tp_order_id: IBKR order ID for take-profit.
entry_price: Filled entry price.
exit_price: Filled exit price (if closed).
tp_price: Take-profit price.
tp_hit: Whether the TP was hit (0 or 1).
closed: Whether the trade is closed (0 or 1).
sl_price: Stop-loss price.
sl_order_id: IBKR order ID for stop-loss.

Notes

Ensure TWS/IB Gateway is running before starting the bot.
The bot uses asynchronous operations for better performance but requires a compatible index.html template.
Logs are output to the console with timestamps and context for debugging.
The bot retries IBKR connections up to 3 times with a 5-second delay between attempts.

License
MIT License. See LICENSE for details.
