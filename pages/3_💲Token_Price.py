import streamlit as st
import requests

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Token Price",
    layout="wide"
)

st.title("💲Token Price")
st.header("🔖 Current Token Price")
# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

/* Main KPI */

[data-testid="metric-container"] {
    background: linear-gradient(
        135deg,
        rgba(220,252,231,0.95),
        rgba(187,247,208,0.85)
    );
    border: 1px solid #86efac;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0px 4px 15px rgba(34,197,94,0.15);
}

/* KPI Label */

div[data-testid="stMetricLabel"] {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #166534 !important;
}

/* KPI Value */

div[data-testid="stMetricValue"] {
    font-size: 42px !important;
    font-weight: 800 !important;
    color: #14532d !important;
}

/* Smaller metrics */

.small-metric [data-testid="metric-container"] {
    background: #111111;
    border: 1px solid rgba(255,255,255,0.08);
}

.small-metric div[data-testid="stMetricLabel"] {
    color: white !important;
    font-size: 14px !important;
}

.small-metric div[data-testid="stMetricValue"] {
    color: white !important;
    font-size: 24px !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# API
# =====================================================

@st.cache_data(ttl=300)
def get_token_price(chain, address):

    coin = f"{chain}:{address}"

    url = f"https://coins.llama.fi/prices/current/{coin}"

    response = requests.get(url, timeout=20)

    response.raise_for_status()

    data = response.json()

    return data["coins"].get(coin)

# =====================================================
# INPUTS
# =====================================================

col1, col2 = st.columns(2)

with col1:
    chain = st.text_input(
        "Blockchain",
        placeholder="ethereum"
    )

with col2:
    address = st.text_input(
        "Token Address",
        placeholder="0x514910771AF9Ca656af840dff83E8264EcF986CA"
    )

# =====================================================
# BUTTON
# =====================================================

if st.button("Get Token Price", use_container_width=True):

    if not chain or not address:
        st.warning("Please enter blockchain and token address.")
        st.stop()

    try:

        token = get_token_price(chain, address)

        if token is None:
            st.error("Token not found.")
            st.stop()

        symbol = token.get("symbol", "Unknown")
        price = float(token.get("price", 0))
        decimals = token.get("decimals", "-")
        confidence = token.get("confidence", 0)

        # =================================================
        # MAIN KPI
        # =================================================

        st.metric(
            label=f"Current Price ({symbol})",
            value=f"${price:,.6f}"
        )

        st.write("")

        # =================================================
        # DETAILS
        # =================================================

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<div class="small-metric">', unsafe_allow_html=True)
            st.metric(
                "Symbol",
                symbol
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="small-metric">', unsafe_allow_html=True)
            st.metric(
                "Decimals",
                decimals
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="small-metric">', unsafe_allow_html=True)

            if confidence:
                conf_text = f"{confidence:.2%}"
            else:
                conf_text = "N/A"

            st.metric(
                "Confidence",
                conf_text
            )

            st.markdown('</div>', unsafe_allow_html=True)

        # =================================================
        # RAW DATA
        # =================================================

#        with st.expander("View Raw API Response"):

#            st.json(token)

    except Exception as e:

        st.error(f"Error: {e}")

# ===================================================================== Part II ================================================================

# =====================================================
# SECTION 2 : HISTORICAL TOKEN PRICE
# =====================================================

from datetime import datetime, timezone

st.divider()
st.header("📅 Historical Token Price")

# -----------------------------------------------------
# API
# -----------------------------------------------------

@st.cache_data(ttl=300)
def get_historical_price(chain, address, timestamp):

    coin = f"{chain}:{address}"

    url = f"https://coins.llama.fi/prices/historical/{timestamp}/{coin}"

    response = requests.get(url, timeout=20)

    response.raise_for_status()

    data = response.json()

    return data["coins"].get(coin)


# -----------------------------------------------------
# INPUTS
# -----------------------------------------------------

h_col1, h_col2 = st.columns(2)

with h_col1:
    historical_chain = st.text_input(
        "Blockchain ",
        placeholder="ethereum",
        key="historical_chain"
    )

with h_col2:
    historical_address = st.text_input(
        "Token Address ",
        placeholder="0x514910771AF9Ca656af840dff83E8264EcF986CA",
        key="historical_address"
    )

selected_date = st.date_input(
    "Select Date",
    value=datetime.utcnow().date(),
    key="historical_date"
)

# -----------------------------------------------------
# BUTTON
# -----------------------------------------------------

if st.button(
    "Get Historical Price",
    use_container_width=True,
    key="historical_button"
):

    try:

        dt = datetime.combine(
            selected_date,
            datetime.min.time()
        ).replace(tzinfo=timezone.utc)

        timestamp = int(dt.timestamp())

        token = get_historical_price(
            historical_chain,
            historical_address,
            timestamp
        )

        if token is None:

            st.error("Historical price not found.")
            st.stop()

        symbol = token.get("symbol", "Unknown")
        price = float(token.get("price", 0))
        confidence = token.get("confidence", 0)
        actual_timestamp = token.get("timestamp")

        actual_date = datetime.utcfromtimestamp(
            actual_timestamp
        ).strftime("%Y-%m-%d %H:%M UTC")

        # -------------------------------------------------
        # MAIN KPI
        # -------------------------------------------------

        st.metric(
            label=f"{symbol} Historical Price",
            value=f"${price:,.6f}"
        )

        # -------------------------------------------------
        # DETAILS
        # -------------------------------------------------

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Symbol",
                symbol
            )

        with c2:
            st.metric(
                "Confidence",
                f"{confidence:.2%}"
            )

        with c3:
            st.metric(
                "Price Timestamp",
                actual_date
            )

    except Exception as e:

        st.error(f"Error: {e}")

# ===================================================== Part III ================================================================================

# =====================================================
# SECTION 3 : TOKEN PRICE CHART
# =====================================================

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone

st.divider()
st.header("📈 Token Price Chart")

# -----------------------------------------------------
# API (Main Chart)
# -----------------------------------------------------

@st.cache_data(ttl=300)
def get_price_chart(
    chain,
    address,
    start_ts,
    span,
    period
):

    coin = f"{chain}:{address}"

    url = f"https://coins.llama.fi/chart/{coin}"

    params = {
        "start": start_ts,
        "period": period,
        "span": span
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    return data["coins"].get(coin)

# -----------------------------------------------------
# API (Independent Candlestick - ALWAYS 4H)
# -----------------------------------------------------

@st.cache_data(ttl=300)
def get_candle_4h(
    chain,
    address,
    start_ts,
    span
):

    coin = f"{chain}:{address}"

    url = f"https://coins.llama.fi/chart/{coin}"

    params = {
        "start": start_ts,
        "period": "4H",
        "span": span
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    return data["coins"].get(coin)

# -----------------------------------------------------
# INPUTS
# -----------------------------------------------------

c1, c2 = st.columns(2)

with c1:
    chart_chain = st.text_input(
        "Blockchain",
        placeholder="ethereum",
        key="chart_chain"
    )

with c2:
    chart_address = st.text_input(
        "Token Address",
        placeholder="0x514910771AF9Ca656af840dff83E8264EcF986CA",
        key="chart_address"
    )

d1, d2, d3 = st.columns(3)

with d1:
    start_date = st.date_input("Start Date", key="chart_start")

with d2:
    end_date = st.date_input("End Date", key="chart_end")

with d3:
    period = st.selectbox(
        "Interval (Main Chart)",
        ["1H", "4H", "12H", "1D", "7D"],
        index=3,
        key="chart_period"
    )

# -----------------------------------------------------
# BUTTON
# -----------------------------------------------------

if st.button("Generate Price Chart", use_container_width=True):

    try:

        # -----------------------------
        # Time conversion
        # -----------------------------

        start_ts = int(
            datetime.combine(start_date, datetime.min.time())
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )

        end_ts = int(
            datetime.combine(end_date, datetime.min.time())
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )

        if end_ts <= start_ts:
            st.error("End Date must be after Start Date")
            st.stop()

        # -----------------------------
        # Span for main chart
        # -----------------------------

        seconds_map = {
            "1H": 3600,
            "4H": 14400,
            "12H": 43200,
            "1D": 86400,
            "7D": 604800
        }

        span = int((end_ts - start_ts) / seconds_map[period])
        if span < 1:
            span = 1

        # -----------------------------
        # MAIN LINE DATA
        # -----------------------------

        token = get_price_chart(
            chart_chain,
            chart_address,
            start_ts,
            span,
            period
        )

        if token is None:
            st.error("No chart data found")
            st.stop()

        symbol = token["symbol"]
        prices = token["prices"]

        df_chart = pd.DataFrame(prices)
        df_chart["datetime"] = pd.to_datetime(df_chart["timestamp"], unit="s")

        # -----------------------------
        # Statistics
        # -----------------------------

        first_price = df_chart["price"].iloc[0]
        last_price = df_chart["price"].iloc[-1]

        change_pct = ((last_price - first_price) / first_price) * 100

        ath_price = df_chart["price"].max()
        atl_price = df_chart["price"].min()
        avg_price = df_chart["price"].mean()

        # -----------------------------
        # LINE CHART (User Interval)
        # -----------------------------

        fig = px.line(
            df_chart,
            x="datetime",
            y="price",
            title=f"{symbol} Price History"
        )

        fig.update_traces(line_width=3)
        fig.update_layout(height=600, hovermode="x unified")

        st.plotly_chart(fig, use_container_width=True)

        # -----------------------------
        # KPI ROW 1
        # -----------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Start Price", f"${first_price:,.6f}")

        with col2:
            st.metric("End Price", f"${last_price:,.6f}")

        with col3:
            st.metric("Change %", f"{change_pct:.2f}%")

        # -----------------------------
        # KPI ROW 2
        # -----------------------------

        col4, col5, col6 = st.columns(3)

        with col4:
            st.metric("ATH Price", f"${ath_price:,.6f}")

        with col5:
            st.metric("ATL Price", f"${atl_price:,.6f}")

        with col6:
            st.metric("Avg Price", f"${avg_price:,.6f}")

        # =================================================
        # CANDLESTICK CHART (INDEPENDENT 4H)
        # =================================================

        st.subheader("🕯️ Candlestick Chart (4H Independent)")

        candle_span = int((end_ts - start_ts) / (4 * 3600))
        if candle_span < 1:
            candle_span = 1

        candle_token = get_candle_4h(
            chart_chain,
            chart_address,
            start_ts,
            candle_span
        )

        if candle_token is not None:

            candle_prices = candle_token["prices"]

            df_candle = pd.DataFrame(candle_prices)
            df_candle["datetime"] = pd.to_datetime(df_candle["timestamp"], unit="s")

            df_candle["date"] = df_candle["datetime"].dt.floor("D")

            ohlc = (
                df_candle
                .groupby("date")["price"]
                .agg(
                    Open="first",
                    High="max",
                    Low="min",
                    Close="last"
                )
                .reset_index()
            )

            fig_candle = go.Figure(
                data=[
                    go.Candlestick(
                        x=ohlc["date"],
                        open=ohlc["Open"],
                        high=ohlc["High"],
                        low=ohlc["Low"],
                        close=ohlc["Close"]
                    )
                ]
            )

            fig_candle.update_layout(
                height=700,
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                xaxis_rangeslider_visible=False
            )

            st.plotly_chart(fig_candle, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

# ================================================================= Deep Analysis ==================================================================
# =====================================================
# INDICATORS PANEL
# =====================================================

st.subheader("📊 Technical Indicators")

indicator_list = [
    "SMA", "EMA", "WMA",
    "RSI", "MACD",
    "Bollinger Bands",
    "ROC",
    "Momentum",
    "Z-Score",
    "Returns",
    "Log Returns",
    "Rolling Mean",
    "Rolling Std",
    "ATR (Approx)",
    "Donchian Channels",
    "Keltner Channels",
    "Pivot Points",
    "Regression Channel",
    "Volatility",
    "Support/Resistance"
]

selected_indicators = st.multiselect(
    "Select Indicators",
    indicator_list,
    default=["SMA", "EMA"]
)

import numpy as np

df_ind = df_chart.copy()

df_ind["returns"] = df_ind["price"].pct_change()
df_ind["log_returns"] = np.log(df_ind["price"]).diff()

window = 14
rolling = 20

# =========================
# Moving Averages
# =========================

df_ind["SMA"] = df_ind["price"].rolling(20).mean()
df_ind["EMA"] = df_ind["price"].ewm(span=20).mean()
df_ind["WMA"] = df_ind["price"].rolling(20).apply(
    lambda x: np.dot(x, np.arange(1, len(x)+1)) / np.sum(np.arange(1, len(x)+1))
)

# =========================
# RSI
# =========================

delta = df_ind["price"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss
df_ind["RSI"] = 100 - (100 / (1 + rs))

# =========================
# MACD
# =========================

ema12 = df_ind["price"].ewm(span=12).mean()
ema26 = df_ind["price"].ewm(span=26).mean()

df_ind["MACD"] = ema12 - ema26
df_ind["MACD_signal"] = df_ind["MACD"].ewm(span=9).mean()

# =========================
# Bollinger Bands
# =========================

df_ind["BB_MID"] = df_ind["price"].rolling(20).mean()
df_ind["BB_STD"] = df_ind["price"].rolling(20).std()

df_ind["BB_UPPER"] = df_ind["BB_MID"] + 2 * df_ind["BB_STD"]
df_ind["BB_LOWER"] = df_ind["BB_MID"] - 2 * df_ind["BB_STD"]

# =========================
# Z-Score
# =========================

df_ind["Z"] = (df_ind["price"] - df_ind["BB_MID"]) / df_ind["BB_STD"]

# =========================
# ROC
# =========================

df_ind["ROC"] = df_ind["price"].pct_change(periods=10) * 100

# =========================
# Momentum
# =========================

df_ind["Momentum"] = df_ind["price"] - df_ind["price"].shift(10)

# =========================
# Rolling Stats
# =========================

df_ind["Rolling_Mean"] = df_ind["price"].rolling(20).mean()
df_ind["Rolling_Std"] = df_ind["price"].rolling(20).std()

# =========================
# Volatility
# =========================

df_ind["Volatility"] = df_ind["returns"].rolling(20).std() * np.sqrt(365)

st.subheader("🕯️ Candlestick + Indicators")

fig = go.Figure()

# Candle
fig.add_trace(go.Candlestick(
    x=ohlc["date"],
    open=ohlc["Open"],
    high=ohlc["High"],
    low=ohlc["Low"],
    close=ohlc["Close"],
    name="Price"
))

# Indicators Overlay
if "SMA" in selected_indicators:
    fig.add_trace(go.Scatter(
        x=df_ind["datetime"],
        y=df_ind["SMA"],
        name="SMA",
        line=dict(width=2)
    ))

if "EMA" in selected_indicators:
    fig.add_trace(go.Scatter(
        x=df_ind["datetime"],
        y=df_ind["EMA"],
        name="EMA",
        line=dict(width=2)
    ))

if "Bollinger Bands" in selected_indicators:
    fig.add_trace(go.Scatter(
        x=df_ind["datetime"],
        y=df_ind["BB_UPPER"],
        name="BB Upper",
        line=dict(dash="dot")
    ))

    fig.add_trace(go.Scatter(
        x=df_ind["datetime"],
        y=df_ind["BB_LOWER"],
        name="BB Lower",
        line=dict(dash="dot")
    ))

fig.update_layout(
    height=750,
    xaxis_rangeslider_visible=False,
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

if "RSI" in selected_indicators:

    st.subheader("📉 RSI")

    fig_rsi = px.line(df_ind, x="datetime", y="RSI")
    fig_rsi.add_hline(y=70, line_dash="dash")
    fig_rsi.add_hline(y=30, line_dash="dash")

    st.plotly_chart(fig_rsi, use_container_width=True)


if "MACD" in selected_indicators:

    st.subheader("📊 MACD")

    fig_macd = go.Figure()

    fig_macd.add_trace(go.Scatter(
        x=df_ind["datetime"],
        y=df_ind["MACD"],
        name="MACD"
    ))

    fig_macd.add_trace(go.Scatter(
        x=df_ind["datetime"],
        y=df_ind["MACD_signal"],
        name="Signal"
    ))

    st.plotly_chart(fig_macd, use_container_width=True)


if "Z-Score" in selected_indicators:

    st.subheader("📐 Z-Score")

    st.plotly_chart(
        px.line(df_ind, x="datetime", y="Z"),
        use_container_width=True
    )
