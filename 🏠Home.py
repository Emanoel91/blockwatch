import streamlit as st

# --- Page Config: Tab Title & Icon ---
st.set_page_config(
    page_title="Blockwatch",
    page_icon="https://raw.githubusercontent.com/Emanoel91/blockwatch/main/logo_blockwatch_no_text.png",
    layout="wide"
)

# --- Title with Logo ---
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 15px;">
        <img src="https://raw.githubusercontent.com/Emanoel91/blockwatch/main/logo_blockwatch_no_text.png" alt="axelar" style="width:60px; height:60px;">
        <h1 style="margin: 0;">Blockwatch</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Builder Info ------------------------------------------------------------------------

st.markdown(
    """
    <div style="margin-top: 20px; margin-bottom: 20px; font-size: 16px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://pbs.twimg.com/profile_images/2060406047391559681/sA9zPNKM_400x400.jpg" alt="Eman Raz" style="width:25px; height:25px; border-radius: 50%;"> 
            <span>Built by: <a href="https://x.com/0xeman_raz" target="_blank">Eman Raz</a></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Info Box ---
st.markdown(
    """
    <div style="background-color: #d5fe8b; padding: 15px; border-radius: 10px; border: 1px solid #d5fe8b;">
        The Blockwatch Dashboard provides a unified view of key performance, activity, and 
        market metrics across multiple blockchains. 
        The dashboard enables users to monitor critical network statistics. 
    </div>
    """,
    unsafe_allow_html=True
)
# ========================================================
# Donation
# ========================================================

def render_donate_box():
    donate_text = """
💖 **Support This Project**

If you find this dashboard useful, you can support its continued development:

⛓ **EVM Wallet**
`0xD61338FD377816538a1E17eeA18D49512a37719a`

🌐 **Solana Wallet**
`ApHkGf2PiQSV9CRzbcmMkFi15q2bfhnSKnxUFatbygR4`

🚀 Your support helps improve data coverage, add new chains, and enhance analytics features.
"""
    st.info(donate_text)

render_donate_box()

# --- Sidebar Footer Slightly Left-Aligned ---
st.sidebar.markdown(
    """
    <style>
    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        width: 250px;
        font-size: 13px;
        color: gray;
        margin-left: 5px; # -- MOVE LEFT
        text-align: left;  
    }
    .sidebar-footer img {
        width: 16px;
        height: 16px;
        vertical-align: middle;
        border-radius: 50%;
        margin-right: 5px;
    }
    .sidebar-footer a {
        color: gray;
        text-decoration: none;
    }
    </style>

    <div class="sidebar-footer">
        <div style="margin-top: 5px;">
            <a href="https://x.com/0xeman_raz" target="_blank">
                <img src="https://pbs.twimg.com/profile_images/2060406047391559681/sA9zPNKM_400x400.jpg" alt="Eman Raz">
                Built by Eman Raz
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
