import logging
import argparse
import sqlite3
from contextlib import contextmanager
from quart import Quart, request, jsonify, render_template
from ib_insync import IB, Forex, Stock, MarketOrder, LimitOrder, util
from datetime import datetime
import asyncio
import aiosqlite
import uuid

# --- 1. Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- 2. Configuration ---
DB_FILE = 'trade_state.db'
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds

# --- 3. Database Setup with Connection Pooling ---
async def init_db():
    """Initializes the trade journal database."""
    async with aiosqlite.connect(DB_FILE) as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                signal TEXT NOT NULL,
                position_size REAL NOT NULL,
                entry_order_id INTEGER,
                tp_order_id INTEGER,
                entry_price REAL,
                exit_price REAL,
                tp_price REAL,
                tp_hit BOOLEAN DEFAULT 0,
                closed BOOLEAN DEFAULT 0,
                sl_price REAL,
                sl_order_id INTEGER
            )
        ''')
        await conn.commit()
    logger.info("Trade Journal Database initialized.")

# Database helper functions
async def log_new_trade(symbol, signal, size, entry_order_id, tp_price=None, tp_order_id=None, sl_price=None, sl_order_id=None):
    async with aiosqlite.connect(DB_FILE) as conn:
        await conn.execute('''
            INSERT INTO trades (symbol, signal, position_size, entry_order_id, tp_price, tp_order_id, sl_price, sl_order_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, signal, size, entry_order_id, tp_price, tp_order_id, sl_price, sl_order_id))
        await conn.commit()

async def update_trade_on_fill(order_id, fill_price):
    async with aiosqlite.connect(DB_FILE) as conn:
        await conn.execute("UPDATE trades SET entry_price = ? WHERE entry_order_id = ? AND closed = 0", (fill_price, order_id))
        await conn.execute("UPDATE trades SET exit_price = ?, closed = 1, tp_hit = 1 WHERE tp_order_id = ? AND closed = 0", (fill_price, order_id))
        await conn.commit()

async def close_trade_in_db(trade_id):
    async with aiosqlite.connect(DB_FILE) as conn:
        await conn.execute("UPDATE trades SET closed = 1 WHERE id = ?", (trade_id,))
        await conn.commit()

async def get_active_trade(symbol):
    async with aiosqlite.connect(DB_FILE) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT * FROM trades WHERE symbol = ? AND closed = 0 ORDER BY id DESC LIMIT 1", (symbol,))
        trade = await cursor.fetchone()
        return dict(trade) if trade else None

async def get_last_closed_trade(symbol):
    async with aiosqlite.connect(DB_FILE) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute("SELECT * FROM trades WHERE symbol = ? AND closed = 1 ORDER BY id DESC LIMIT 1", (symbol,))
        trade = await cursor.fetchone()
        return dict(trade) if trade else None

# --- 4. Trading Bot Class ---
class TradingBot:
    def __init__(self, args):
        self.args = args
        self.app = Quart(__name__)
        self.ib = IB()
        self.dashboard_data = {
            'status': 'Initializing...',
            'account': {},
            'positions': []
        }
        self.trade_log_ui = []
        self._setup_routes()

    async def connect_ibkr(self):
        for attempt in range(RETRY_ATTEMPTS):
            try:
                if not self.ib.isConnected():
                    await self.ib.connectAsync(self.args.ib_host, self.args.ib_port, clientId=self.args.ib_client_id)
                    logger.info("IBKR connection successful.")
                return
            except Exception as e:
                logger.error(f"IBKR connection attempt {attempt + 1} failed: {e}")
                if attempt < RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    raise Exception("Failed to connect to IBKR after retries")

    async def update_dashboard_data(self):
        while self.ib.isConnected():
            try:
                account_values = await self.ib.accountValuesAsync()
                self.dashboard_data['account'] = {
                    item.tag: item.value for item in account_values
                    if item.tag in ['NetLiquidation', 'TotalCashValue', 'BuyingPower', 'UnrealizedPnL', 'RealizedPnL']
                }
                positions = await self.ib.positionsAsync()
                self.dashboard_data['positions'] = [
                    {'symbol': p.contract.localSymbol, 'position': p.position, 'avgCost': round(p.avgCost, 2)}
                    for p in positions
                ]
                server_time = await self.ib.reqCurrentTimeAsync()
                self.dashboard_data['status'] = f"Data updated at {server_time.strftime('%Y-%m-%d %H:%M:%S')}"
                logger.info("Dashboard data refreshed.")
            except Exception as e:
                logger.error(f"Error refreshing dashboard data: {e}")
                self.dashboard_data['status'] = f"Error refreshing data: {e}"
            await asyncio.sleep(60)

    async def open_position(self, symbol: str, side: str, quantity: float, tp=None, sl=None):
        sym = symbol.replace('/', '').upper()
        await self.connect_ibkr()

        # Check for recent TP to prevent re-entry
        last_closed = await get_last_closed_trade(sym)
        if last_closed and last_closed.get('tp_hit') and last_closed.get('signal') == side:
            message = f"Re-entry for '{side}' on {sym} blocked due to recent TP."
            logger.warning(message)
            self.trade_log_ui.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': sym,
                'action': "RE-ENTRY BLOCKED",
                'details': message
            })
            return

        # Handle active trades and reversals
        active_trade = await get_active_trade(sym)
        if active_trade:
            if active_trade.get('signal') == side:
                logger.info(f"Signal '{side}' matches active trade for {sym}. No action taken.")
                return
            else:
                logger.info(f"Signal '{side}' is opposite of active trade for {sym}. Reversing.")
                await self.close_position(symbol)

        # Place market order
        contract = Forex(sym) if '/' in symbol else Stock(sym, 'SMART', 'USD')
        action = 'BUY' if side == 'buy' else 'SELL'
        market_order_trade = await self.ib.placeOrderAsync(contract, MarketOrder(action, quantity))
        entry_order_id = market_order_trade.order.orderId
        self.trade_log_ui.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': sym,
            'action': f"Market Order ({action})",
            'details': repr(market_order_trade)
        })

        # Place TP order
        tp_id = None
        if tp:
            tp_price = float(tp)
            exit_act = 'SELL' if side == 'buy' else 'BUY'
            tp_order_trade = await self.ib.placeOrderAsync(contract, LimitOrder(exit_act, quantity, tp_price))
            tp_id = tp_order_trade.order.orderId
            self.trade_log_ui.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': sym,
                'action': f"Take Profit ({exit_act})",
                'details': repr(tp_order_trade)
            })

        # Place SL order
        sl_id = None
        if sl:
            sl_price = float(sl)
            sl_act = 'SELL' if side == 'buy' else 'BUY'
            sl_order_trade = await self.ib.placeOrderAsync(contract, LimitOrder(sl_act, quantity, sl_price))
            sl_id = sl_order_trade.order.orderId
            self.trade_log_ui.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': sym,
                'action': f"Stop Loss ({sl_act})",
                'details': repr(sl_order_trade)
            })

        await log_new_trade(sym, side, quantity, entry_order_id, tp, tp_id, sl, sl_id)

    async def close_position(self, symbol: str):
        sym = symbol.replace('/', '').upper()
        await self.connect_ibkr()
        active_trade = await get_active_trade(sym)
        if not active_trade:
            logger.info(f"No active trade found for {sym} to close.")
            return

        # Cancel TP order
        tp_order_id = active_trade.get('tp_order_id')
        if tp_order_id:
            try:
                await self.ib.cancelOrderAsync(self.ib.orders()[tp_order_id])
                logger.info(f"Cancelled TP order {tp_order_id}")
            except Exception as e:
                logger.warning(f"Failed to cancel TP order {tp_order_id}: {e}")

        # Place closing market order
        side = active_trade.get('signal')
        quantity = active_trade.get('position_size')
        action_to_close = 'SELL' if side == 'buy' else 'BUY'
        contract = Forex(sym) if '/' in symbol else Stock(sym, 'SMART', 'USD')
        close_order_trade = await self.ib.placeOrderAsync(contract, MarketOrder(action_to_close, quantity))
        await close_trade_in_db(active_trade.get('id'))
        self.trade_log_ui.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': sym,
            'action': f"Close by Signal ({action_to_close})",
            'details': repr(close_order_trade)
        })

    def _setup_routes(self):
        @self.app.route('/')
        async def index():
            return await render_template('index.html', dashboard_data=self.dashboard_data, trade_log=self.trade_log_ui)

        @self.app.route('/webhook', methods=['POST'])
        async def webhook():
            try:
                data = await request.get_json()
                action = data.get('action')
                if action == 'open':
                    await self.open_position(
                        data.get('symbol'),
                        data.get('side'),
                        data.get('quantity'),
                        data.get('tp'),
                        data.get('sl')
                    )
                elif action == 'close':
                    await self.close_position(data.get('symbol'))
                return jsonify({'status': 'success'}), 200
            except Exception as e:
                logger.error(f"Webhook error: {e}", exc_info=True)
                return jsonify({'status': 'error', 'msg': str(e)}), 500

    def on_exec_details(self, trade, fill):
        order_id = fill.execution.orderId
        fill_price = fill.execution.price
        logger.info(f"Fill detected for orderId {order_id} at price {fill_price}")
        asyncio.create_task(update_trade_on_fill(order_id, fill_price))

    def on_connected(self, *args):
        logger.info("IBKR connected.")
        asyncio.create_task(self.update_dashboard_data())

    async def run(self):
        await init_db()
        self.ib.execDetailsEvent += self.on_exec_details
        self.ib.connectedEvent += self.on_connected
        util.startLoop()
        await self.connect_ibkr()
        await self.app.run_task(host=self.args.flask_host, port=self.args.flask_port, debug=False)

# --- 5. Main Entry Point ---
async def main():
    parser = argparse.ArgumentParser(description='IBKR Stateful Trading Bot')
    parser.add_argument('--flask-host', default='0.0.0.0', help='Flask host')
    parser.add_argument('--flask-port', type=int, default=5001, help='Flask port')
    parser.add_argument('--ib-host', default='127.0.0.1', help='IB host')
    parser.add_argument('--ib-port', type=int, default=7497, help='IB port for TWS')
    parser.add_argument('--ib-client-id', type=int, default=1, help='IB client ID')
    args = parser.parse_args()

    bot = TradingBot(args)
    await bot.run()

if __name__ == '__main__':
    asyncio.run(main())