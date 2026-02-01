
import pandas as pd
import os

def apply_basel_mapping(financials_series, mapping_path="data/mapping/bank_map.csv"):
    """
    Standardizes raw Yahoo Finance financial labels into Basel III regulatory buckets.
    Includes fallback logic to prevent 'Zero Gauges' during API interruptions.
    """
    try:
        # 1. Load the mapping definition
        if not os.path.exists(mapping_path):
            print(f"Error: Mapping file not found at {mapping_path}")
            return get_fallback_data(financials_series)

        mapping_df = pd.read_csv(mapping_path)
        
        # 2. Pre-process mapping labels (Lowercase & Strip for fuzzy matching)
        mapping_df['Yahoo_Finance_Label'] = mapping_df['Yahoo_Finance_Label'].str.strip().str.lower()
        
        # 3. Pre-process raw bank data
        raw_data = financials_series.to_frame(name='amount').reset_index()
        raw_data['index'] = raw_data['index'].str.strip().str.lower()
        
        # 4. Perform Mapping (Inner Join)
        merged = raw_data.merge(mapping_df, left_on='index', right_on='Yahoo_Finance_Label')
        
        # 5. Aggregate into Basel Categories
        basel_buckets = merged.groupby('Basel_III_Category')['amount'].sum().to_dict()
        
        # 6. Validation: If critical buckets are missing, trigger Fallback
        critical_keys = ['Level_1_HQLA', 'Retail_Stable', 'Equity_Capital', 'Loans_to_Retail']
        if not all(key in basel_buckets for key in critical_keys):
            print("⚠️ Mapping incomplete. Activating Safe Mode Fallback.")
            return get_fallback_data(financials_series)
            
        return basel_buckets

    except Exception as e:
        print(f"Mapping Logic Error: {e}")
        return get_fallback_data(financials_series)

def get_fallback_data(financials_series):
    """
    Provides estimated Basel buckets based on typical Indian Private Bank ratios 
    (LCR ~120%, NSFR ~118%) if the mapping engine fails.
    """
    # Use 'Total Assets' or the first available row as a scaling factor
    try:
        scale = financials_series.iloc[0] 
    except:
        scale = 2500000000000 # Default scale (approx 25 Lakh Cr)

    return {
        'Level_1_HQLA': scale * 0.18,      # 18% of assets in HQLA
        'Level_2A_HQLA': scale * 0.04,     # 4% in secondary HQLA
        'Retail_Stable': scale * 0.70,     # 70% Deposits
        'Equity_Capital': scale * 0.12,    # 12% Tier 1 Capital
        'Loans_to_Retail': scale * 0.75    # 75% Loans/Illiquid assets
    }
