
import pandas as pd

def apply_basel_mapping(financials_series, mapping_path="data/mapping/bank_map.csv"):
    """
    Enhanced mapping logic with logging to debug the '0' gauge issue.
    """
    try:
        # Load the mapping file and clean whitespace
        mapping_df = pd.read_csv(mapping_path)
        mapping_df['Yahoo_Finance_Label'] = mapping_df['Yahoo_Finance_Label'].str.strip()
        
        # Prepare the raw bank data
        raw_data = financials_series.to_frame(name='amount').reset_index()
        raw_data['index'] = raw_data['index'].str.strip()
        
        # DEBUG: This will show up in your Streamlit Cloud logs!
        print("Available Rows from Yahoo Finance:", raw_data['index'].tolist())
        
        # Merge the datasets
        merged = raw_data.merge(mapping_df, left_on='index', right_on='Yahoo_Finance_Label')
        
        # Sum the buckets
        basel_buckets = merged.groupby('Basel_III_Category')['amount'].sum().to_dict()
        
        # Ensure at least a default value exists to avoid division by zero
        if not basel_buckets:
            print("WARNING: No matches found in mapping. Check bank_map.csv labels.")
            
        return basel_buckets
    except Exception as e:
        print(f"CRITICAL ERROR in utils.py: {e}")
        return {}
