
def calculate_lcr_v2(buckets, config, custom_run_off=None, custom_haircut=None):
    """Calculates LCR with optional stress overrides."""
    # Apply Haircuts to HQLA
    h_rate = custom_haircut if custom_haircut is not None else 0.0
    
    level_1 = buckets.get('Level_1_HQLA', 0) * (1 - h_rate)
    level_2 = buckets.get('Level_2A_HQLA', 0) * (1 - 0.15) # Standard 15% haircut
    
    hqla_total = level_1 + level_2
    
    # Apply Run-off to Outflows
    r_rate = custom_run_off if custom_run_off is not None else config['regulatory_settings']['lcr']['run_off_rates']['retail_stable']
    
    outflows = buckets.get('Retail_Stable', 0) * r_rate
    
    lcr = (hqla_total / outflows * 100) if outflows > 0 else 0
    return round(lcr, 2)

def calculate_nsfr(buckets, config):
    """Calculates structural funding stability (NSFR)."""
    asf = (buckets.get('Equity_Capital', 0) * 1.0) + (buckets.get('Retail_Stable', 0) * 0.90)
    rsf = (buckets.get('Loans_to_Retail', 0) * 0.85)
    
    nsfr = (asf / rsf * 100) if rsf > 0 else 0
    return round(nsfr, 2)
