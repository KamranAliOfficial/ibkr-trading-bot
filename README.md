🚀 IBKR Stateful Trading Bot
A high-speed Python bot for automated trading with Interactive Brokers (IBKR) using Quart and ib_insync. It supports webhooks, stores trade history in SQLite, and shows a real-time dashboard.

✨ Features
🔄 Async trading engine (Quart + aiosqlite)

📡 Webhook-based trade execution (JSON)

📊 Real-time dashboard (account + trades)

📚 Trade journal with TP/SL tracking

🧠 Smart logic: one trade/symbol, reversal support

🛠️ Auto retry + error handling

🚀 Quick Start
bash
Copy
Edit
# 1. Install dependencies
pip install quart aiosqlite ib_insync

# 2. Start TWS/IB Gateway (API port 7497)

# 3. Run the bot
python trading_bot.py --flask-port 5001
Visit: http://localhost:5001

📡 Webhook Example
Open Position

json
Copy
Edit
{
  "action": "open",
  "symbol": "EURUSD",
  "side": "buy",
  "quantity": 10000,
  "tp": 1.20,
  "sl": 1.18
}
Close Position

json
Copy
Edit
{
  "action": "close",
  "symbol": "EURUSD"
}
Send to: POST http://localhost:5001/webhook

📄 License
MIT — free to use and modify.
