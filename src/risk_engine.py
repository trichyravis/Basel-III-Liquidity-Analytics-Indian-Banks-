import pandas as pd

def calculate_ratios(buckets, config, r_stress=1.0, h_stress=1.0):
    # LCR Logic
    hqla = (buckets.get('Level_1_HQLA', 0) * (1 - (0.0 * h_stress))) + \
           (buckets.get('Level_2A_HQLA', 0) * (1 - (0.15 * h_stress)))
    
    outflows = buckets.get('Retail_Stable', 0) * (config['regulatory_settings']['lcr']['run_off_rates']['retail_stable'] * r_stress)
    lcr = (hqla / outflows * 100) if outflows > 0 else 0
    
    # NSFR Logic
    asf = (buckets.get('Equity_Capital', 0) * 1.0) + (buckets.get('Retail_Stable', 0) * 0.9)
    rsf = (buckets.get('Loans_to_Retail', 0) * 0.85)
    nsfr = (asf / rsf * 100) if rsf > 0 else 0
    
    return round(lcr, 2), round(nsfr, 2)
