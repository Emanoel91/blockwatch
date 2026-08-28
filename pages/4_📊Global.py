import streamlit as st
import requests
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime, timezone

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Global",
    layout="wide"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

div[data-testid="stMetricValue"] {
    font-size: 34px !important;
    font-weight: bold !important;
}

div[data-testid="stMetricLabel"] {
    font-size: 16px !important;
    font-weight: bold !important;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg,#1c1c1c,#111111);
    border: 1px solid rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.25);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# KPI HELP
# =====================================================

KPI_HELP = {
    "BTC Dominance": "سهم بیت‌کوین از کل مارکت‌کپ کریپتو (٪).",
    "ETH Dominance": "سهم اتریوم از کل مارکت‌کپ کریپتو (٪).",
    "Others Dominance": "سهم سایر ارزها (به‌جز BTC و ETH) از کل مارکت‌کپ (٪).",
    "Total Market Cap": "کل ارزش بازار جهانی کریپتو (دلار).",
    "Total Volume 24H": "کل حجم معاملات ۲۴ ساعت گذشته بازار (دلار).",
    "Market Cap Change 24H": "تغییر کل ارزش بازار طی ۲۴ ساعت گذشته (٪).",
    "Active Cryptocurrencies": "تعداد ارزهای دیجیتال فعال شناسایی‌شده.",
    "Markets": "تعداد صرافی‌ها/بازارهای شناسایی‌شده.",
}

# =====================================================
# FORMATTER
# =====================================================

def format_number(value):

    if value is None:
        return "-"

    try:

        value = float(value)

        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"

        if value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"

        if value >= 1_000:
            return f"{value / 1_000:.2f}K"

        return f"{value:,.2f}"

    except Exception:
        return str(value)

# =====================================================
# FETCH DATA (CoinGecko - free, no API key required)
# =====================================================

@st.cache_data(ttl=1800)
def fetch_global_data():

    url = "https://api.coingecko.com/api/v3/global"

    response = requests.get(url, timeout=30)

    if not response.ok:
        raise RuntimeError(
            f"CoinGecko API error {response.status_code}: {response.text}"
        )

    return response.json()["data"]

# =====================================================
# FETCH DOMINANCE HISTORY (approximate, top-N coins)
# =====================================================
# توضیح: CoinGecko در پلن رایگان، تاریخچه دامیننس کل بازار را
# نمی‌دهد. برای تخمین آن، مارکت‌کپ تاریخی چند ارز برتر را جمع
# می‌زنیم و به‌عنوان «کل بازار» در نظر می‌گیریم. این یک تخمین
# است، نه عدد دقیق رسمی.

TOP_N_FOR_HISTORY = 12


def _fetch_market_chart(coin_id, days):

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"

    params = {
        "vs_currency": "usd",
        "days": days
    }

    response = requests.get(url, params=params, timeout=30)

    if not response.ok:
        raise RuntimeError(
            f"CoinGecko API error {response.status_code} "
            f"for {coin_id}: {response.text}"
        )

    return response.json()


def _market_caps_to_daily_series(raw_json, label):

    df = pd.DataFrame(raw_json.get("market_caps", []), columns=["timestamp", label])

    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
    df = df.groupby("date")[label].last().reset_index()

    return df.set_index("date")


@st.cache_data(ttl=21600)
def fetch_dominance_history(days, top_n=TOP_N_FOR_HISTORY):

    markets_url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": top_n,
        "page": 1,
        "sparkline": "false"
    }

    response = requests.get(markets_url, params=params, timeout=30)

    if not response.ok:
        raise RuntimeError(
            f"CoinGecko API error {response.status_code}: {response.text}"
        )

    top_coins = response.json()

    series_list = []

    for coin in top_coins:

        coin_id = coin["id"]

        raw = _fetch_market_chart(coin_id, days)

        series = _market_caps_to_daily_series(raw, coin_id)

        if not series.empty:
            series_list.append(series)

        # فاصله کوچک بین درخواست‌ها برای جلوگیری از rate limit
        time.sleep(1.3)

    if not series_list:
        raise RuntimeError("No historical market cap data returned.")

    merged = pd.concat(series_list, axis=1).sort_index()
    merged = merged.ffill().dropna(how="all")

    coin_columns = [c for c in merged.columns]
    merged["total"] = merged[coin_columns].sum(axis=1)

    merged["btc_dominance"] = merged.get("bitcoin", 0) / merged["total"] * 100
    merged["eth_dominance"] = merged.get("ethereum", 0) / merged["total"] * 100
    merged["others_dominance"] = (
        100 - merged["btc_dominance"] - merged["eth_dominance"]
    )

    return merged.reset_index()

# =====================================================
# KPI RENDER
# =====================================================

def show_metrics(metrics, cols=4):

    for i in range(0, len(metrics), cols):

        row = st.columns(cols)
        chunk = metrics[i:i + cols]

        for col, (label, value, is_pct) in zip(row, chunk):

            with col:

                if value is None:
                    display_value = "-"
                elif is_pct:
                    display_value = f"{value:.2f}%"
                else:
                    display_value = format_number(value)

                st.metric(
                    label=label,
                    value=display_value,
                    help=KPI_HELP.get(label)
                )

# =====================================================
# HEADER
# =====================================================

st.title("🌐 Global Market Dominance")

st.info(
    "📊 سهم بازار بیت‌کوین، اتریوم و سایر ارزها از کل مارکت‌کپ کریپتو (منبع: CoinGecko)."
)

# =====================================================
# LOAD DATA
# =====================================================

try:

    data = fetch_global_data()

    market_cap_pct = data.get("market_cap_percentage", {})

    btc_dom = market_cap_pct.get("btc")
    eth_dom = market_cap_pct.get("eth")
    others_dom = None

    if btc_dom is not None and eth_dom is not None:
        others_dom = max(0.0, 100 - btc_dom - eth_dom)

    total_market_cap = data.get("total_market_cap", {}).get("usd")
    total_volume = data.get("total_volume", {}).get("usd")
    market_cap_change_24h = data.get("market_cap_change_percentage_24h_usd")
    active_cryptos = data.get("active_cryptocurrencies")
    markets = data.get("markets")
    updated_at = data.get("updated_at")

    # -------------------------------------------------
    # DOMINANCE METRICS
    # -------------------------------------------------

    st.subheader("🪙 Dominance")

    show_metrics([
        ("BTC Dominance", btc_dom, True),
        ("ETH Dominance", eth_dom, True),
        ("Others Dominance", others_dom, True),
    ], cols=3)

    st.divider()

    # -------------------------------------------------
    # MARKET OVERVIEW METRICS
    # -------------------------------------------------

    st.subheader("💰 Market Overview")

    show_metrics([
        ("Total Market Cap", total_market_cap, False),
        ("Total Volume 24H", total_volume, False),
        ("Market Cap Change 24H", market_cap_change_24h, True),
        ("Active Cryptocurrencies", active_cryptos, False),
    ])

    st.divider()

    # -------------------------------------------------
    # PIE / DONUT CHART
    # -------------------------------------------------

    st.subheader("🥧 Market Cap Share")

    labels = ["BTC", "ETH", "Others"]
    values = [btc_dom, eth_dom, others_dom]
    colors = ["#f7931a", "#627eea", "#4a4a4a"]

    fig_pie = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors),
                textinfo="label+percent"
            )
        ]
    )

    fig_pie.update_layout(
        height=500,
        title="BTC vs ETH vs Others Dominance"
    )

    st.plotly_chart(fig_pie, width="stretch")

    # -------------------------------------------------
    # TOP COINS DOMINANCE BAR CHART
    # -------------------------------------------------

    st.subheader("📊 Top Coins Market Cap Share")

    top_items = sorted(
        market_cap_pct.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    fig_bar = go.Figure()

    fig_bar.add_trace(
        go.Bar(
            x=[coin.upper() for coin, _ in top_items],
            y=[pct for _, pct in top_items],
            marker_color="#264e72"
        )
    )

    fig_bar.update_layout(
        height=450,
        title="Top 10 Coins by Market Cap Share (%)",
        yaxis_title="Dominance %"
    )

    st.plotly_chart(fig_bar, width="stretch")

    st.divider()

    # -------------------------------------------------
    # DOMINANCE OVER TIME (approximate)
    # -------------------------------------------------

    st.subheader("📈 Dominance Over Time (BTC vs ETH vs Others)")

    st.caption(
        "⚠️ این نمودار بر اساس مجموع مارکت‌کپ تاریخی "
        f"{TOP_N_FOR_HISTORY} ارز برتر تخمین زده شده "
        "(چون CoinGecko در پلن رایگان تاریخچه دامیننس کل بازار را نمی‌دهد)."
    )

    days_option = st.selectbox(
        "Time Range",
        ["7", "30", "90", "180", "365"],
        index=1
    )

    try:

        hist_df = fetch_dominance_history(int(days_option))

        fig_dom_history = go.Figure()

        fig_dom_history.add_trace(
            go.Scatter(
                x=hist_df["date"],
                y=hist_df["btc_dominance"],
                mode="lines",
                name="BTC",
                stackgroup="one",
                line=dict(color="#f7931a")
            )
        )

        fig_dom_history.add_trace(
            go.Scatter(
                x=hist_df["date"],
                y=hist_df["eth_dominance"],
                mode="lines",
                name="ETH",
                stackgroup="one",
                line=dict(color="#627eea")
            )
        )

        fig_dom_history.add_trace(
            go.Scatter(
                x=hist_df["date"],
                y=hist_df["others_dominance"],
                mode="lines",
                name="Others",
                stackgroup="one",
                line=dict(color="#4a4a4a")
            )
        )

        fig_dom_history.update_layout(
            height=550,
            title=f"Dominance Over Last {days_option} Days (Approximate)",
            yaxis_title="Dominance %",
            yaxis_range=[0, 100],
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig_dom_history, width="stretch")

    except Exception as hist_error:

        st.warning(f"Could not load dominance history: {hist_error}")

    st.divider()

    if updated_at:
        updated_str = datetime.fromtimestamp(
            updated_at, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S UTC")

        st.caption(f"Last update: {updated_str}")

    # -------------------------------------------------
    # RAW DATA
    # -------------------------------------------------

    with st.expander("🔍 View Raw API Response"):

        st.json(data)

except Exception as e:

    st.error(f"Failed to load data: {e}")
