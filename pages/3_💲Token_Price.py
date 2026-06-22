import streamlit as st
import requests

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Token Price",
    layout="wide"
)

st.title("🪙 Token Price")

# =====================================================
# CUSTOM KPI CSS
# =====================================================

st.markdown("""
<style>

.token-kpi {
    background: linear-gradient(
        135deg,
        rgba(34,197,94,0.20),
        rgba(22,163,74,0.08)
    );
    border: 1px solid rgba(34,197,94,0.35);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    box-shadow: 0px 6px 20px rgba(34,197,94,0.15);
}

.token-kpi-title {
    font-size: 18px;
    font-weight: 700;
    color: #22c55e;
    margin-bottom: 15px;
}

.token-kpi-price {
    font-size: 42px;
    font-weight: 800;
    color: white;
}

.token-kpi-symbol {
    font-size: 22px;
    font-weight: 700;
    color: #a7f3d0;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# API FUNCTION
# =====================================================

@st.cache_data(ttl=300)
def get_token_price(chain, address):

    coin = f"{chain}:{address}"

    url = f"https://coins.llama.fi/prices/current/{coin}"

    response = requests.get(url, timeout=20)

    response.raise_for_status()

    data = response.json()

    coin_data = data["coins"].get(coin)

    return coin_data


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
        placeholder="0xdAC17F958D2ee523a2206206994597C13D831ec7"
    )

# =====================================================
# SEARCH
# =====================================================

if st.button("Get Token Price", use_container_width=True):

    if not chain or not address:
        st.warning("Please enter chain and token address.")
        st.stop()

    try:

        token = get_token_price(chain, address)

        if token is None:
            st.error("Token not found.")
            st.stop()

        price = token.get("price", 0)
        symbol = token.get("symbol", "Unknown")
        decimals = token.get("decimals", "-")
        confidence = token.get("confidence", "-")

        # =============================================
        # BEAUTIFUL KPI
        # =============================================

        st.markdown(
            f"""
            <div class="token-kpi">
                <div class="token-kpi-title">
                    Current Price ({symbol})
                </div>

                <div class="token-kpi-price">
                    ${price:,.6f}
                </div>

                <div class="token-kpi-symbol">
                    {symbol}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        # =============================================
        # EXTRA INFO
        # =============================================

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Symbol",
                symbol
            )

        with c2:
            st.metric(
                "Decimals",
                decimals
            )

        with c3:
            st.metric(
                "Confidence",
                f"{confidence:.2%}"
                if isinstance(confidence, float)
                else confidence
            )

    except Exception as e:
        st.error(f"Error: {e}")
