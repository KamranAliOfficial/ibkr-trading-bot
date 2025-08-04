🚀 IBKR Trading Bot: Your Trading Sidekick!
   
Welcome to the IBKR Trading Bot—a fun, powerful tool that trades automatically with Interactive Brokers (IBKR)! 🤑 Built with Python, it’s super fast, saves your trades in a database, and comes with a gorgeous web dashboard to watch your account and trades live. 📈 Whether you’re a trading newbie or a pro, this bot makes trading a breeze!
Show it off! Replace with a GIF of the dashboard showing account stats and trades (upload to Giphy or Imgur).
🌟 Why You’ll Love This Bot

⚡ Super Speedy: Uses cool tech (Quart & aiosqlite) to run without hiccups.
📝 Trade Diary: Keeps a record of every trade (like EURUSD or AAPL) in a database.
🌐 Easy Commands: Send simple messages to buy or sell from anywhere.
🤝 Works with IBKR: Places buy, sell, take-profit, and stop-loss orders for you.
📊 Awesome Dashboard: See your money, trades, and history live in a slick interface.
🧠 Smart Moves: Avoids duplicate trades, flips positions, and stays safe.
🛡️ Worry-Free: Fixes connection issues and logs errors clearly.

📋 What You Need

🐍 Python 3.8+: The magic behind the bot.
💻 Interactive Brokers TWS or Gateway: A free app to connect your IBKR account.
📦 A Few Tools:pip install quart aiosqlite ib_insync



🛠️ Setup in 5 Easy Steps
Get your bot up and running with these simple steps! 🎉
1. 📥 Grab the Code
Download the bot to your computer:
git clone https://github.com/<your-username>/ibkr-trading-bot.git
cd ibkr-trading-bot

Make it fun! Add a GIF of cloning the repo in your terminal.
2. 📦 Install the Tools
Create a file called requirements.txt:
quart==0.19.4
aiosqlite==0.20.0
ib_insync==0.9.70

Then install them:
pip install -r requirements.txt

3. 🔧 Set Up Interactive Brokers

Download TWS or IB Gateway from Interactive Brokers.
Open the app and enable API access:
Go to Settings > API Settings.
Check Enable ActiveX and Socket Clients.
Set the port to 7497 (paper trading) or 7496 (live trading).
Allow connections from 127.0.0.1 (your computer).



Show the steps! Add a GIF of enabling API access in TWS/Gateway.
4. 🎨 Build the Dashboard
Create a folder called templates and add a file named index.html:
<!DOCTYPE html>
<html>
<head>
  <title>IBKR Trading Bot Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: linear-gradient(to bottom, #f0f4f8, #d9e2ec); }
    h1 { color: #1a73e8; text-align: center; }
    h2, h3 { color: #333; font-weight: 500; }
    ul { list-style: none; padding: 0; }
    li { margin: 10px 0; padding: 12px; background: white; border-radius: 10px; box-shadow: 0 3px 6px rgba(0,0,0,0.1); }
    .section { margin-bottom: 20px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 3px 6px rgba(0,0,0,0.1); }
    .section h3 { margin-top: 0; }
  </style>
</head>
<body>
  <h1>IBKR Trading Bot Dashboard</h1>
  <div class="section">
    <h2>Status: {{ dashboard_data.status }}</h2>
  </div>
  <div class="section">
    <h3>💰 Account Summary</h3>
    <ul>
      {% for key, value in dashboard_data.account.items() %}
      <li>{{ key }}: {{ value }}</li>
      {% endfor %}
    </ul>
  </div>
  <div class="section">
    <h3>📈 Open Trades</h3>
    <ul>
      {% for pos in dashboard_data.positions %}
      <li>{{ pos.symbol }}: {{ pos.position }} @ {{ pos.avgCost }}</li>
      {% endfor %}
    </ul>
  </div>
  <div class="section">
    <h3>📜 Trade History</h3>
    <ul>
      {% for log in trade_log %}
      <li>{{ log.timestamp }} - {{ log.symbol }} - {{ log.action }}: {{ log.details }}</li>
      {% endfor %}
    </ul>
  </div>
</body>
</html>

Bring it to life! Add a GIF of the dashboard rendering in a browser.
5. 🗄️ Database Magic
No setup needed! The bot creates a trade_state.db file when you run it. 🪄
🚀 How to Use Your Bot
1. ▶️ Start Trading
Run this command in your terminal:
python trading_bot.py

Want to tweak it? Use these options:



Option
What It Does
Default



--flask-host
Web server address
0.0.0.0


--flask-port
Web server port
5001


--ib-host
IBKR app address
127.0.0.1


--ib-port
IBKR API port (paper: 7497)
7497


--ib-client-id
Unique ID for the bot
1


2. 🌐 Explore the Dashboard
Open your browser and visit:
http://localhost:5001

Check out:

💰 Account Summary: Your balance, buying power, and profits.
📈 Open Trades: What you’re trading and at what price.
📜 Trade History: Every trade logged with details.

Make it shine! Add a GIF of the dashboard updating with trades.
3. 📡 Send Trade Commands
Tell the bot to trade by sending messages to:
http://localhost:5001/webhook

🟢 Start a Trade
{
  "action": "open",
  "symbol": "EURUSD",
  "side": "buy",
  "quantity": 10000,
  "tp": 1.20,
  "sl": 1.18
}

🔴 Close a Trade
{
  "action": "close",
  "symbol": "EURUSD"
}

Try it with curl:
curl -X POST -H "Content-Type: application/json" \
-d '{"action":"open","symbol":"EURUSD","side":"buy","quantity":10000,"tp":1.20,"sl":1.18}' \
http://localhost:5001/webhook

Show the action! Add a GIF of sending a trade command and the dashboard updating.
🤖 How the Bot Trades

🔒 One Trade Only: One trade per symbol (e.g., EURUSD or AAPL) at a time.
🚫 No Repeats: Won’t let you trade the same side after a take-profit.
🔄 Flip It: A “sell” closes a “buy” (or vice versa) and starts a new trade.
🎯 Safety Net: Adds take-profit and stop-loss orders if you want.
📝 Keeps Records: Saves every trade in the database for you to check later.

🗄️ Inside the Database
The bot saves trades in trade_state.db. Here’s what it stores:



Column
What It Means
Type



id
Unique trade number
Number


timestamp
When the trade started
Date/Time


symbol
Trading pair (e.g., EURUSD)
Text


signal
Buy or sell
Text


position_size
How much you traded
Number


entry_order_id
IBKR’s ID for the trade
Number


tp_order_id
ID for take-profit order
Number


entry_price
Price you bought/sold at
Number


exit_price
Price when trade closed
Number


tp_price
Take-profit price
Number


tp_hit
Did TP happen? (0=no, 1=yes)
True/False


closed
Is trade done? (0=no, 1=yes)
True/False


sl_price
Stop-loss price
Number


sl_order_id
ID for stop-loss order
Number


🎥 Add Awesome Animations!
Make your README sparkle with animated GIFs! 🌟 Here’s how:

Record the Fun:
Use OBS Studio or ScreenRec to record:
Cloning the Repo: Show the git clone command in a terminal.
IBKR Setup: Show enabling API access in TWS/Gateway.
Dashboard Template: Show the dashboard rendering in a browser.
Live Dashboard: Show the dashboard updating with trades.
Webhook Action: Show sending a trade command (via Postman or curl) and the dashboard updating.


Convert to GIFs at ezgif.com (keep under 2MB for fast loading).


Share the GIFs:
Upload to Giphy or Imgur.
Or add to your GitHub repo:git add clone.gif ibkr_setup.gif dashboard_template.gif live_dashboard.gif webhook.gif
git commit -m "Add awesome demo GIFs"
git push origin main


Replace placeholder URLs (e.g., https://via.placeholder.com/...) with your GIF URLs.


Update the README:git add README.md
git commit -m "Add animated GIFs to README"
git push origin main



📝 Handy Tips

Start IBKR First: Run TWS or IB Gateway before the bot.
Dashboard Needs index.html: Keep it in the templates/ folder.
Check the Logs: Look in your terminal for messages if something goes wrong.
Connection Issues?: The bot tries 3 times to connect, waiting 5 seconds each try.
Stay Safe: Don’t share your IBKR account details in the code.


🙈 Keep Your Repo Clean (`.gitignore`)

# Python stuff
__pycache__/
*.py[cod]
*.pyc
env/
venv/
*.egg-info/
.pytest_cache/

# Database
trade_state.db

# Logs
*.log

# Editor files
.idea/
*.sublime-project
*.sublime-workspace

# Mac/Windows junk
.DS_Store
Thumbs.db



📜 Free to Use
This bot is shared under the MIT License. Check the LICENSE file for details.
🤝 Want to Make It Better?
Love the bot? Add your own ideas! Here’s how:

Fork the repo on GitHub.
Create a new branch:git checkout -b my-awesome-feature


Save your changes:git commit -m "Added my awesome feature"


Push to GitHub:git push origin my-awesome-feature


Open a pull request! 🚀

❓ Got Questions?

Ask Away: Open an issue on GitHub.
Chat with Us: Join GitHub Discussions or message the project owner.

🌟 Love this bot? Give it a star on GitHub! Share it with your trading pals or coder buddies! 😄
