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
st.divider()
st.header("📅 Historical Token Price")
