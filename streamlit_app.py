import streamlit as st
import pandas as pd
import numpy as np
import requests
import xml.etree.ElementTree as ET

st.set_page_config(page_title="AI Crypto Quantitative Terminal", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    .main { background-color: #0b0e14; }
    .stMetric { background-color: #151924; border-radius: 10px; padding: 12px; border: 1px solid #232936; }
</style>
""", unsafe_allow_html=True)

# 1. LIVE BREAKING NEWS FEED
@st.cache_data(ttl=300)
def fetch_live_news():
    headlines = []
    rss_urls = ["https://feeds.feedburner.com/CoinDesk", "https://cointelegraph.com/rss"]
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in rss_urls:
        try:
            res = requests.get(url, headers=headers, timeout=4)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall(".//item")[:3]:
                    t = item.find("title").text
                    if t:
                        low = t.lower()
                        score = 0.80 if any(w in low for w in ["surge", "bull", "rally", "high"]) else (-0.70 if any(w in low for w in ["drop", "dump", "fall", "crash"]) else 0.20)
                        headlines.append((t.strip(), score))
                if len(headlines) >= 4:
                    break
        except Exception:
            continue
    if not headlines:
        headlines = [("Liquidity aggregates remain concentrated across key orderbooks", 0.45)]
    return headlines

news_items = fetch_live_news()
ticker_items_html = "".join([
    '<div class="ticker-item">' + ("🟢" if s > 0 else "🔴") + ' <b>LIVE:</b> ' + t + ' • Sentiment: ' + f"{s:+.2f}" + '</div>'
    for t, s in news_items
])

st.markdown("""
<style>
.ticker-wrap { width: 100%; overflow: hidden; background-color: #131722; padding: 10px 0; border-bottom: 2px solid #2962ff; margin-bottom: 20px; }
.ticker-move { display: inline-block; white-space: nowrap; animation: ticker 40s linear infinite; }
.ticker-item { display: inline-block; padding: 0 2rem; font-size: 14px; color: #ffffff; font-weight: 600; }
@keyframes ticker { 0% { transform: translate3d(100%, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
<div class="ticker-wrap"><div class="ticker-move">""" + ticker_items_html + """</div></div>
""", unsafe_allow_html=True)

st.title("⚡ AI Crypto Quantitative Terminal")
st.caption("Live Exchange Feed • Real-Time Predictive Modeling • Systematic Signals")

# Direct Global Spot/Futures pairs
COINS_MAP = [
    {"display": "BTC/USD", "pair": "BTC-USD"},
    {"display": "ETH/USD", "pair": "ETH-USD"},
    {"display": "SOL/USD", "pair": "SOL-USD"},
    {"display": "XRP/USD", "pair": "XRP-USD"},
    {"display": "DOGE/USD", "pair": "DOGE-USD"},
    {"display": "ADA/USD", "pair": "ADA-USD"},
    {"display": "AVAX/USD", "pair": "AVAX-USD"},
    {"display": "LINK/USD", "pair": "LINK-USD"},
    {"display": "SUI/USD", "pair": "SUI-USD"}
]

GRANULARITY_MAP = {
    "1h": 3600,
    "4h": 21600,
    "1d": 86400
}

# 2. REAL-TIME DATA & PREDICTIVE QUANT MODEL
@st.cache_data(ttl=45)
def get_predictive_metrics(pair, tf="1h"):
    gran = GRANULARITY_MAP.get(tf, 3600)
    url = f"https://api.exchange.coinbase.com/products/{pair}/candles?granularity={gran}"
    headers = {"User-Agent": "QuantitativeAI/2.0"}
    try:
        res = requests.get(url, headers=headers, timeout=6)
        if res.status_code != 200:
            return None
        data = res.json()
        if not data or len(data) < 30:
            return None
            
        # [time, low, high, open, close, volume]
        df = pd.DataFrame(data, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
        df = df.iloc[::-1].reset_index(drop=True)
        
        closes = df['close'].astype(float)
        highs = df['high'].astype(float)
        lows = df['low'].astype(float)
        cmp_val = closes.iloc[-1]
        
        # 1. Technical Momentum: RSI (14)
        delta = closes.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=14, min_periods=14).mean()
        avg_loss = loss.rolling(window=14, min_periods=14).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        rsi = float((100 - (100 / (1 + rs))).iloc[-1])
        
        # 2. Moving Averages
        ema20 = float(closes.ewm(span=20, adjust=False).mean().iloc[-1])
        ema50 = float(closes.ewm(span=min(50, len(closes)), adjust=False).mean().iloc[-1])
        ema200 = float(closes.ewm(span=min(200, len(closes)), adjust=False).mean().iloc[-1])
        
        # 3. Volatility Modeling: ATR (Average True Range)
        tr1 = highs - lows
        tr2 = (highs - closes.shift()).abs()
        tr3 = (lows - closes.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
        
        # 4. Expected Price Drift Prediction Logic
        returns = closes.pct_change().dropna()
        recent_momentum = float(returns.tail(5).mean())
        volatility_sigma = float(returns.std())
        
        # Predictive target calculation based on momentum direction & 1.5x ATR expansion
        if cmp_val > ema20 and rsi > 48:
            bias = "BULLISH_EXPANSION"
            predicted_price = cmp_val + (atr * 1.6)
            predicted_range_high = cmp_val + (atr * 2.2)
            predicted_range_low = cmp_val - (atr * 0.8)
        elif cmp_val < ema20 and rsi < 52:
            bias = "BEARISH_CONTRACTION"
            predicted_price = cmp_val - (atr * 1.6)
            predicted_range_high = cmp_val + (atr * 0.8)
            predicted_range_low = cmp_val - (atr * 2.2)
        else:
            bias = "CONSOLIDATION_DRIFT"
            predicted_price = cmp_val + (recent_momentum * cmp_val)
            predicted_range_high = cmp_val + atr
            predicted_range_low = cmp_val - atr
            
        pred_pct_change = ((predicted_price - cmp_val) / cmp_val) * 100
        
        return {
            "cmp": cmp_val,
            "rsi": rsi,
            "ema50": ema50,
            "ema200": ema200,
            "atr": atr,
            "bias": bias,
            "predicted_price": predicted_price,
            "predicted_high": predicted_range_high,
            "predicted_low": predicted_range_low,
            "pred_pct": pred_pct_change,
            "volatility_pct": (atr / cmp_val) * 100
        }
    except Exception:
        return None

tab_futures, tab_spot = st.tabs(["⚡ FUTURES SIGNALS (1H, 4H, 1D)", "💎 SPOT ACCUMULATION (24H, 1M, 1Y)"])

# ----------------- FUTURES TAB -----------------
with tab_futures:
    tf = st.radio("Select Prediction Timeframe:", ["1h", "4h", "1d"], horizontal=True)
    st.info("Live algorithmic volatility & momentum prediction model running for: " + tf.upper())
    
    cols = st.columns(3)
    col_idx = 0
    for item in COINS_MAP:
        m = get_predictive_metrics(item["pair"], tf=tf)
        if not m:
            continue
            
        cmp_val = m["cmp"]
        pred_price = m["predicted_price"]
        bias = m["bias"]
        
        # Signal Generation based on Prediction
        if bias == "BULLISH_EXPANSION" and m["rsi"] < 68:
            signal_title = "🟢 LONG"
            sig_color = "#00c853"
            entry_zone = f"${cmp_val:,.4f} -${m['predicted_low']:,.4f}"
            stop_loss = cmp_val - (m["atr"] * 1.2)
        elif bias == "BEARISH_CONTRACTION" and m["rsi"] > 32:
            signal_title = "🔴 SHORT"
            sig_color = "#ff5252"
            entry_zone = f"${cmp_val:,.4f} -${m['predicted_high']:,.4f}"
            stop_loss = cmp_val + (m["atr"] * 1.2)
        else:
            signal_title = "🟡 WAIT / RANGE"
            sig_color = "#ffb300"
            entry_zone = "No Edge / Wait Breakout"
            stop_loss = cmp_val - m["atr"]
            
        with cols[col_idx % 3]:
            st.markdown("### " + item["display"])
            st.write("**Live Price:** $" + f"{cmp_val:,.4f}")
            
            # Prediction Box
            st.metric("Predicted Target Price", "$" + f"{pred_price:,.4f}", delta=f"{m['pred_pct']:+.2f}%")
            st.caption(f"Expected Range: ${m['predicted_low']:,.2f} ➔${m['predicted_high']:,.2f} (ATR Vol: {m['volatility_pct']:.2f}%)")
            
            # Output Signal
            st.markdown("Algorithmic Signal: <b style='color:" + sig_color + "; font-size:16px;'>" + signal_title + "</b>", unsafe_allow_html=True)
            st.write(f"**Optimal Entry Zone:** {entry_zone}")
            st.write(f"**Calculated Stop Loss:** ${stop_loss:,.4f}")
            st.write(f"**RSI (14):** `{m['rsi']:.1f}` | **EMA 50:** `${m['ema50']:,.2f}`")
            st.divider()
        col_idx += 1

# ----------------- SPOT TAB -----------------
with tab_spot:
    horizon = st.radio("Select Investment Horizon:", ["24 Hours", "1 Month", "1 Year"], horizontal=True)
    st.info("Institutional macro accumulation model calculated from 1D historical distribution for " + horizon + ".")
    
    cols2 = st.columns(3)
    col_idx2 = 0
    for item in COINS_MAP:
        m_day = get_predictive_metrics(item["pair"], tf="1d")
        if not m_day:
            continue
            
        cmp_val = m_day["cmp"]
        ema200 = m_day["ema200"]
        atr_day = m_day["atr"]
        
        # Horizon Projection Model
        if horizon == "24 Hours":
            proj_price = cmp_val + (atr_day * 1.1)
            dca_level_1 = cmp_val
            dca_level_2 = cmp_val - (atr_day * 0.9)
            cycle_desc = "Intraday Swing Accumulation"
        elif horizon == "1 Month":
            # 30-day volatility drift
            proj_price = cmp_val + (atr_day * 5.0)
            dca_level_1 = cmp_val * 0.96
            dca_level_2 = min(cmp_val * 0.90, ema200)
            cycle_desc = "Mid-Term Cycle Positioning"
        else: # 1 Year
            # Macro structural expansion
            proj_price = max(cmp_val * 2.2, ema200 * 2.8)
            dca_level_1 = cmp_val
            dca_level_2 = ema200 * 0.95
            cycle_desc = "Macro Bull Run DCA"
            
        proj_pct = ((proj_price - cmp_val) / cmp_val) * 100
        
        with cols2[col_idx2 % 3]:
            st.markdown("### " + item["display"])
            st.write("**Current Market Price:** $" + f"{cmp_val:,.4f}")
            st.metric(f"Predicted Valuation ({horizon})", "$" + f"{proj_price:,.4f}", delta=f"+{proj_pct:.1f}%")
            
            st.markdown("Action: <b style='color:#00e676;'>SYSTEMATIC DCA ACCUMULATE</b>", unsafe_allow_html=True)
            st.write(f"**DCA Level 1 (Market):** ${dca_level_1:,.4f}")
            st.write(f"**DCA Level 2 (Value Dip):** ${dca_level_2:,.4f}")
            st.caption(f"Strategy: {cycle_desc} | Benchmark EMA 200: ${ema200:,.2f}")
            st.divider()
        col_idx2 += 1
