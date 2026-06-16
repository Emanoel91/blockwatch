import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
# =====================================================
#   Sidebar Footer Slightly Left-Aligned  
# =====================================================

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
# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="TVL Analysis",
    layout="wide"
)

st.title("TVL Analysis")

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

[data-testid="metric-container"] {
    background: linear-gradient(145deg,#1c1c1c,#111111);
    border: 1px solid rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.25);
}

div[data-testid="stMetricValue"] {
    font-size: 32px !important;
    font-weight: bold !important;
}

div[data-testid="stMetricLabel"] {
    font-size: 15px !important;
    font-weight: bold !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HELPERS
# =====================================================

def format_tvl(value):

    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"

    elif value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"

    elif value >= 1_000:
        return f"${value/1_000:.2f}K"

    return f"${value:.0f}"


@st.cache_data(ttl=3600)
def load_data():

    url = "https://api.llama.fi/v2/chains"

    data = requests.get(url).json()

    df = pd.DataFrame(data)

    df["tvl"] = pd.to_numeric(df["tvl"], errors="coerce")

    return df


df = load_data()

# =====================================================
# KPI SECTION
# =====================================================

top_chain = df.loc[df["tvl"].idxmax()]

median_tvl = df["tvl"].median()

chains = sorted(df["name"].dropna().unique())

selected_chain = st.selectbox(
    "Select Blockchain",
    chains
)

selected_tvl = df.loc[
    df["name"] == selected_chain,
    "tvl"
].iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Highest TVL Chain",
        top_chain["name"],
        format_tvl(top_chain["tvl"])
    )

with col2:
    st.metric(
        "Median TVL",
        format_tvl(median_tvl)
    )

with col3:
    st.metric(
        f"{selected_chain} TVL",
        format_tvl(selected_tvl)
    )

st.divider()

# =====================================================
# TOP 10 TVL
# =====================================================

st.subheader("Top 10 Chains by TVL")

top10 = df.nlargest(10, "tvl").copy()

top10["Label"] = top10["tvl"].apply(format_tvl)

fig = px.bar(
    top10,
    x="name",
    y="tvl",
    text="Label"
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    height=500,
    xaxis_title="Blockchain",
    yaxis_title="TVL ($)",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# HORIZONTAL BARS
# =====================================================

def horizontal_chart(data, title):

    fig = px.bar(
        data,
        x="tvl",
        y="name",
        orientation="h",
        text=data["tvl"].apply(format_tvl)
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        title=title,
        height=500,
        yaxis_title="",
        xaxis_title="TVL ($)"
    )

    return fig


less_1b = (
    df[df["tvl"] < 1_000_000_000]
    .nlargest(10, "tvl")
)

less_500m = (
    df[df["tvl"] < 500_000_000]
    .nlargest(10, "tvl")
)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        horizontal_chart(
            less_1b,
            "Top 10 Chains Below $1B TVL"
        ),
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        horizontal_chart(
            less_500m,
            "Top 10 Chains Below $500M TVL"
        ),
        use_container_width=True
    )

# =====================================================
# SECOND ROW HORIZONTAL
# =====================================================

less_100m = (
    df[df["tvl"] < 100_000_000]
    .nlargest(10, "tvl")
)

less_50m = (
    df[df["tvl"] < 50_000_000]
    .nlargest(10, "tvl")
)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        horizontal_chart(
            less_100m,
            "Top 10 Chains Below $100M TVL"
        ),
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        horizontal_chart(
            less_50m,
            "Top 10 Chains Below $50M TVL"
        ),
        use_container_width=True
    )

# =====================================================
# TVL DISTRIBUTION
# =====================================================

bins = [
    0,
    1_000_000,
    10_000_000,
    50_000_000,
    100_000_000,
    500_000_000,
    1_000_000_000,
    np.inf
]

labels = [
    "<1M$",
    "1M$-10M$",
    "10M$-50M$",
    "50M$-100M$",
    "100M$-500M$",
    "500M$-1B$",
    ">1B$"
]

df["TVL Range"] = pd.cut(
    df["tvl"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

distribution = (
    df["TVL Range"]
    .value_counts()
    .reindex(labels)
    .reset_index()
)

distribution.columns = [
    "Range",
    "Count"
]

# =====================================================
# BAR + PIE
# =====================================================

col1, col2 = st.columns(2)

with col1:

    fig_bar = px.bar(
        distribution,
        x="Range",
        y="Count",
        text="Count",
        title="Blockchain Distribution by TVL"
    )

    fig_bar.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

with col2:

    pie_colors = [
        "#FFF8DC",
        "#FFE082",
        "#FFD54F",
        "#FFCA28",
        "#FFC107",
        "#FFB300",
        "#FF8F00"
    ]

    fig_pie = go.Figure(
        data=[
            go.Pie(
                labels=distribution["Range"],
                values=distribution["Count"],
                hole=0.45,
                textinfo="percent+value",
                marker=dict(
                    colors=pie_colors
                )
            )
        ]
    )

    fig_pie.update_layout(
        title="Blockchain Distribution by TVL"
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

# =====================================================
# TABLE
# =====================================================

st.subheader("Blockchain TVL Table")

table_df = (
    df.sort_values(
        "tvl",
        ascending=False
    )
    .reset_index(drop=True)
)

table_df.insert(
    0,
    "Rank",
    range(1, len(table_df) + 1)
)

table_df = table_df[
    [
        "Rank",
        "name",
        "tvl",
        "tokenSymbol",
        "chainId",
        "gecko_id",
        "cmcId"
    ]
]

table_df.columns = [
    "Rank",
    "Blockchain",
    "TVL",
    "Native Coin",
    "Chain ID",
    "Gecko ID",
    "CMC ID"
]

table_df["TVL"] = table_df["TVL"].apply(format_tvl)

st.dataframe(
    table_df,
    use_container_width=True,
    height=700
)
