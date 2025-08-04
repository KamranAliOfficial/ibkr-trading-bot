***IBKR Stateful Trading Bot 🚀***
  
A high-performance, asynchronous trading bot built with Python, Quart, and ib_insync for automated trading with Interactive Brokers (IBKR). It supports webhook-based trade signals, logs trades in a SQLite database, and provides a sleek web dashboard to monitor account status and trade activity. 📈
Placeholder: Add a GIF of the dashboard showing real-time updates (e.g., via Giphy or Imgur).

✨ Features

⚡ Asynchronous Architecture: Leverages Quart and aiosqlite for non-blocking operations, ensuring high performance.
📚 Trade Journal: Stores detailed trade records (symbol, signal, position size, entry/exit prices, TP/SL) in SQLite.
🌐 Webhook Support: Processes JSON trade signals to open/close positions.
🤝 IBKR Integration: Executes market, take-profit, and stop-loss orders via IBKR’s API.
📊 Web Dashboard: Displays account values, open positions, and trade logs in real time.
🔒 Trade Logic: Prevents re-entry after take-profit, supports reversals, and enforces one trade per symbol.
🛡️ Error Handling: Includes retry logic for IBKR connections and robust exception management.


📋 Prerequisites

🐍 Python 3.8+
💻 Interactive Brokers TWS or IB Gateway running locally
📦 Required Packages:pip install quart aiosqlite ib_insync




🛠️ Setup
1. Clone the Repository 📥
git clone https://github.com/<your-username>/ibkr-trading-bot.git
cd ibkr-trading-bot

2. Install Dependencies 📦
Create a requirements.txt file:
quart==0.19.4
aiosqlite==0.20.0
ib_insync==0.9.70

Then run:
pip install -r requirements.txt

3. Configure IBKR TWS/IB Gateway 🔧

Enable API access in TWS/IB Gateway settings.
Set the API port (default: 7497 for TWS paper trading).
Allow connections from 127.0.0.1.

4. Create the Dashboard Template 🎨
Create a templates/ directory and add index.html:
<!DOCTYPE html>
<html>
<head>
    <title>Trading Bot Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2, h3 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 10px 0; }
        .section { margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>Trading Bot Dashboard</h1>
    <div class="section">
        <h2>Status: {{ dashboard_data.status }}</h2>
    </div>
    <div class="section">
        <h3>Account Values</h3>
        <ul>
            {% for key, value in dashboard_data.account.items() %}
            <li>{{ key }}: {{ value }}</li>
            {% endfor %}
        </ul>
    </div>
    <div class="section">
        <h3>Positions</h3>
        <ul>
            {% for pos in dashboard_data.positions %}
            <li>{{ pos.symbol }}: {{ pos.position }} @ {{ pos.avgCost }}</li>
            {% endfor %}
        </ul>
    </div>
    <div class="section">
        <h3>Trade Log</h3>
        <ul>
            {% for log in trade_log %}
            <li>{{ log.timestamp }} - {{ log.symbol }} - {{ log.action }}: {{ log.details }}</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>

5. Initialize the Database 🗄️
The bot automatically creates a trade_state.db SQLite database on first run.

🚀 Usage
1. Run the Bot ▶️
python trading_bot.py --flask-host 0.0.0.0 --flask-port 5001 --ib-host 127.0.0.1 --ib-port 7497 --ib-client-id 1

Command-line Arguments:



Argument
Description
Default



--flask-host
Host for Quart web server
0.0.0.0


--flask-port
Port for web server
5001


--ib-host
IBKR TWS/IB Gateway host
127.0.0.1


--ib-port
IBKR API port
7497


--ib-client-id
Unique client ID for IBKR API
1


2. Access the Dashboard 🌐
Open your browser and navigate to:
http://localhost:5001

View real-time account status, open positions, and trade logs.
Placeholder: Add a GIF showing a webhook request and response (e.g., via Postman or curl).
3. Send Trade Signals 📡
Send POST requests to http://localhost:5001/webhook with JSON payloads.
Open a Position
{
  "action": "open",
  "symbol": "EURUSD",
  "side": "buy",
  "quantity": 10000,
  "tp": 1.20,
  "sl": 1.18
}

Close a Position
{
  "action": "close",
  "symbol": "EURUSD"
}

Example using curl:
curl -X POST -H "Content-Type: application/json" -d '{"action":"open","symbol":"EURUSD","side":"buy","quantity":10000,"tp":1.20,"sl":1.18}' http://localhost:5001/webhook


🧠 Trade Logic

🔐 One Trade at a Time: Only one active trade per symbol.
🚫 Re-entry Protection: Blocks re-entry on the same side after a take-profit hit.
🔄 Reversals: Opposite signals close the current trade and open a new one.
🎯 Take-Profit/Stop-Loss: Optional TP/SL orders are placed with market orders.
📝 Trade Journal: Logs all trades in SQLite with entry/exit prices, TP/SL, and status.


🗄️ Database Schema
The trades table in trade_state.db includes:



Column
Description
Type



id
Unique trade ID
INTEGER (PK, auto-increment)


timestamp
When trade was opened
DATETIME


symbol
Trading symbol (e.g., EURUSD)
TEXT


signal
Trade direction (buy/sell)
TEXT


position_size
Trade quantity
REAL


entry_order_id
IBKR order ID for entry
INTEGER


tp_order_id
IBKR order ID for take-profit
INTEGER


entry_price
Filled entry price
REAL


exit_price
Filled exit price (if closed)
REAL


tp_price
Take-profit price
REAL


tp_hit
TP hit status (0 or 1)
BOOLEAN


closed
Trade closed status (0 or 1)
BOOLEAN


sl_price
Stop-loss price
REAL


sl_order_id
IBKR order ID for stop-loss
INTEGER



📝 Notes

Ensure TWS/IB Gateway is running before starting the bot.
The bot uses asynchronous operations for optimal performance but requires a compatible index.html template.
Logs are output to the console with timestamps and context for debugging.
IBKR connections retry up to 3 times with a 5-second delay if they fail.
To add animated GIFs:
Record the dashboard or webhook usage (e.g., using a screen recorder like OBS).
Upload to a service like Giphy or Imgur.
Replace placeholder URLs in this README with the GIF links.




📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

🛠️ Contributing
Contributions are welcome! Please:

Fork the repository.
Create a feature branch (git checkout -b feature/YourFeature).
Commit changes (git commit -m 'Add YourFeature').
Push to the branch (git push origin feature/YourFeature).
Open a pull request.


⭐ Star this repository if you find it useful! For questions or support, open an issue or contact the maintainer.
