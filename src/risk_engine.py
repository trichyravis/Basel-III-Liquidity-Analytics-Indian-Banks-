
def calculate_ratios(buckets, config, r_stress=1.0, h_stress=1.0):
    """
    Core Risk Engine: Calculates LCR and NSFR based on Basel III standards.
   
    """
    # 1. LIQUIDITY COVERAGE RATIO (LCR) CALCULATION
    # Apply Haircuts to HQLA (Level 1 and Level 2A)
    # Haircut multipliers increase as h_stress increases
    h_multiplier = h_stress
    
    level_1 = buckets.get('Level_1_HQLA', 0) * (1 - (0.0 * h_multiplier))
    level_2 = buckets.get('Level_2A_HQLA', 0) * (1 - (0.15 * h_multiplier))
    
    total_hqla = level_1 + level_2
    
    # Apply Run-off rates to Outflows
    # Standard 5% for retail; multiplier increases as r_stress increases
    base_run_off = config['regulatory_settings']['lcr']['run_off_rates']['retail_stable']
    total_outflows = buckets.get('Retail_Stable', 0) * (base_run_off * r_stress)
    
    lcr = (total_hqla / total_outflows * 100) if total_outflows > 0 else 0
    
    # 2. NET STABLE FUNDING RATIO (NSFR) CALCULATION
    # ASF (Available Stable Funding) / RSF (Required Stable Funding)
    asf = (buckets.get('Equity_Capital', 0) * 1.0) + (buckets.get('Retail_Stable', 0) * 0.90)
    rsf = (buckets.get('Loans_to_Retail', 0) * 0.85)
    
    nsfr = (asf / rsf * 100) if rsf > 0 else 0
    
    return round(lcr, 2), round(nsfr, 2)
