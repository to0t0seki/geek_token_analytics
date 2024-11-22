import streamlit as st
from src.visualization.components.layout.sidebar import show_sidebar
from src.data_access.database import get_all_balances, get_airdrop_recipient_balances, get_exchange_balances, db_file


st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

show_sidebar()


st.title("個別アドレスの残高")

# データソースの選択
data_sources = {
    "All Addresses": lambda: get_all_balances(db_file),
    "Airdrop Claimed Addresses": lambda: get_airdrop_recipient_balances(db_file),
    "Exchange Addresses": lambda: get_exchange_balances(db_file),
}

selected_source = st.selectbox("Select data source:", list(data_sources.keys()))

