import pandas as pd

def apply_basel_mapping(financials_series, mapping_path="data/mapping/bank_map.csv"):
    """Maps raw Yahoo Finance labels to Basel III categories."""
    try:
        mapping_df = pd.read_csv(mapping_path)
        # Convert series to a manageable dataframe
        raw_data = financials_series.to_frame(name='amount').reset_index()
        
        # Join raw data with the mapping file
        merged = raw_data.merge(mapping_df, left_on='index', right_on='Yahoo_Finance_Label')
        
        # Group by the Basel Category and sum the amounts
        basel_buckets = merged.groupby('Basel_III_Category')['amount'].sum().to_dict()
        return basel_buckets
    except Exception as e:
        print(f"Mapping Error: {e}")
        return {}
