import streamlit as st
import requests
import pandas as pd
import os

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Blockscout Multi-Chain Dashboard",
    layout="wide"
)

# =====================================================
# API KEY
# =====================================================

API_KEY = "YOUR_API_KEY"

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg,#1c1c1c,#111111);
    border: 1px solid rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.25);
}

[data-testid="metric-container"] label {
    color: #9f9f9f !important;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# NETWORKS
# =====================================================

MAINNETS = {
    "Ethereum": {
        "chain_id": 1,
        "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/ethereum.svg"
    },
    "Base": {
        "chain_id": 8453,
        "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/base.svg"
    },
    "Polygon PoS": {
        "chain_id": 137,
        "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/polygon-pos.svg"
    },
    "OP Mainnet": {
        "chain_id": 10,
        "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/op-mainnet.svg"
    },
    "Arbitrum One Nitro": {
        "chain_id": 42161,
        "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/arbitrum-one-nitro.svg"
    },
    "Scroll": {
        "chain_id": 534352,
        "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/scroll.svg"
    },
    "ZKsync Era": {
        "chain_id": 324,
        "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/zksync-era.svg"
    }
}

TESTNETS = {
    "Arc Testnet": {
        "chain_id": 5042002,
        "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/Arc.svg"
    },
    "Ethereum Sepolia": {
        "chain_id": 11155111,
        "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/ethereum.svg"
    },
    "Base Sepolia": {
        "chain_id": 84532,
        "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/base-sepolia.svg"
    },
    "Arbitrum Sepolia": {
        "chain_id": 421614,
        "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/arbitrum.svg"
    },
    "OP Sepolia": {
        "chain_id": 11155420,
        "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/op-mainnet.svg"
    }
}

NETWORKS = {
    "Mainnet": MAINNETS,
    "Testnet": TESTNETS
}

# =====================================================
# HELPERS
# =====================================================

def format_number(value):

    if value is None:
        return "-"

    try:
        value = float(value)

        if value >= 1_000_000_000:
            return f"{value/1_000_000_000:.2f}B"

        if value >= 1_000_000:
            return f"{value/1_000_000:.2f}M"

        if value >= 1_000:
            return f"{value/1_000:.2f}K"

        if value.is_integer():
            return f"{int(value):,}"

        return f"{value:,.4f}"

    except:
        return str(value)


@st.cache_data(ttl=300)
def fetch_stats(chain_id):

    API_KEY = os.getenv("BLOCKSCOUT_API_KEY")

    url = (
        f"https://api.blockscout.com/{chain_id}"
        f"/api/v2/stats?apikey={API_KEY}"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return response.json()


# =====================================================
# HEADER
# =====================================================

st.title("🌐 Blockscout Multi-Chain Dashboard")

st.info(
    "Select Mainnet/Testnet and a blockchain network to view live Blockscout statistics."
)

# =====================================================
# FILTERS
# =====================================================

col1, col2 = st.columns(2)

with col1:
    network_type = st.selectbox(
        "Network Type",
        ["Mainnet", "Testnet"]
    )

available_chains = list(
    NETWORKS[network_type].keys()
)

with col2:
    chain_name = st.selectbox(
        "Blockchain",
        available_chains
    )

selected_chain = NETWORKS[network_type][chain_name]

chain_id = selected_chain["chain_id"]
logo = selected_chain["logo"]

# =====================================================
# LOGO + TITLE
# =====================================================

st.markdown(
    f"""
    <div style="display:flex;align-items:center;gap:15px;margin-bottom:20px;">
        <img src="{logo}" width="70">
        <div>
            <h2 style="margin:0;">{chain_name}</h2>
            <p style="margin:0;">Chain ID: {chain_id}</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# DATA
# =====================================================

try:

    data = fetch_stats(chain_id)

    kpis = [
        ("Average Block Time", data.get("average_block_time")),
        ("Coin Price", data.get("coin_price")),
        ("Coin Price Change %", data.get("coin_price_change_percentage")),
        ("Gas Slow", data.get("gas_prices", {}).get("slow")),
        ("Gas Average", data.get("gas_prices", {}).get("average")),
        ("Gas Fast", data.get("gas_prices", {}).get("fast")),
        ("Gas Used Today", data.get("gas_used_today")),
        ("Market Cap", data.get("market_cap")),
        ("Network Utilization %", data.get("network_utilization_percentage")),
        ("Total Addresses", data.get("total_addresses")),
        ("Total Blocks", data.get("total_blocks")),
        ("Total Gas Used", data.get("total_gas_used")),
        ("Total Transactions", data.get("total_transactions")),
        ("Transactions Today", data.get("transactions_today")),
        ("TVL", data.get("tvl")),
        ("Gas Prices Update In", data.get("gas_prices_update_in"))
    ]

    st.subheader("📊 Network KPIs")

    cols = st.columns(4)

    for idx, (label, value) in enumerate(kpis):

        with cols[idx % 4]:
            st.metric(
                label=label,
                value=format_number(value)
            )

    st.divider()

    st.subheader("📄 Raw API Response")
    st.json(data)

except Exception as e:

    st.error(f"Failed to load data: {e}")
