import streamlit as st
import requests
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

    # -------------------------------------------------
    # LAST UPDATE
    # -------------------------------------------------

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
