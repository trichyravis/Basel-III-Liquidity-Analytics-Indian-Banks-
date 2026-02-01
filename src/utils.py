
import pandas as pd

def apply_basel_mapping(financials_series, mapping_path="data/mapping/bank_map.csv"):
    """
    Maps raw Yahoo Finance labels to Basel III categories.
    Cleans strings to ensure matches even if there are trailing spaces.
    """
    try:
        # Load the mapping file
        mapping_df = pd.read_csv(mapping_path)
        
        # Clean the mapping labels
        mapping_df['Yahoo_Finance_Label'] = mapping_df['Yahoo_Finance_Label'].str.strip()
        
        # Convert financials to a clean DataFrame
        raw_data = financials_series.to_frame(name='amount').reset_index()
        raw_data['index'] = raw_data['index'].str.strip()
        
        # Merge raw data with the mapping file (inner join)
        merged = raw_data.merge(mapping_df, left_on='index', right_on='Yahoo_Finance_Label')
        
        # Group by the Basel Category and sum the amounts
        basel_buckets = merged.groupby('Basel_III_Category')['amount'].sum().to_dict()
        
        # Debugging: Print buckets to console (visible in Streamlit 'Manage app' logs)
        print(f"Mapped Buckets: {basel_buckets}")
        
        return basel_buckets
    except Exception as e:
        print(f"Mapping Error in utils.py: {e}")
        return {}
