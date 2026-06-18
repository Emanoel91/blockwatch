import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# HELPERS
# =====================================================

def build_coin(chain, address):
    return f"{chain}:{address}"

def format_price(x):
    if x is None:
        return "N/A"
    return f"${x:.6f}"


@st.cache_data(ttl=600)
def get_current_price(coin):
    url = f"https://coins.llama.fi/prices/current/{coin}"
    r = requests.get(url).json()
    data = r["coins"].get(coin, {})
    return data.get("price", None)


@st.cache_data(ttl=600)
def get_first_price(coin):
    url = f"https://coins.llama.fi/prices/first/{coin}"
    r = requests.get(url).json()
    data = r["coins"].get(coin, {})
    return data.get("price", None), data.get("timestamp", None)


@st.cache_data(ttl=600)
def get_percentage(coin, period="24h"):
    url = f"https://coins.llama.fi/percentage/{coin}?period={period}"
    r = requests.get(url).json()
    return r["coins"].get(coin, None)


@st.cache_data(ttl=600)
def get_chart(coin, start=None, span="24h", period="1h"):
    url = f"https://coins.llama.fi/chart/{coin}"
    params = {"span": span, "period": period}
    if start:
        params["start"] = start

    r = requests.get(url, params=params).json()
    data = r["coins"].get(coin, {})
    return pd.DataFrame(data.get("prices", []))


def calc_avg(series):
    return series.mean() if len(series) > 0 else None


# =====================================================
# UI
# =====================================================

st.header("Token Price Analysis")

chain = st.text_input("Chain (e.g. ethereum)")
address = st.text_input("Token Contract Address")

coin = None
if chain and address:
    coin = build_coin(chain, address)

# =====================================================
# SINGLE TOKEN ANALYSIS
# =====================================================

if coin:

    current_price = get_current_price(coin)
    first_price, first_ts = get_first_price(coin)

    # chart data (default last 30d)
    df_chart = get_chart(
        coin,
        span="30d",
        period="1h"
    )

    if not df_chart.empty:
        df_chart["timestamp"] = pd.to_datetime(df_chart["timestamp"], unit="s")

        ath = df_chart["price"].max()
        atl = df_chart["price"].min()
        avg = calc_avg(df_chart["price"])

    else:
        ath = atl = avg = None

    # percentages
    pct_1d = get_percentage(coin, "24h")
    pct_7d = get_percentage(coin, "7d")
    pct_30d = get_percentage(coin, "30d")
    pct_6m = get_percentage(coin, "180d")
    pct_1y = get_percentage(coin, "365d")

    # =================================================
    # KPI SECTION
    # =================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current Price", format_price(current_price))

    with col2:
        st.metric("ATH Price", format_price(ath))

    with col3:
        st.metric("ATL Price", format_price(atl))

    with col4:
        st.metric("Average Price", format_price(avg))

    # =================================================
    # EXTRA KPI ROW
    # =================================================

    col1, col2, col3 = st.columns(3)

    def pct_vs(ref):
        if ref and current_price:
            return ((current_price - ref) / ref) * 100
        return None

    with col1:
        st.metric("% vs ATH", f"{pct_vs(ath):.2f}%" if pct_vs(ath) else "N/A")

    with col2:
        st.metric("% vs ATL", f"{pct_vs(atl):.2f}%" if pct_vs(atl) else "N/A")

    with col3:
        st.metric("% vs First Price", f"{pct_vs(first_price):.2f}%" if pct_vs(first_price) else "N/A")

    # =================================================
    # TIMEFRAME SELECTOR
    # =================================================

    st.subheader("Price Chart")

    timeframe = st.selectbox(
        "Timeframe",
        ["7d", "30d", "90d", "180d", "365d"]
    )

    df_chart = get_chart(coin, span=timeframe, period="1h")

    if not df_chart.empty:
        df_chart["timestamp"] = pd.to_datetime(df_chart["timestamp"], unit="s")

        fig = px.line(
            df_chart,
            x="timestamp",
            y="price",
            title="Token Price Over Time"
        )

        st.plotly_chart(fig, use_container_width=True)

    # =================================================
    # MOVING AVERAGES
    # =================================================

    if not df_chart.empty:
        df_chart["MA7"] = df_chart["price"].rolling(7).mean()
        df_chart["MA15"] = df_chart["price"].rolling(15).mean()
        df_chart["MA30"] = df_chart["price"].rolling(30).mean()

        fig_ma = go.Figure()

        fig_ma.add_trace(go.Scatter(x=df_chart["timestamp"], y=df_chart["MA7"], name="MA 7"))
        fig_ma.add_trace(go.Scatter(x=df_chart["timestamp"], y=df_chart["MA15"], name="MA 15"))
        fig_ma.add_trace(go.Scatter(x=df_chart["timestamp"], y=df_chart["MA30"], name="MA 30"))

        fig_ma.update_layout(title="Moving Averages")

        st.plotly_chart(fig_ma, use_container_width=True)

    # =================================================
    # DAILY CHANGE (APPROX USING CHART)
    # =================================================

    if not df_chart.empty:
        df_chart["daily_return"] = df_chart["price"].pct_change() * 100

        fig_ret = px.line(
            df_chart,
            x="timestamp",
            y="daily_return",
            title="Daily Price Change %"
        )

        st.plotly_chart(fig_ret, use_container_width=True)


# =====================================================
# MULTI TOKEN COMPARISON (2-5 TOKENS)
# =====================================================

st.divider()
st.subheader("Token Comparison (2–5 tokens)")

tokens_input = st.text_area(
    "Enter tokens (format: chain:address, one per line)"
)

if tokens_input:

    tokens = [t.strip() for t in tokens_input.split("\n") if t.strip()]

    if 2 <= len(tokens) <= 5:

        prices = {}
        aths = {}
        atls = {}
        p7d = {}
        p30d = {}
        p1y = {}

        for t in tokens:
            prices[t] = get_current_price(t)
            aths[t], _ = get_first_price(t)  # approximation baseline

            p7d[t] = get_percentage(t, "7d")
            p30d[t] = get_percentage(t, "30d")
            p1y[t] = get_percentage(t, "365d")

        # =================================================
        # KPI ROWS
        # =================================================

        st.markdown("### Current Prices")
        cols = st.columns(len(tokens))
        for i, t in enumerate(tokens):
            with cols[i]:
                st.metric(t, format_price(prices[t]))

        st.markdown("### % Change 7D")
        cols = st.columns(len(tokens))
        for i, t in enumerate(tokens):
            with cols[i]:
                st.metric(t, f"{p7d[t]}%" if p7d[t] else "N/A")

        st.markdown("### % Change 30D")
        cols = st.columns(len(tokens))
        for i, t in enumerate(tokens):
            with cols[i]:
                st.metric(t, f"{p30d[t]}%" if p30d[t] else "N/A")

        st.markdown("### % Change 1Y")
        cols = st.columns(len(tokens))
        for i, t in enumerate(tokens):
            with cols[i]:
                st.metric(t, f"{p1y[t]}%" if p1y[t] else "N/A")

        # =================================================
        # COMPARE CHART
        # =================================================

        fig = go.Figure()

        for t in tokens:
            df = get_chart(t, span="30d", period="1h")
            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
                fig.add_trace(
                    go.Scatter(
                        x=df["timestamp"],
                        y=df["price"],
                        mode="lines",
                        name=t
                    )
                )

        fig.update_layout(title="Price Comparison Chart")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Please enter between 2 and 5 tokens")
