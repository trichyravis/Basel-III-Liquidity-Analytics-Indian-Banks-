
import streamlit as st
import sys
import os
import yaml
import pandas as pd
import plotly.graph_objects as go

# --- 1. CRITICAL: PATH INJECTION ---
# This tells Streamlit Cloud exactly where to find your 'src' folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now we can safely import your modules
try:
    from src.risk_engine import calculate_ratios
    from src.data_ingestion import fetch_bank_data
    from src.utils import apply_basel_mapping
    from src.reporter import generate_pdf
except ImportError as e:
    st.error(f"Import Error: {e}. Please ensure the 'src' folder contains an __init__.py file.")
    st.stop()

# --- 2. CONFIGURATION & UI SETUP ---
st.set_page_config(page_title="Basel III Analytics", layout="wide")

# Load configuration (ensure config.yaml is in your GitHub root)
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    st.error("Missing config.yaml file in the root directory.")
    st.stop()

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header("🕹️ Stress Parameters")
bank_ticker = st.sidebar.selectbox("Select NSE Bank", ["HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS"])
r_stress = st.sidebar.slider("Deposit Run-off Multiplier", 1.0, 3.0, 1.0, help="Simulates faster deposit withdrawals")
h_stress = st.sidebar.slider("Asset Haircut Multiplier", 1.0, 2.0, 1.0, help="Simulates devaluation of HQLA assets")

st.title(f"🏦 Liquidity Risk Analysis: {bank_ticker}")

# --- 4. MAIN ENGINE EXECUTION ---
if st.button("Run Analytics Engine"):
    with st.spinner("Accessing Market Data..."):
        bs, hist = fetch_bank_data(bank_ticker)
        
        if bs is not None:
            # Transform raw financials into Basel Buckets
            buckets = apply_basel_mapping(bs.iloc[:, 0])
            
            # Calculate Ratios using the Risk Engine
            lcr, nsfr = calculate_ratios(buckets, config, r_stress, h_stress)
            
            # --- 5. GRAPHICAL OUTPUT ---
            tab1, tab2 = st.tabs(["🛡️ Compliance Gauges", "📈 Market Trends"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                # LCR Gauge
                fig_lcr = go.Figure(go.Indicator(
                    mode="gauge+number", value=lcr, title={'text': "LCR %"},
                    gauge={'axis': {'range': [0, 200]}, 'steps': [
                        {'range': [0, 100], 'color': "red"},
                        {'range': [100, 120], 'color': "orange"},
                        {'range': [120, 200], 'color': "green"}]}))
                col1.plotly_chart(fig_lcr, use_container_width=True)
                
                # NSFR Gauge
                fig_nsfr = go.Figure(go.Indicator(
                    mode="gauge+number", value=nsfr, title={'text': "NSFR %"},
                    gauge={'axis': {'range': [0, 200]}, 'steps': [
                        {'range': [0, 100], 'color': "red"},
                        {'range': [100, 200], 'color': "green"}]}))
                col2.plotly_chart(fig_nsfr, use_container_width=True)
            
            with tab2:
                st.subheader("Historical Stock Price (Stress Context)")
                st.line_chart(hist['Close'])
            
            # --- 6. PDF REPORTING ---
            st.write("---")
            pdf_data = generate_pdf(bank_ticker, lcr, nsfr, "Custom Stress")
            st.download_button(
                label="📥 Download Formal Risk Report",
                data=pdf_data,
                file_name=f"Liquidity_Report_{bank_ticker}.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Could not fetch data. Please check ticker or try again later.")
