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
# API
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

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

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
    start_date = st.date_input(
        "Start Date",
        key="chart_start"
    )

with d2:
    end_date = st.date_input(
        "End Date",
        key="chart_end"
    )

with d3:
    period = st.selectbox(
        "Interval",
        [
            "1H",
            "4H",
            "12H",
            "1D",
            "7D"
        ],
        index=3,
        key="chart_period"
    )

# -----------------------------------------------------
# BUTTON
# -----------------------------------------------------

if st.button(
    "Generate Price Chart",
    use_container_width=True,
    key="chart_button"
):

    try:

        # ---------------------------------------------
        # Convert Dates To Unix Timestamp
        # ---------------------------------------------

        start_ts = int(
            datetime.combine(
                start_date,
                datetime.min.time()
            ).replace(
                tzinfo=timezone.utc
            ).timestamp()
        )

        end_ts = int(
            datetime.combine(
                end_date,
                datetime.min.time()
            ).replace(
                tzinfo=timezone.utc
            ).timestamp()
        )

        if end_ts <= start_ts:

            st.error(
                "End Date must be after Start Date."
            )

            st.stop()

        # ---------------------------------------------
        # Calculate Span
        # ---------------------------------------------

        seconds_per_period = {
            "1H": 3600,
            "4H": 14400,
            "12H": 43200,
            "1D": 86400,
            "7D": 604800
        }

        period_seconds = seconds_per_period[period]

        span = int(
            (end_ts - start_ts)
            / period_seconds
        )

        if span < 1:
            span = 1

        # ---------------------------------------------
        # Fetch Data
        # ---------------------------------------------

        token = get_price_chart(
            chart_chain,
            chart_address,
            start_ts,
            span,
            period
        )

        if token is None:

            st.error(
                "No chart data found."
            )

            st.stop()

        symbol = token["symbol"]

        prices = token["prices"]

        if len(prices) == 0:

            st.warning(
                "No price data available."
            )

            st.stop()

        # ---------------------------------------------
        # Create DataFrame
        # ---------------------------------------------

        df_chart = pd.DataFrame(prices)

        df_chart["datetime"] = pd.to_datetime(
            df_chart["timestamp"],
            unit="s"
        )

        # ---------------------------------------------
        # Statistics
        # ---------------------------------------------

        first_price = df_chart["price"].iloc[0]

        last_price = df_chart["price"].iloc[-1]

        change_pct = (
            (last_price - first_price)
            / first_price
        ) * 100

        ath_price = df_chart["price"].max()

        atl_price = df_chart["price"].min()

        avg_price = df_chart["price"].mean()

        # ---------------------------------------------
        # Line Chart
        # ---------------------------------------------

        fig = px.line(
            df_chart,
            x="datetime",
            y="price",
            title=f"{symbol} Price History"
        )

        fig.update_traces(
            line_width=3
        )

        fig.update_layout(
            height=600,
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ---------------------------------------------
        # KPI Row 1
        # ---------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Start Price",
                f"${first_price:,.6f}"
            )

        with col2:
            st.metric(
                "End Price",
                f"${last_price:,.6f}"
            )

        with col3:
            st.metric(
                "Change %",
                f"{change_pct:.2f}%"
            )

        # ---------------------------------------------
        # KPI Row 2
        # ---------------------------------------------

        col4, col5, col6 = st.columns(3)

        with col4:
            st.metric(
                "ATH Price",
                f"${ath_price:,.6f}"
            )

        with col5:
            st.metric(
                "ATL Price",
                f"${atl_price:,.6f}"
            )

        with col6:
            st.metric(
                "Avg Price",
                f"${avg_price:,.6f}"
            )

        # ---------------------------------------------
        # Daily Candlestick Chart
        # ---------------------------------------------

        st.subheader("🕯️ Daily Candlestick Chart")

        if period == "1D":

            st.info(
                "For meaningful candlesticks, use 1H, 4H or 12H intervals."
            )

        if len(df_chart) > 5000:

            st.warning(
                "Too many data points for candlestick chart. Consider increasing interval."
            )

        df_daily = df_chart.copy()

        df_daily["date"] = (
            df_daily["datetime"]
            .dt
            .floor("D")
        )

        ohlc = (
            df_daily
            .groupby("date")["price"]
            .agg(
                Open="first",
                High="max",
                Low="min",
                Close="last"
            )
            .reset_index()
        )

        if len(ohlc) > 0:

            candle_fig = go.Figure(
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

            candle_fig.update_layout(
                title=f"{symbol} Daily OHLC",
                height=700,
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                xaxis_rangeslider_visible=False
            )

            st.plotly_chart(
                candle_fig,
                use_container_width=True
            )

    except Exception as e:

        st.error(f"Error: {e}")
