# Los Angeles Location Quotient Analysis Guide

## 🎯 Objective
Compare Los Angeles metropolitan area location quotients for all occupations between 2013 and 2023, ranking the biggest changes.

## 📊 What We Discovered

### ✅ What Works with BLS API
- **Employment data (CEU series)**: Monthly employment levels by sector
- **CPI data**: Consumer Price Index data
- **Basic economic indicators**: Various economic time series

### ❌ What Doesn't Work with BLS API
- **OES Location Quotients**: Not available through the API
- **Occupational employment by metro area**: Limited availability
- **Specialized OES datasets**: Often portal-only

## 🔍 Alternative Approaches

### Option 1: BLS Data Portal (Recommended)
The most reliable way to get location quotient data is through the BLS data portal:

1. **Visit**: https://data.bls.gov/PDQWeb/oe
2. **Select**: "Location Quotients" 
3. **Choose**:
   - Area: Los Angeles-Long Beach-Anaheim, CA MSA (31080)
   - Time Period: 2013 and 2023
   - Occupation: All occupations or specific ones
4. **Download**: CSV files for analysis

### Option 2: BLS API with Different Series
Try these alternative series IDs that might work:

```python
# Alternative OES series patterns to test
alternative_series = [
    "OES31080000000000000000000000000000",  # All occupations
    "OES31080151132000000000000000000000",  # Software Developers
    "OES31080291141000000000000000000000",  # Registered Nurses
    "OES31080272000000000000000000000000",  # Entertainment
    "OES31080172000000000000000000000000",  # Arts and Design
]
```

### Option 3: Employment Data Analysis
Since we have working employment data, we can analyze sector concentration changes:

```python
# Los Angeles employment concentration analysis
la_employment_series = {
    "CEU3108000001": "Los Angeles Total Nonfarm",
    "CEU3108000501": "Los Angeles Private",
    "CEU3108009001": "Los Angeles Government",
}
```

## 📈 Location Quotient Interpretation

### What Location Quotients Mean
- **LQ > 1.0**: Higher concentration than national average
- **LQ = 1.0**: Same concentration as national average
- **LQ < 1.0**: Lower concentration than national average

### Expected LA Trends (2013-2023)
Based on economic trends, we might expect:

**Likely Increases:**
- Entertainment and Media (Hollywood)
- Technology and Software Development
- International Trade and Logistics
- Tourism and Hospitality
- Creative Arts and Design

**Likely Decreases:**
- Manufacturing (continued decline)
- Some traditional industries

## 🛠️ Manual Data Collection Process

### Step 1: Portal Navigation
1. Go to https://data.bls.gov/PDQWeb/oe
2. Click "Location Quotients"
3. Select "Metropolitan Areas"
4. Choose "Los Angeles-Long Beach-Anaheim, CA"

### Step 2: Data Selection
1. **Year 1**: 2013
2. **Year 2**: 2023
3. **Occupation Level**: 
   - Major groups (2-digit codes)
   - Detailed occupations (6-digit codes)
4. **Data Type**: Location Quotients

### Step 3: Export and Analysis
1. Download CSV files
2. Import into Python/R/Excel
3. Calculate changes: LQ_2023 - LQ_2013
4. Rank by absolute change and percentage change

## 📊 Sample Analysis Code

```python
import pandas as pd
import numpy as np

def analyze_location_quotients(csv_file_2013, csv_file_2023):
    """Analyze location quotient changes"""
    
    # Load data
    df_2013 = pd.read_csv(csv_file_2013)
    df_2023 = pd.read_csv(csv_file_2023)
    
    # Merge data
    merged = pd.merge(df_2013, df_2023, 
                     on='occupation_code', 
                     suffixes=('_2013', '_2023'))
    
    # Calculate changes
    merged['lq_change'] = merged['lq_2023'] - merged['lq_2013']
    merged['lq_percent_change'] = ((merged['lq_2023'] - merged['lq_2013']) / merged['lq_2013']) * 100
    
    # Rank by absolute change
    biggest_changes = merged.sort_values('lq_change', key=abs, ascending=False)
    
    return biggest_changes
```

## 🎯 Key Occupations to Focus On

### High-Impact LA Occupations
1. **Entertainment**: Actors, Directors, Producers
2. **Technology**: Software Developers, Data Scientists
3. **Trade**: Import/Export Specialists, Logistics
4. **Tourism**: Hotel Managers, Tour Guides
5. **Creative**: Graphic Designers, Fashion Designers
6. **Healthcare**: Medical Specialists, Nurses
7. **Finance**: Investment Bankers, Financial Analysts

### Expected Findings
- **Entertainment**: Likely highest LQ, may be increasing
- **Technology**: Growing concentration
- **Manufacturing**: Declining concentration
- **Trade/Logistics**: Stable high concentration

## 📋 Next Steps

1. **Manual Data Collection**: Use BLS portal to get actual location quotient data
2. **Alternative Analysis**: Use employment data we have to show sector concentration trends
3. **Hybrid Approach**: Combine portal data with API employment data for comprehensive analysis

## 🔗 Useful Resources

- **BLS OES Homepage**: https://www.bls.gov/oes/
- **Location Quotients Guide**: https://www.bls.gov/oes/oes_emp.htm
- **Metropolitan Area Codes**: https://www.bls.gov/sae/additional-resources/metropolitan-area-codes.htm
- **Occupation Codes**: https://www.bls.gov/soc/

## 💡 Recommendation

For the most accurate and comprehensive analysis of Los Angeles location quotient changes from 2013-2023, I recommend:

1. **Use the BLS data portal** to manually collect location quotient data
2. **Focus on major occupation groups** first (easier to manage)
3. **Supplement with employment data** from our working API analysis
4. **Create a hybrid report** showing both location quotients and employment trends

This approach will give you the most reliable and complete picture of how occupational concentration in Los Angeles has changed over the past decade. 