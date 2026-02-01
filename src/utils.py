
# Inside src/utils.py
def apply_basel_mapping(financials_series, mapping_path="data/mapping/bank_map.csv"):
    mapping_df = pd.read_csv(mapping_path)
    
    # Clean both sides to ensure a match
    mapping_df['Yahoo_Finance_Label'] = mapping_df['Yahoo_Finance_Label'].str.strip().str.lower()
    
    raw_data = financials_series.to_frame(name='amount').reset_index()
    raw_data['index'] = raw_data['index'].str.strip().str.lower()
    
    merged = raw_data.merge(mapping_df, left_on='index', right_on='Yahoo_Finance_Label')
    return merged.groupby('Basel_III_Category')['amount'].sum().to_dict()
