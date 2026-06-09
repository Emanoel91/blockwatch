import streamlit as st
import requests
import pandas as pd

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

API_KEY = st.secrets["BLOCKSCOUT_API_KEY"]

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
# NETWORKS
# =====================================================
# کل دیکشنری Mainnet و Testnet خودت را اینجا قرار بده

NETWORKS = {
    "Mainnet": {
        "Ethereum": {
            "chain_id": 1,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/ethereum.svg"
        }
    },

    "Testnet": {
        "Arc Testnet": {
            "chain_id": 5042002,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/Arc.svg"
        }
    }
}

# =====================================================
# KPI HELP
# =====================================================

KPI_HELP = {

    "Average Block Time":
        "Average time required to produce a block.",

    "Coin Price":
        "Current market price of the native token.",

    "Coin Price Change %":
        "24-hour price change percentage.",

    "Gas Slow":
        "Recommended gas price for low-priority transactions.",

    "Gas Average":
        "Recommended gas price for normal transactions.",

    "Gas Fast":
        "Recommended gas price for urgent transactions.",

    "Gas Used Today":
        "Total gas consumed today.",

    "Market Cap":
        "Current network market capitalization.",

    "Network Utilization %":
        "Percentage of network capacity currently utilized.",

    "Total Addresses":
        "Total addresses discovered on chain.",

    "Total Blocks":
        "Total blocks produced.",

    "Total Gas Used":
        "Lifetime gas consumed on the network.",

    "Total Transactions":
        "Lifetime transaction count.",

    "Transactions Today":
        "Transactions processed today.",

    "TVL":
        "Total Value Locked.",

    "Gas Prices Update In":
        "Seconds until gas prices refresh."
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

        if value < 1 and value != 0:
            return f"{value:.4f}"

        if value.is_integer():
            return f"{int(value):,}"

        return f"{value:,.4f}"

    except:
        return str(value)

# =====================================================
# FETCH DATA
# =====================================================

@st.cache_data(ttl=7200)
def fetch_stats(chain_id):

    url = (
        f"https://api.blockscout.com/"
        f"{chain_id}/api/v2/stats"
        f"?apikey={API_KEY}"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.json()

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
                    value=format_number(value),
                    help=KPI_HELP.get(label)
                )

# =====================================================
# HEADER
# =====================================================

st.title("🌐 Blockscout Multi-Chain Dashboard")

st.info(
    "Select a blockchain network to view live Blockscout statistics."
)

# =====================================================
# FILTERS
# =====================================================

col1, col2 = st.columns(2)

with col1:

    network_type = st.selectbox(
        "Network Type",
        list(NETWORKS.keys())
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
# NETWORK HEADER
# =====================================================

st.markdown(
    f"""
    <div style="display:flex;align-items:center;gap:20px;margin-bottom:25px;">
        <img src="{logo}" width="10">
        <div>
            <h2 style="margin:0;">{chain_name}</h2>
            <p style="margin:0;font-size:18px;">
                Chain ID: {chain_id}
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# LOAD DATA
# =====================================================

try:

    data = fetch_stats(chain_id)

    # -------------------------------------------------
    # NETWORK
    # -------------------------------------------------

    st.subheader("⛓ Network")

    show_metrics([
        ("Average Block Time",
         data.get("average_block_time")),

        ("Network Utilization %",
         data.get("network_utilization_percentage")),

        ("Total Blocks",
         data.get("total_blocks")),

        ("Gas Prices Update In",
         data.get("gas_prices_update_in"))
    ])

    st.divider()

    # -------------------------------------------------
    # ACTIVITY
    # -------------------------------------------------

    st.subheader("📈 Activity")

    show_metrics([
        ("Total Transactions",
         data.get("total_transactions")),

        ("Transactions Today",
         data.get("transactions_today")),

        ("Total Addresses",
         data.get("total_addresses")),

        ("Total Gas Used",
         data.get("total_gas_used"))
    ])

    st.divider()

    # -------------------------------------------------
    # GAS
    # -------------------------------------------------

    st.subheader("⛽ Gas")

    gas = data.get("gas_prices", {})

    show_metrics([
        ("Gas Slow",
         gas.get("slow")),

        ("Gas Average",
         gas.get("average")),

        ("Gas Fast",
         gas.get("fast")),

        ("Gas Used Today",
         data.get("gas_used_today"))
    ])

    st.divider()

    # -------------------------------------------------
    # MARKET
    # -------------------------------------------------

    st.subheader("💰 Market")

    show_metrics([
        ("Coin Price",
         data.get("coin_price")),

        ("Coin Price Change %",
         data.get("coin_price_change_percentage")),

        ("Market Cap",
         data.get("market_cap")),

        ("TVL",
         data.get("tvl"))
    ])

    st.divider()

    # -------------------------------------------------
    # LAST UPDATE
    # -------------------------------------------------

    st.caption(
        f"Last gas update: "
        f"{data.get('gas_price_updated_at')}"
    )

    # -------------------------------------------------
    # RAW DATA
    # -------------------------------------------------

    with st.expander("🔍 View Raw API Response"):

        st.json(data)

except Exception as e:

    st.error(f"Failed to load data: {e}")
