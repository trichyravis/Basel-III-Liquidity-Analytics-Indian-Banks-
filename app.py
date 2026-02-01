
import sys
import os

# This forces the app to look in its own root directory for the 'src' folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now perform your imports
from src.risk_engine import calculate_ratios
from src.data_ingestion import fetch_bank_data
# ... rest of your imports

import streamlit as st
import yaml
import pandas as pd
import plotly.graph_objects as go
from src.data_ingestion import fetch_bank_data
from src.risk_engine import calculate_ratios

st.set_page_config(page_title="Basel III Analytics", layout="wide")

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Sidebar
st.sidebar.header("Stress Parameters")
bank_ticker = st.sidebar.selectbox("NSE Bank", ["HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS"])
r_stress = st.sidebar.slider("Run-off Stress Multiplier", 1.0, 3.0, 1.0)
h_stress = st.sidebar.slider("Haircut Stress Multiplier", 1.0, 2.0, 1.0)

st.title(f"Liquidity Risk Analysis: {bank_ticker}")

if st.button("Run Engine"):
    bs, hist = fetch_bank_data(bank_ticker)
    # Simplified mapping for demo
    mock_buckets = {
        'Level_1_HQLA': bs.iloc[0,0] * 0.2, 
        'Level_2A_HQLA': bs.iloc[0,0] * 0.1,
        'Retail_Stable': bs.iloc[0,0] * 0.6,
        'Equity_Capital': bs.iloc[0,0] * 0.1,
        'Loans_to_Retail': bs.iloc[0,0] * 0.7
    }
    
    lcr, nsfr = calculate_ratios(mock_buckets, config, r_stress, h_stress)
    
    t1, t2 = st.tabs(["Compliance Gauges", "Market Data"])
    
    with t1:
        col1, col2 = st.columns(2)
        fig_lcr = go.Figure(go.Indicator(mode="gauge+number", value=lcr, title={'text': "LCR %"}, gauge={'axis': {'range': [0, 200]}, 'steps': [{'range': [0, 100], 'color': "red"}, {'range': [100, 200], 'color': "green"}]}))
        col1.plotly_chart(fig_lcr)
        
        fig_nsfr = go.Figure(go.Indicator(mode="gauge+number", value=nsfr, title={'text': "NSFR %"}, gauge={'axis': {'range': [0, 200]}, 'steps': [{'range': [0, 100], 'color': "red"}, {'range': [100, 200], 'color': "green"}]}))
        col2.plotly_chart(fig_nsfr)

    with t2:
        st.line_chart(hist['Close'])
