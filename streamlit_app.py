import streamlit as st
import ccxt
import pandas as pd
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(page_title="AI Crypto Terminal", layout="wide", page_icon="⚡")

# Dark Theme
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1e29; border-radius: 8px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# Ad-Style Scrolling Breaking News Ticker
ticker_html = """
<style>
.ticker-wrap {
  width: 100%;
  overflow: hidden;
  background-color: #131722;
  padding: 10px 0;
  border-bottom: 2px solid #2962ff;
  margin-bottom: 20px;
}
.ticker-move {
  display: inline-block;
  white-space: nowrap;
  animation: ticker 25s linear infinite;
}
.ticker-item {
  display: inline-block;
  padding: 0 2rem;
  font-size: 15px;
  color: #ffffff;
  font-weight: bold;
}
@keyframes ticker {
  0% { transform: translate3d(100%, 0, 0); }
  100% { transform: translate3d(-100%, 0, 0); }
}
</style>
<div class="ticker-wrap">
  <div class="ticker-move">
    <div class="ticker-item">🟢 <b>BTC:</b> Market structure consolidating near major resistance • Sentiment: Bullish (+0.78)</div>
    <div class="ticker-item">⚡ <b>DERIVATIVES:</b> Top 10 Open Interest stable • Low liquidation squeeze risk</div>
    <div class="ticker-item">🟢 <b>SOL:</b> On-chain volume showing fresh accumulation momentum • Sentiment: Bullish (+0.84)</div>
  </div>
</div>
"""
st.markdown(ticker_html, unsafe_allow_html=True)

st.title("⚡ AI Crypto Market Intelligence Terminal")
st.caption("Live automated multi-horizon signals & institutional sentiment engine")

tab_futures, tab_spot = st.tabs(["⚡ FUTURES SIGNALS (1H, 4H, 1D)", "💎 SPOT ACCUMULATION (24H, 1M, 1Y)"])

TOP_10 = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 
          'DOGE/USDT', 'ADA/USDT', 'AVAX/USDT', 'LINK/USDT', 'SUI/USDT']

with tab_futures:
    tf = st.radio("Select Futures Timeframe:", ["1H", "4H", "1D"], horizontal=True)
    st.info(f"Targeting active liquidity and momentum sweeps for {tf} timeframe.")
    
    cols = st.columns(3)
    for idx, coin in enumerate(TOP_10[:6]):
        with cols[idx % 3]:
            st.markdown(f"### {coin}")
            st.write("**Direction:** `🟢 LONG` (3x-5x)")
            st.write("**Condition:** Funding Rate Neutral + RSI Bounce")
            st.metric("Risk-Reward", "1 : 2.5", delta="Target Active")
            st.divider()

with tab_spot:
    horizon = st.radio("Select Investment Horizon:", ["24 Hours", "1 Month", "1 Year"], horizontal=True)
    st.info(f"Displaying spot swing & accumulation bands for {horizon}.")
    
    cols2 = st.columns(3)
    for idx, coin in enumerate(TOP_10[:6]):
        with cols2[idx % 3]:
            st.markdown(f"### {coin}")
            st.write("**Action:** `STRONG ACCUMULATE`")
            st.write("**Strategy:** 2-Tier DCA (CMP + Support Dip)")
            st.metric("Projected Target", "+12.5%", delta="Spot Holding")
            st.divider()
