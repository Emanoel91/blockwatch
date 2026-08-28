import streamlit as st
import requests
import pandas as pd
import time
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Top Gainers",
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

</style>
""", unsafe_allow_html=True)

# =====================================================
# COINGECKO REQUEST HELPER (with retry/backoff on 429)
# =====================================================

# اختیاری: اگه یک کلید رایگان Demo API از CoinGecko داری، آن را در
# secrets.toml با نام COINGECKO_API_KEY اضافه کن تا محدودیت نرخ
# درخواست بالاتر بره. اگه نداری، کد بدون کلید هم کار می‌کنه.
COINGECKO_API_KEY = st.secrets.get("COINGECKO_API_KEY", None)


def _coingecko_get(url, params=None, max_retries=4):

    headers = {}

    if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY

    delay = 5

    for attempt in range(max_retries):

        response = requests.get(url, params=params, headers=headers, timeout=30)

        if response.status_code == 429:

            retry_after = response.headers.get("Retry-After")
            wait_time = float(retry_after) if retry_after else delay

            if attempt < max_retries - 1:
                time.sleep(wait_time)
                delay *= 2
                continue

            raise RuntimeError(
                f"CoinGecko API error 429: Rate limit exceeded after "
                f"{max_retries} retries. {response.text}"
            )

        if not response.ok:
            raise RuntimeError(
                f"CoinGecko API error {response.status_code}: {response.text}"
            )

        return response

    raise RuntimeError("CoinGecko API request failed after retries.")

# =====================================================
# FETCH DATA
# =====================================================

SCAN_SIZE = 250  # تعداد ارزهای برتر (بر اساس مارکت‌کپ) که برای رتبه‌بندی بررسی می‌شوند


@st.cache_data(ttl=1800)
def fetch_market_data(vs_currency="usd", per_page=SCAN_SIZE):

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h,7d,30d"
    }

    response = _coingecko_get(url, params=params)

    df = pd.DataFrame(response.json())

    return df

# =====================================================
# CHART BUILDER
# =====================================================

def build_gainers_chart(df, column, title, top_n=10):

    d = df.dropna(subset=[column]).copy()

    d = d.sort_values(column, ascending=False).head(top_n)

    # برای نمودار افقی، مرتب‌سازی صعودی می‌کنیم تا بیشترین مقدار بالای نمودار قرار بگیرد
    d = d.sort_values(column, ascending=True)

    colors = ["#16c784" if v >= 0 else "#ea3943" for v in d[column]]

    labels = [
        f"{sym.upper()} ({name})"
        for sym, name in zip(d["symbol"], d["name"])
    ]

    fig = go.Figure(
        go.Bar(
            x=d[column],
            y=labels,
            orientation="h",
            marker_color=colors,
            text=[f"{v:+.2f}%" for v in d[column]],
            textposition="outside"
        )
    )

    fig.update_layout(
        height=450,
        title=title,
        xaxis_title="Price Change %",
        margin=dict(l=10, r=60, t=60, b=10)
    )

    return fig

# =====================================================
# HEADER
# =====================================================

st.title("🚀 Top Gainers")

st.info(
    f"📊 ۱۰ ارز برتر بر اساس بیشترین رشد قیمت در بازه‌های ۲۴ ساعته، "
    f"۷ روزه و ۳۰ روزه (از میان {SCAN_SIZE} ارز برتر بر اساس مارکت‌کپ — منبع: CoinGecko)."
)

# =====================================================
# LOAD DATA
# =====================================================

try:

    df = fetch_market_data()

    # -------------------------------------------------
    # 24H TOP GAINERS
    # -------------------------------------------------

    st.subheader("⏱️ Top 10 Gainers — Last 24 Hours")

    fig_24h = build_gainers_chart(
        df,
        "price_change_percentage_24h_in_currency",
        "Top 10 Gainers (24H)"
    )

    st.plotly_chart(fig_24h, width="stretch")

    st.divider()

    # -------------------------------------------------
    # 7D TOP GAINERS
    # -------------------------------------------------

    st.subheader("📅 Top 10 Gainers — Last 7 Days")

    fig_7d = build_gainers_chart(
        df,
        "price_change_percentage_7d_in_currency",
        "Top 10 Gainers (7D)"
    )

    st.plotly_chart(fig_7d, width="stretch")

    st.divider()

    # -------------------------------------------------
    # 30D TOP GAINERS
    # -------------------------------------------------

    st.subheader("🗓️ Top 10 Gainers — Last 30 Days")

    fig_30d = build_gainers_chart(
        df,
        "price_change_percentage_30d_in_currency",
        "Top 10 Gainers (30D)"
    )

    st.plotly_chart(fig_30d, width="stretch")

    st.divider()

    # -------------------------------------------------
    # RAW DATA
    # -------------------------------------------------

    with st.expander("🔍 View Raw Market Data"):

        st.dataframe(
            df[[
                "symbol", "name", "current_price",
                "price_change_percentage_24h_in_currency",
                "price_change_percentage_7d_in_currency",
                "price_change_percentage_30d_in_currency",
                "market_cap"
            ]],
            width="stretch"
        )

except Exception as e:

    st.error(f"Failed to load data: {e}")
