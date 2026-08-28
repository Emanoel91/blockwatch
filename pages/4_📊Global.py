import streamlit as st
import requests
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Global",
    layout="wide"
)

# =====================================================
# API KEY
# =====================================================

# بهتر است کلید API را داخل .streamlit/secrets.toml قرار دهید:
# CRYPTORANK_API_KEY = "e8d6bf058e3f0210b43ad8c89131bbd32e83aae1c86ff1e5009adbbda66a"
API_KEY = st.secrets["CRYPTORANK_API_KEY"]

BASE_URL = "https://api.cryptorank.io/v3"

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
    "BTC Dominance Change 24H": "تغییر سهم بیت‌کوین طی ۲۴ ساعت گذشته (٪).",
    "ETH Dominance": "سهم اتریوم از کل مارکت‌کپ کریپتو (٪).",
    "ETH Dominance Change 24H": "تغییر سهم اتریوم طی ۲۴ ساعت گذشته (٪).",
    "Others Dominance": "سهم سایر ارزها (به‌جز BTC و ETH) از کل مارکت‌کپ (٪).",
}

# =====================================================
# FETCH DATA
# =====================================================

@st.cache_data(ttl=7200)
def fetch_dominance():

    url = f"{BASE_URL}/global/dominance"

    headers = {
        "X-Api-Key": API_KEY
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()["data"]

# =====================================================
# KPI RENDER
# =====================================================

def show_metrics(metrics, cols=4):

    for i in range(0, len(metrics), cols):

        row = st.columns(cols)
        chunk = metrics[i:i + cols]

        for col, (label, value) in zip(row, chunk):

            with col:

                st.metric(
                    label=label,
                    value=f"{value:.2f}%" if value is not None else "-",
                    help=KPI_HELP.get(label)
                )

# =====================================================
# HEADER
# =====================================================

st.title("🌐 Global Market Dominance")

st.info(
    "📊 سهم بازار بیت‌کوین، اتریوم و سایر ارزها از کل مارکت‌کپ کریپتو (منبع: CryptoRank)."
)

# =====================================================
# LOAD DATA
# =====================================================

try:

    data = fetch_dominance()

    btc_dom = data.get("btcDominance")
    btc_change = data.get("btcDominanceChangePercent24h")
    eth_dom = data.get("ethDominance")
    eth_change = data.get("ethDominanceChangePercent24h")
    others_dom = data.get("othersDominance")

    # -------------------------------------------------
    # METRICS
    # -------------------------------------------------

    show_metrics([
        ("BTC Dominance", btc_dom),
        ("BTC Dominance Change 24H", btc_change),
        ("ETH Dominance", eth_dom),
        ("ETH Dominance Change 24H", eth_change),
    ])

    show_metrics([
        ("Others Dominance", others_dom),
    ], cols=4)

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

    st.plotly_chart(fig_pie, use_container_width=True)

    # -------------------------------------------------
    # 24H CHANGE BAR CHART
    # -------------------------------------------------

    st.subheader("📉 24H Dominance Change")

    fig_bar = go.Figure()

    fig_bar.add_trace(
        go.Bar(
            x=["BTC", "ETH"],
            y=[btc_change, eth_change],
            marker_color=[
                "green" if btc_change and btc_change >= 0 else "red",
                "green" if eth_change and eth_change >= 0 else "red"
            ]
        )
    )

    fig_bar.update_layout(
        height=450,
        title="Dominance Change % (24H)",
        yaxis_title="Change %"
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # -------------------------------------------------
    # RAW DATA
    # -------------------------------------------------

    with st.expander("🔍 View Raw API Response"):

        st.json(data)

except Exception as e:

    st.error(f"Failed to load data: {e}")
