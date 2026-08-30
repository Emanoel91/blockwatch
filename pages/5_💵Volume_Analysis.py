import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Volume Spikes",
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

        if response.status_code == 404:
            return None

        if not response.ok:
            raise RuntimeError(
                f"CoinGecko API error {response.status_code}: {response.text}"
            )

        return response

    raise RuntimeError("CoinGecko API request failed after retries.")

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
# FETCH CURRENT MARKET DATA (1 API call)
# =====================================================

@st.cache_data(ttl=1800)
def fetch_current_markets(vs_currency="usd", per_page=100):

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": "false"
    }

    response = _coingecko_get(url, params=params)

    return pd.DataFrame(response.json())

# =====================================================
# FETCH YESTERDAY'S VOLUME PER COIN (1 API call per coin)
# =====================================================

def fetch_yesterday_volume(coin_id, date_str):

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/history"

    params = {
        "date": date_str,
        "localization": "false"
    }

    response = _coingecko_get(url, params=params)

    if response is None:
        return None

    data = response.json()

    try:
        return data["market_data"]["total_volume"]["usd"]
    except (KeyError, TypeError):
        return None


@st.cache_data(ttl=21600)
def fetch_volume_spikes(universe_size, sleep_seconds):

    df = fetch_current_markets(per_page=universe_size)

    yesterday_str = (
        datetime.now(timezone.utc) - timedelta(days=1)
    ).strftime("%d-%m-%Y")

    yesterday_volumes = []

    for coin_id in df["id"]:

        vol_yesterday = fetch_yesterday_volume(coin_id, yesterday_str)
        yesterday_volumes.append(vol_yesterday)

        time.sleep(sleep_seconds)

    df["volume_yesterday"] = yesterday_volumes

    df = df.dropna(subset=["volume_yesterday", "total_volume"])
    df = df[df["volume_yesterday"] > 0]

    df["volume_change_pct"] = (
        (df["total_volume"] - df["volume_yesterday"])
        / df["volume_yesterday"] * 100
    )

    return df

# =====================================================
# CHART BUILDER
# =====================================================

def build_volume_chart(df, top_n=10):

    d = df.sort_values("volume_change_pct", ascending=False).head(top_n)
    d = d.sort_values("volume_change_pct", ascending=True)

    colors = ["#16c784" if v >= 0 else "#ea3943" for v in d["volume_change_pct"]]

    labels = [
        f"{sym.upper()} ({name})"
        for sym, name in zip(d["symbol"], d["name"])
    ]

    fig = go.Figure(
        go.Bar(
            x=d["volume_change_pct"],
            y=labels,
            orientation="h",
            marker_color=colors,
            text=[f"{v:+.1f}%" for v in d["volume_change_pct"]],
            textposition="outside"
        )
    )

    fig.update_layout(
        height=500,
        title="Top 10 Volume Increase vs Previous Day",
        xaxis_title="Volume Change % (vs yesterday)",
        margin=dict(l=10, r=60, t=60, b=10)
    )

    return fig

# =====================================================
# HEADER
# =====================================================

st.title("📊 Volume Spikes")

st.info(
    "🔍 ۱۰ ارزی که حجم معاملات ۲۴ ساعته‌شان نسبت به روز قبل بیشترین "
    "افزایش را داشته‌اند (منبع: CoinGecko)."
)

# =====================================================
# SETTINGS
# =====================================================

col1, col2 = st.columns(2)

with col1:

    universe_size = st.selectbox(
        "Universe (بر اساس مارکت‌کپ)",
        [30, 50, 100, 150],
        index=1,
        help="تعداد ارزهای برتری که برای مقایسه حجم بررسی می‌شوند. عدد بزرگ‌تر یعنی دقت بیشتر ولی زمان و ریسک rate limit بیشتر."
    )

with col2:

    sleep_seconds = st.selectbox(
        "فاصله بین درخواست‌ها (ثانیه)",
        [1.0, 1.5, 2.0, 3.0],
        index=1,
        help="فاصله بیشتر یعنی ریسک کمتر برای خطای 429 ولی زمان بارگذاری بیشتر."
    )

st.caption(
    f"⚠️ این بررسی برای هر ارز یک درخواست جداگانه به CoinGecko می‌زند "
    f"(یعنی برای Universe={universe_size}، حدود {universe_size} درخواست + کمی تأخیر بین آن‌ها). "
    "به همین دلیل به‌صورت خودکار اجرا نمی‌شود — روی دکمه زیر بزن."
)

load_data = st.button("📥 Scan Volume Spikes")

if "volume_df" not in st.session_state:
    st.session_state["volume_df"] = None

# =====================================================
# LOAD & DISPLAY
# =====================================================

try:

    if load_data:

        with st.spinner(f"در حال بررسی حجم {universe_size} ارز برتر... این ممکن است کمی طول بکشد."):
            st.session_state["volume_df"] = fetch_volume_spikes(universe_size, sleep_seconds)

    result_df = st.session_state["volume_df"]

    if result_df is None:

        st.info("برای شروع بررسی، روی دکمه «📥 Scan Volume Spikes» کلیک کن.")

    elif result_df.empty:

        st.warning("داده‌ای برای مقایسه حجم پیدا نشد.")

    else:

        fig = build_volume_chart(result_df)
        st.plotly_chart(fig, width="stretch")

        st.divider()

        with st.expander("🔍 View Full Comparison Table"):

            display_df = result_df[[
                "symbol", "name", "total_volume",
                "volume_yesterday", "volume_change_pct", "current_price"
            ]].sort_values("volume_change_pct", ascending=False).reset_index(drop=True)

            display_df["total_volume"] = display_df["total_volume"].apply(format_number)
            display_df["volume_yesterday"] = display_df["volume_yesterday"].apply(format_number)
            display_df["volume_change_pct"] = display_df["volume_change_pct"].round(2)

            st.dataframe(display_df, width="stretch")

except Exception as e:

    st.error(f"Failed to load data: {e}")
