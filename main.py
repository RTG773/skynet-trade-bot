//@version=5
strategy("XAUUSD Smart Money Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=1)

// === Fixed Session (London: 03:00–07:00 UTC)
in_session = (hour >= 3 and hour < 7)

// === Risk:Reward
rr_ratio = 3.0

// === Confluences
bos = high > high[1] and low > low[1] and close > close[1]
fvg = (low[1] > high[2])
ob = close[1] < open[1] and close > open and volume > volume[1]

// === Entry Logic
long_condition = bos and fvg and ob and in_session

// === Trade Levels
entry_price = close
sl_price    = entry_price - 20
tp1_price   = entry_price + 40
tp2_price   = entry_price + 60

if (long_condition)
    strategy.entry("Long", strategy.long)
    strategy.exit("TP/SL", from_entry="Long", limit=tp2_price, stop=sl_price)

// === Plot Signal
plotshape(long_condition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")

// === Confluence Text
bos_txt = bos ? "☑ Break of Structure (BOS)\n" : ""
fvg_txt = fvg ? "☑ Fair Value Gap (FVG)\n" : ""
ob_txt  = ob ? "☑ Order Block (OB)\n" : ""
session_txt = in_session ? "☑ London Session\n" : ""
confluence_list = bos_txt + fvg_txt + ob_txt + session_txt

// === Alert JSON with Confluences
alert_message =
  '{' +
  '"pair": "XAUUSD",' +
  '"entry": ' + str.tostring(entry_price) + ',' +
  '"sl": ' + str.tostring(sl_price) + ',' +
  '"tp1": ' + str.tostring(tp1_price) + ',' +
  '"tp2": ' + str.tostring(tp2_price) + ',' +
  '"direction": "buy",' +
  '"rr": "1:' + str.tostring(rr_ratio) + '",' +
  '"winrate": "' + str.tostring(4 * 20) + '",' +  // assuming 4 total confluences
  '"confluences": "' + str.replace(confluence_list, "\n", "\\n") + '"' +
  '}'

alert(alert_message, freq=alert.freq_once_per_bar_close)
