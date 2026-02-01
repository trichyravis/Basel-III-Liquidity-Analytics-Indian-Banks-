
import streamlit as st
import sys
import os
import yaml
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# --- 1. CRITICAL: PATH INJECTION ---
# Ensures Streamlit Cloud sees the 'src' folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.risk_engine import calculate_ratios
    from src.data_ingestion import fetch_bank_data
    from src.utils import apply_basel_mapping
    from src.reporter import generate_pdf
except ImportError as e:
    st.error(f"Import Error: {e}. Ensure 'src' folder has an __init__.py file.")
    st.stop()

# --- 2. CONFIGURATION & UI SETUP ---
st.set_page_config(page_title="Basel III Analytics - Prof. V. Ravichandran", layout="wide")

@st.cache_data
def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header("🕹️ Stress Test Controls")
bank_ticker = st.sidebar.selectbox("Select NSE Bank", ["HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS"])
st.sidebar.markdown("---")

st.sidebar.subheader("LCR Stress")
r_stress = st.sidebar.slider("Deposit Run-off Multiplier", 1.0, 3.0, 1.0, help="Simulates faster withdrawals")
h_stress = st.sidebar.slider("HQLA Haircut Multiplier", 1.0, 2.0, 1.0, help="Simulates asset devaluation")

# --- 4. MAIN DASHBOARD ---
st.title(f"🏦 Basel III Liquidity Intelligence: {bank_ticker}")
st.markdown(f"*Powered by Prof. V. Ravichandran - The Mountain Path*")

if st.button("🚀 Run Analytics Engine"):
    with st.spinner(f"Fetching disclosures for {bank_ticker}..."):
        bs, hist = fetch_bank_data(bank_ticker)
        
        if bs is not None and not bs.empty:
            # Step 1: Map raw data to Basel Buckets
            buckets = apply_basel_mapping(bs.iloc[:, 0])
            
            # Step 2: Calculate Ratios
            lcr, nsfr = calculate_ratios(buckets, config, r_stress, h_stress)
            
            # --- 5. TABBED OUTPUT ---
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🛡️ Compliance Gauges", 
                "📈 Market Trends", 
                "🧪 Stress Sensitivity",
                "🏛️ NSFR Ratio",
                "📥 Raw Data Download"
            ])

            # TAB 1: GAUGES
            with tab1:
                col1, col2 = st.columns(2)
                fig_lcr = go.Figure(go.Indicator(
                    mode="gauge+number", value=lcr, title={'text': "LCR %"},
                    gauge={'axis': {'range': [0, 200]}, 'steps': [
                        {'range': [0, 100], 'color': "red"},
                        {'range': [100, 120], 'color': "orange"},
                        {'range': [120, 200], 'color': "green"}]}))
                col1.plotly_chart(fig_lcr, use_container_width=True)

                fig_nsfr = go.Figure(go.Indicator(
                    mode="gauge+number", value=nsfr, title={'text': "NSFR %"},
                    gauge={'axis': {'range': [0, 200]}, 'steps': [
                        {'range': [0, 100], 'color': "red"},
                        {'range': [100, 200], 'color': "green"}]}))
                col2.plotly_chart(fig_nsfr, use_container_width=True)

            # TAB 2: MARKET DATA
            with tab2:
                st.subheader("Historical Stock Price Context")
                st.line_chart(hist['Close'])

            # TAB 3: SENSITIVITY MATRIX
            with tab3:
                st.subheader("LCR Sensitivity Heatmap")
                runoffs = np.linspace(1.0, 3.0, 5)
                haircuts = np.linspace(1.0, 2.0, 5)
                z_data = [[calculate_ratios(buckets, config, r, h)[0] for h in haircuts] for r in runoffs]
                
                fig_heat = px.imshow(z_data, 
                                     x=[f"H:{h}x" for h in haircuts], 
                                     y=[f"R:{r}x" for r in runoffs],
                                     color_continuous_scale='RdYlGn',
                                     labels=dict(x="Haircut Stress", y="Run-off Stress", color="LCR %"))
                st.plotly_chart(fig_heat, use_container_width=True)

            # TAB 4: NSFR DETAILS
            with tab4:
                st.subheader("Net Stable Funding Ratio Analysis")
                st.info(f"The current NSFR of {nsfr}% represents the structural funding balance over a 1-year horizon.")
                # Component breakdown logic could go here

            # TAB 5: DATA DOWNLOAD (As requested)
            with tab5:
                st.subheader("Traceability: Raw Data Source")
                st.write("This table shows the raw quarterly financials fetched from Yahoo Finance.")
                st.dataframe(bs)
                
                csv = bs.to_csv().encode('utf-8')
                st.download_button(
                    label="📥 Download Raw Financials (CSV)",
                    data=csv,
                    file_name=f"{bank_ticker}_financials.csv",
                    mime='text/csv'
                )

            # --- 6. FORMAL REPORTING ---
            st.divider()
            pdf_data = generate_pdf(bank_ticker, lcr, nsfr, "Dynamic Stress Test")
            st.download_button("📜 Download Formal PDF Risk Report", pdf_data, f"{bank_ticker}_Report.pdf", "application/pdf")
            
        else:
            st.error("Failed to fetch data. Yahoo Finance might be throttled or the ticker is incorrect.")
