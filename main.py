from flask import Flask, request
import threading
import requests
import time

app = Flask(__name__)

# === CONFIGURATION ===
BOT_TOKEN = "8131820675:AAHX6-lsME5ccr1lL0bsTRlpE3aefpy02XM"
CHAT_ID = "-1002552746807"
TWELVE_DATA_API_KEY = "30dd7bca99ca43c09aaf1a95d188de0b"
PRICE_POLL_INTERVAL = 10  # seconds

open_trades = []

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def monitor_prices():
    while True:
        time.sleep(PRICE_POLL_INTERVAL)
        for trade in open_trades[:]:
            symbol = trade["pair"]
            if symbol == "US30":
                tw_symbol = "DJI"
            elif symbol == "NASDAQ":
                tw_symbol = "NDX"
            elif symbol == "XAUUSD":
                tw_symbol = "XAU/USD"
            else:
                tw_symbol = symbol

            url = f"https://api.twelvedata.com/price?symbol={tw_symbol}&apikey={TWELVE_DATA_API_KEY}"
            r = requests.get(url).json()
            try:
                current_price = float(r['price'])
            except:
                continue

            if trade["direction"].lower() == "buy":
                if current_price >= trade["tp2"]:
                    send_telegram(f"✅ *{symbol} TP2 Hit!* | Final RR: {trade['rr']} | +{trade['tp2'] - trade['entry']:.1f} pips")
                    open_trades.remove(trade)
                elif current_price >= trade["tp1"] and not trade["tp1_hit"]:
                    send_telegram(f"✅ *{symbol} TP1 Hit!* | +{trade['tp1'] - trade['entry']:.1f} pips")
                    trade["tp1_hit"] = True
                elif current_price <= trade["sl"]:
                    send_telegram(f"❌ *{symbol} SL Hit!* | -{trade['entry'] - trade['sl']:.1f} pips | Final RR: -1")
                    open_trades.remove(trade)
            elif trade["direction"].lower() == "sell":
                if current_price <= trade["tp2"]:
                    send_telegram(f"✅ *{symbol} TP2 Hit!* | Final RR: {trade['rr']} | +{trade['entry'] - trade['tp2']:.1f} pips")
                    open_trades.remove(trade)
                elif current_price <= trade["tp1"] and not trade["tp1_hit"]:
                    send_telegram(f"✅ *{symbol} TP1 Hit!* | +{trade['entry'] - trade['tp1']:.1f} pips")
                    trade["tp1_hit"] = True
                elif current_price >= trade["sl"]:
                    send_telegram(f"❌ *{symbol} SL Hit!* | -{trade['sl'] - trade['entry']:.1f} pips | Final RR: -1")
                    open_trades.remove(trade)

@app.route("/", methods=["POST"])
def receive_trade():
    data = request.get_json()
    trade = {
        "pair": data.get("pair", "Unknown"),
        "entry": float(data.get("entry", 0)),
        "sl": float(data.get("sl", 0)),
        "tp1": float(data.get("tp1", 0)),
        "tp2": float(data.get("tp2", 0)),
        "direction": data.get("direction", "buy"),
        "rr": data.get("rr", "1:2"),
        "winrate": data.get("winrate", "N/A"),
        "tp1_hit": False
    }

    open_trades.append(trade)

    msg = f"""
*[{trade['pair']} {trade['direction'].capitalize()} Signal]*

Entry: {trade['entry']}
SL: {trade['sl']}
TP1: {trade['tp1']}
TP2: {trade['tp2']}
RR: {trade['rr']}
Win Rate Estimate: {trade['winrate']}%
"""
    send_telegram(msg.strip())
    return {"status": "Trade Received"}

if __name__ == "__main__":
    threading.Thread(target=monitor_prices, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
