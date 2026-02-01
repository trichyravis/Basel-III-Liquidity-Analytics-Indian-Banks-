import yfinance as yf
import pandas as pd

def fetch_bank_data(ticker):
    """Fetches quarterly financials and historical market prices."""
    try:
        bank = yf.Ticker(ticker)
        # Get the most recent quarterly balance sheet
        bs = bank.quarterly_balance_sheet
        # Get 1 year of daily market data
        hist = bank.history(period="1y")
        
        if bs.empty or hist.empty:
            return None, None
            
        return bs, hist
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None, None
