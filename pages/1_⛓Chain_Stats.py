import streamlit as st
import requests
import pandas as pd
# ====================================================
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

NETWORKS = {
    "Mainnet": {
        "Arbitrum Nova": {
            "chain_id": 42170,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/arbitrum-nova.svg"
        },
        "Arbitrum One Nitro": {
            "chain_id": 42161,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/arbitrum-one-nitro.svg"
        },
        "Astar": {
            "chain_id": 592,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/astar.svg"
        },
        "Awaji": {
            "chain_id": 6497,
            "logo": "https://raw.githubusercontent.com/blockscout/frontend-configs/main/configs/network-icons/awaji-light.svg"
        },
        "Base": {
            "chain_id": 8453,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/base.svg"
        },
        "BXN": {
            "chain_id": 488,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/blackfort.svg"
        },
        "Celo": {
            "chain_id": 42220,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/celo.svg"
        },
        "Creditcoin": {
            "chain_id": 102030,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/creditcoin.svg"
        },
        "Cross Mainnet": {
            "chain_id": 612055,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/cross.svg"
        },
        "Eden": {
            "chain_id": 714,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/eden_testnet.svg"
        },
        "EDU Chain": {
            "chain_id": 41923,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/edu-chain.svg"
        },
        "Ethereum": {
            "chain_id": 1,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/ethereum.svg"
        },
        "Ethereum Classic": {
            "chain_id": 61,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/ethereum-classic.svg"
        },
        "Etherlink": {
            "chain_id": 42793,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/etherlink.svg"
        },
        "Filecoin Virtual Machine": {
            "chain_id": 314,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/filecoin.svg"
        },
        "Flow Mainnet": {
            "chain_id": 747,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/flow.svg"
        },
        "Fuse": {
            "chain_id": 122,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/fuse.svg"
        },
        "Gensyn": {
            "chain_id": 685689,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/gensyn_testnet.png"
        },
        "Gnosis": {
            "chain_id": 100,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/gnosis.svg"
        },
        "HashKey": {
            "chain_id": 177,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/hashkey.svg"
        },
        "ICB Network": {
            "chain_id": 73115,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/icb.svg"
        },
        "Immutable zkEVM": {
            "chain_id": 13371,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/Immutable_zkEVM.svg"
        },
        "Ink": {
            "chain_id": 57073,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/ink.svg"
        },
        "IOTA EVM": {
            "chain_id": 8822,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/iota.svg"
        },
        "KiteAI Mainnet": {
            "chain_id": 2366,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/kite.svg"
        },
        "LightLink Phoenix Mainnet": {
            "chain_id": 1890,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/lightlink.svg"
        },
        "Lisk": {
            "chain_id": 1135,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/lisk.svg"
        },
        "Matchain": {
            "chain_id": 698,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/matchain.svg"
        },
        "MegaETH": {
            "chain_id": 4326,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/megaeth.svg"
        },
        "Moca Chain": {
            "chain_id": 2288,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/moca.svg"
        },
        "Mode": {
            "chain_id": 34443,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/mode.svg"
        },
        "Neon": {
            "chain_id": 245022934,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/neon.svg"
        },
        "Nexus Mainnet": {
            "chain_id": 3946,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/nexus.png"
        },
        "Numine": {
            "chain_id": 8021,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/numine.png"
        },
        "OP Mainnet": {
            "chain_id": 10,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/op-mainnet.svg"
        },
        "Playnance Playblock": {
            "chain_id": 1829,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/playblock.svg"
        },
        "Polygon PoS": {
            "chain_id": 137,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/polygon-pos.svg"
        },
        "Reya": {
            "chain_id": 1729,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/reya.svg"
        },
        "Rootstock": {
            "chain_id": 30,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/rootstock.svg"
        },
        "Scroll": {
            "chain_id": 534352,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/scroll.svg"
        },
        "Shape": {
            "chain_id": 360,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/shape.svg"
        },
        "Shibarium": {
            "chain_id": 109,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/shibarium.svg"
        },
        "Shimmer EVM Mainnet": {
            "chain_id": 148,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/shimmer.svg"
        },
        "Soneium": {
            "chain_id": 1868,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/soneium.svg"
        },
        "Story": {
            "chain_id": 1514,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/story.svg"
        },
        "TAC Mainnet": {
            "chain_id": 239,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/tac.jpg"
        },
        "Unichain": {
            "chain_id": 130,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/Unichain.svg"
        },
        "World Chain": {
            "chain_id": 480,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/world-chain.svg"
        },
        "World Mobile": {
            "chain_id": 869,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/world_mobile.svg"
        },
        "ZetaChain": {
            "chain_id": 7000,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/zeta.svg"
        },
        "Zilliqa 2 Mainnet": {
            "chain_id": 32769,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/zilliqa.svg"
        },
        "ZKsync Era": {
            "chain_id": 324,
            "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/zksync-era.svg"
        }
    },

    "Testnet": {
        "Alchemy Sepolia": {"chain_id": 69420, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/alchemy.svg"},
        "Arbitrum Sepolia": {"chain_id": 421614, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/arbitrum.svg"},
        "Arc Testnet": {"chain_id": 5042002, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/Arc.svg"},
        "Astar Shibuya": {"chain_id": 81, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/astar.svg"},
        "Base Sepolia": {"chain_id": 84532, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/base-sepolia.svg"},
        "BXN Testnet": {"chain_id": 4888, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/blackfort.svg"},
        "Celo Sepolia": {"chain_id": 11142220, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/celo.svg"},
        "Creditcoin Devnet": {"chain_id": 102032, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/creditcoin.svg"},
        "Creditcoin Testnet": {"chain_id": 102031, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/creditcoin.svg"},
        "Cross Testnet": {"chain_id": 612044, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/cross.svg"},
        "Eden Testnet": {"chain_id": 3735928814, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/eden_testnet.svg"},
        "EDU Chain Testnet": {"chain_id": 656476, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/edu-chain.svg"},
        "Ethereum Classic Mordor": {"chain_id": 63, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/ethereum-classic.svg"},
        "Ethereum Sepolia": {"chain_id": 11155111, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/ethereum.svg"},
        "Etherlink Shadownet": {"chain_id": 127823, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/etherlink.svg"},
        "Filecoin Calibration Testnet": {"chain_id": 314159, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/filecoin.svg"},
        "Flow Testnet": {"chain_id": 545, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/flow.svg"},
        "Fuse Sparknet": {"chain_id": 123, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/fuse.svg"},
        "Gensyn Testnet": {"chain_id": 685685, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/gensyn_testnet.png"},
        "Gnosis Chiado Testnet": {"chain_id": 10200, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/gnosis.svg"},
        "Hoodi": {"chain_id": 560048, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/hoodi.png"},
        "ICB Network Testnet": {"chain_id": 73114, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/icb.svg"},
        "Immutable zkEVM Testnet": {"chain_id": 13473, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/Immutable_zkEVM.svg"},
        "Ink Sepolia": {"chain_id": 763373, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/ink.svg"},
        "IOTA EVM Testnet": {"chain_id": 1076, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/iota.svg"},
        "KiteAI Testnet": {"chain_id": 2368, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/kite.svg"},
        "LightLink Pegasus Testnet": {"chain_id": 1891, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/lightlink.svg"},
        "Lisk Sepolia Testnet": {"chain_id": 4202, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/lisk.svg"},
        "MegaETH Testnet v2": {"chain_id": 6343, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/megaeth.svg"},
        "Moca Chain Testnet": {"chain_id": 222888, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/moca.svg"},
        "Neon Devnet": {"chain_id": 245022926, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/neon.svg"},
        "Nexus Staging Testnet": {"chain_id": 3941, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/nexus.png"},
        "Nexus Testnet": {"chain_id": 3945, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/nexus.png"},
        "OP Sepolia": {"chain_id": 11155420, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/op-mainnet.svg"},
        "Reya Cronos": {"chain_id": 89346162, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/reya.svg"},
        "Rootstock Testnet": {"chain_id": 31, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/rootstock.svg"},
        "Scroll Testnet": {"chain_id": 534351, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/scroll.svg"},
        "Shape Testnet": {"chain_id": 11011, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/shape.svg"},
        "Shimmer EVM Testnet": {"chain_id": 1073, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/shimmer.svg"},
        "Soneium Minato Testnet": {"chain_id": 1946, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/soneium.svg"},
        "Story Aeneid": {"chain_id": 1315, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/story.svg"},
        "TAC SPB": {"chain_id": 2391, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/tac.jpg"},
        "Unichain Sepolia Testnet": {"chain_id": 1301, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/Unichain.svg"},
        "World Chain Testnet": {"chain_id": 4801, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/world-chain.svg"},
        "World Mobile Testnet": {"chain_id": 323432, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/world_mobile.svg"},
        "Zenchain Testnet": {"chain_id": 8408, "logo": "https://cdn.prod.website-files.com/644a5b7efad46e3cd70deafb/672e2004ecbf024c711f68a8_ZenChain.png"},
        "ZetaChain Testnet": {"chain_id": 7001, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/zeta.svg"},
        "Zilliqa 2 Testnet": {"chain_id": 33101, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/zilliqa.svg"},
        "ZKsync Era Sepolia Testnet": {"chain_id": 300, "logo": "https://blockscout-icons.s3.us-east-1.amazonaws.com/zksync-era.svg"}
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
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:25px;">
        <img src="{logo}" width="50">
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
# ==================================================
@st.cache_data(ttl=7200)
def fetch_transactions_chart(chain_id):

    url = (
        f"https://api.blockscout.com/"
        f"{chain_id}/api/v2/stats/charts/transactions"
        f"?apikey={API_KEY}"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.json()
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

        # =====================================================
    # TRANSACTIONS ANALYTICS
    # =====================================================

    st.divider()

    st.subheader("📊 Transaction Analytics (Last 30 Days)")

    tx_data = fetch_transactions_chart(chain_id)

    chart_df = pd.DataFrame(
        tx_data["chart_data"]
    )

    chart_df["date"] = pd.to_datetime(
        chart_df["date"]
    )

    chart_df = chart_df.sort_values(
        "date"
    )

    chart_df["transactions_count"] = (
        chart_df["transactions_count"]
        .astype(float)
    )

    # -----------------------------------------------------
    # BASIC METRICS
    # -----------------------------------------------------

    latest_tx = chart_df.iloc[-1]["transactions_count"]

    previous_tx = chart_df.iloc[-2]["transactions_count"]

    tx_7d = (
        chart_df.tail(7)["transactions_count"]
        .sum()
    )

    tx_30d = (
        chart_df["transactions_count"]
        .sum()
    )

    max_tx = (
        chart_df["transactions_count"]
        .max()
    )

    min_tx = (
        chart_df["transactions_count"]
        .min()
    )

    avg_tx = (
        chart_df["transactions_count"]
        .mean()
    )

    # -----------------------------------------------------
    # KPI CALCULATIONS
    # -----------------------------------------------------

    daily_change_pct = (
        (latest_tx - previous_tx)
        / previous_tx
        * 100
    )

    recent_7d_avg = (
        chart_df.tail(7)["transactions_count"]
        .mean()
    )

    previous_7d_avg = (
        chart_df.iloc[-14:-7]["transactions_count"]
        .mean()
    )

    weekly_change_pct = (
        (recent_7d_avg - previous_7d_avg)
        / previous_7d_avg
        * 100
    )

    pct_from_ath = (
        (latest_tx - max_tx)
        / max_tx
        * 100
    )

    # -----------------------------------------------------
    # KPI ROW 1
    # -----------------------------------------------------

    show_metrics([
        (
            "Transactions Last 24H",
            latest_tx
        ),
        (
            "Transactions Last 7D",
            tx_7d
        ),
        (
            "Transactions Last 30D",
            tx_30d
        )
    ], cols=3)

    # -----------------------------------------------------
    # KPI ROW 2
    # -----------------------------------------------------

    show_metrics([
        (
            "1D Change %",
            round(
                daily_change_pct,
                2
            )
        ),
        (
            "7D Change %",
            round(
                weekly_change_pct,
                2
            )
        ),
        (
            "% From ATH",
            round(
                pct_from_ath,
                2
            )
        )
    ], cols=3)

    # -----------------------------------------------------
    # KPI ROW 3
    # -----------------------------------------------------

    show_metrics([
        (
            "30D Max Daily Tx",
            max_tx
        ),
        (
            "30D Min Daily Tx",
            min_tx
        ),
        (
            "30D Avg Daily Tx",
            avg_tx
        )
    ], cols=3)

    # =====================================================
    # CHART 1
    # DAILY TX + CUMULATIVE TX
    # =====================================================

    chart_df["cumulative_tx"] = (
        chart_df["transactions_count"]
        .cumsum()
    )

    fig = make_subplots(
        specs=[
            [{"secondary_y": True}]
        ]
    )

    fig.add_trace(
        go.Bar(
            x=chart_df["date"],
            y=chart_df["transactions_count"],
            name="Daily Transactions"
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df["date"],
            y=chart_df["cumulative_tx"],
            mode="lines+markers",
            name="Cumulative Transactions"
        ),
        secondary_y=True
    )

    fig.update_layout(
        height=550,
        title="Daily Transactions & Cumulative Transactions"
    )

    fig.update_yaxes(
        title_text="Daily Transactions",
        secondary_y=False
    )

    fig.update_yaxes(
        title_text="Cumulative Transactions",
        secondary_y=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # CHART PREPARATION
    # =====================================================

    chart_df["daily_change_pct"] = (
        chart_df["transactions_count"]
        .pct_change()
        * 100
    )

    chart_df["daily_change_pct"] = (
        chart_df["daily_change_pct"]
        .fillna(0)
    )

    colors = np.where(
        chart_df["daily_change_pct"] >= 0,
        "green",
        "red"
    )

    chart_df["pct_from_ath"] = (
        (
            chart_df["transactions_count"]
            - max_tx
        )
        / max_tx
        * 100
    )

    chart_df["pct_from_atl"] = (
        (
            chart_df["transactions_count"]
            - min_tx
        )
        / min_tx
        * 100
    )

    # =====================================================
    # CHART ROW
    # =====================================================

    col_left, col_right = st.columns(2)

    # -----------------------------------------------------
    # DAILY CHANGE %
    # -----------------------------------------------------

    with col_left:

        fig_change = go.Figure()

        fig_change.add_trace(
            go.Bar(
                x=chart_df["date"],
                y=chart_df["daily_change_pct"],
                marker_color=colors,
                name="% Change"
            )
        )

        fig_change.update_layout(
            height=500,
            title="Daily Transaction Change %"
        )

        st.plotly_chart(
            fig_change,
            use_container_width=True
        )

    # -----------------------------------------------------
    # ATH / ATL DISTANCE
    # -----------------------------------------------------

    with col_right:

        fig_levels = go.Figure()

        fig_levels.add_trace(
            go.Scatter(
                x=chart_df["date"],
                y=chart_df["pct_from_ath"],
                mode="lines+markers",
                line=dict(
                    color="red",
                    width=3
                ),
                name="% From ATH"
            )
        )

        fig_levels.add_trace(
            go.Scatter(
                x=chart_df["date"],
                y=chart_df["pct_from_atl"],
                mode="lines+markers",
                line=dict(
                    color="green",
                    width=3
                ),
                name="% From ATL"
            )
        )

        fig_levels.update_layout(
            height=500,
            title="Distance From ATH / ATL"
        )

        st.plotly_chart(
            fig_levels,
            use_container_width=True
        )
