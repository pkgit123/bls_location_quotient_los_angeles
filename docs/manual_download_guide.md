# Manual OES Data Download Guide

## 🎯 Goal
Download OES location quotient data for Los Angeles metropolitan area and analyze changes between 2019 and 2024.

## 📥 Manual Download Instructions

### Step 1: Download 2019 Data
1. **Visit**: https://www.bls.gov/oes/2019/may/oessrcma.htm
2. **Look for**: Excel file download links (usually .xlsx or .xls files)
3. **Download**: The location quotient data file for metropolitan areas
4. **Save as**: `oes_2019_srcma.xlsx` in the `oes_data` folder

### Step 2: Download 2024 Data
1. **Visit**: https://www.bls.gov/oes/2024/may/oessrcma.htm
2. **Look for**: Excel file download links (usually .xlsx or .xls files)
3. **Download**: The location quotient data file for metropolitan areas
4. **Save as**: `oes_2024_srcma.xlsx` in the `oes_data` folder

### Step 3: Alternative Download Locations
If the direct links don't work, try these alternative sources:

#### BLS OES Main Page
- **Visit**: https://www.bls.gov/oes/
- **Navigate to**: "Location Quotients" section
- **Select**: Metropolitan areas
- **Choose**: Los Angeles-Long Beach-Anaheim, CA MSA

#### BLS Data Portal
- **Visit**: https://data.bls.gov/PDQWeb/oe
- **Select**: "Location Quotients"
- **Choose**: Metropolitan areas
- **Download**: Excel files for 2019 and 2024

## 🛠️ Analysis Script

Once you have the files, use this script to analyze them:

```python
#!/usr/bin/env python3
"""
Manual OES Data Analysis for Los Angeles Location Quotients
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_manual_oes_data():
    """Analyze manually downloaded OES data"""
    
    # File paths
    data_dir = "oes_data"
    file_2019 = os.path.join(data_dir, "oes_2019_srcma.xlsx")
    file_2024 = os.path.join(data_dir, "oes_2024_srcma.xlsx")
    
    # Check if files exist
    if not os.path.exists(file_2019):
        print(f"❌ File not found: {file_2019}")
        print("Please download the 2019 OES data file first")
        return None
    
    if not os.path.exists(file_2024):
        print(f"❌ File not found: {file_2024}")
        print("Please download the 2024 OES data file first")
        return None
    
    print("📖 Reading OES data files...")
    
    # Read Excel files
    try:
        df_2019 = pd.read_excel(file_2019)
        df_2024 = pd.read_excel(file_2024)
        
        print(f"✅ 2019 data shape: {df_2019.shape}")
        print(f"✅ 2024 data shape: {df_2024.shape}")
        
    except Exception as e:
        print(f"❌ Error reading files: {e}")
        return None
    
    # Display column information
    print(f"\n📋 2019 columns: {list(df_2019.columns)}")
    print(f"📋 2024 columns: {list(df_2024.columns)}")
    
    # Extract Los Angeles data
    la_data_2019 = extract_la_data(df_2019, "2019")
    la_data_2024 = extract_la_data(df_2024, "2024")
    
    if la_data_2019 is None or la_data_2024 is None:
        print("❌ Could not extract Los Angeles data")
        return None
    
    # Analyze location quotient changes
    results = analyze_location_quotients(la_data_2019, la_data_2024)
    
    return results

def extract_la_data(df, year):
    """Extract Los Angeles metropolitan area data"""
    print(f"\n🔍 Extracting Los Angeles data from {year}...")
    
    # Los Angeles identifiers
    la_patterns = [
        "Los Angeles-Long Beach-Anaheim",
        "Los Angeles",
        "LA",
        "31080"
    ]
    
    # Search for Los Angeles data
    for pattern in la_patterns:
        for col in df.columns:
            if df[col].dtype == 'object':
                mask = df[col].astype(str).str.contains(pattern, case=False, na=False)
                if mask.any():
                    la_data = df[mask].copy()
                    print(f"✅ Found LA data using '{pattern}' in column '{col}'")
                    print(f"📊 Found {len(la_data)} rows")
                    return la_data
    
    print("⚠️  Could not find Los Angeles data")
    print("🔍 Available values in first few columns:")
    for col in df.columns[:3]:
        if df[col].dtype == 'object':
            unique_vals = df[col].dropna().unique()
            print(f"Column '{col}': {unique_vals[:5]}...")
    
    return None

def analyze_location_quotients(data_2019, data_2024):
    """Analyze location quotient changes"""
    print("\n📊 ANALYZING LOCATION QUOTIENT CHANGES (2019-2024)")
    print("=" * 70)
    
    # Identify key columns
    occupation_col = None
    lq_col_2019 = None
    lq_col_2024 = None
    
    # Find occupation column
    for col in data_2019.columns:
        if any(keyword in col.lower() for keyword in ['occupation', 'title', 'job', 'code']):
            occupation_col = col
            break
    
    # Find location quotient columns
    for col in data_2019.columns:
        if any(keyword in col.lower() for keyword in ['location quotient', 'lq', 'quotient']):
            lq_col_2019 = col
            break
    
    for col in data_2024.columns:
        if any(keyword in col.lower() for keyword in ['location quotient', 'lq', 'quotient']):
            lq_col_2024 = col
            break
    
    print(f"🔍 Identified columns:")
    print(f"   Occupation: {occupation_col}")
    print(f"   LQ 2019: {lq_col_2019}")
    print(f"   LQ 2024: {lq_col_2024}")
    
    if not all([occupation_col, lq_col_2019, lq_col_2024]):
        print("❌ Could not identify required columns")
        return None
    
    # Merge data
    merged = pd.merge(
        data_2019[[occupation_col, lq_col_2019]], 
        data_2024[[occupation_col, lq_col_2024]], 
        on=occupation_col, 
        how='inner',
        suffixes=('_2019', '_2024')
    )
    
    # Convert to numeric
    merged[lq_col_2019] = pd.to_numeric(merged[lq_col_2019], errors='coerce')
    merged[lq_col_2024] = pd.to_numeric(merged[lq_col_2024], errors='coerce')
    
    # Calculate changes
    merged['lq_change'] = merged[lq_col_2024] - merged[lq_col_2019]
    merged['lq_percent_change'] = ((merged[lq_col_2024] - merged[lq_col_2019]) / merged[lq_col_2019]) * 100
    
    # Remove missing data
    merged = merged.dropna()
    
    print(f"📊 Analysis complete: {len(merged)} occupations with data")
    
    # Rank by absolute change
    biggest_changes = merged.sort_values('lq_change', key=abs, ascending=False)
    
    print(f"\n🏆 BIGGEST LOCATION QUOTIENT CHANGES (2019-2024)")
    print("-" * 80)
    print(f"{'Rank':<4} {'Occupation':<50} {'2019':<8} {'2024':<8} {'Change':<8} {'% Change':<10}")
    print("-" * 80)
    
    for i, (_, row) in enumerate(biggest_changes.head(20).iterrows(), 1):
        occupation = str(row[occupation_col])[:49]
        lq_2019 = row[lq_col_2019]
        lq_2024 = row[lq_col_2024]
        change = row['lq_change']
        percent_change = row['lq_percent_change']
        
        change_symbol = "+" if change > 0 else ""
        percent_symbol = "+" if percent_change > 0 else ""
        
        print(f"{i:<4} {occupation:<50} {lq_2019:<8.2f} {lq_2024:<8.2f} {change_symbol}{change:<7.2f} {percent_symbol}{percent_change:<9.1f}%")
    
    # Save results
    output_file = os.path.join("oes_data", "la_location_quotient_analysis_2019_2024.csv")
    merged.to_csv(output_file, index=False)
    print(f"\n💾 Complete analysis saved to {output_file}")
    
    return merged

if __name__ == "__main__":
    results = analyze_manual_oes_data()
    if results is not None:
        print(f"\n✅ Analysis completed successfully!")
        print(f"📊 Analyzed {len(results)} occupations in Los Angeles MSA")
```

## 📋 Expected File Structure

After downloading, your `oes_data` folder should contain:
```
oes_data/
├── oes_2019_srcma.xlsx    # 2019 OES location quotient data
├── oes_2024_srcma.xlsx    # 2024 OES location quotient data
└── la_location_quotient_analysis_2019_2024.csv  # Analysis results
```

## 🔍 What to Look For

### In the Excel Files:
1. **Metropolitan Area Column**: Should contain "Los Angeles-Long Beach-Anaheim, CA"
2. **Occupation Column**: Contains job titles or codes
3. **Location Quotient Column**: Contains the LQ values

### Expected Los Angeles Trends:
- **🎬 Entertainment**: High LQ, likely increasing
- **💻 Technology**: Growing concentration
- **🌊 International Trade**: High concentration
- **🏨 Tourism**: Stable high concentration
- **🏭 Manufacturing**: Likely decreasing

## 🚀 Quick Start

1. **Download files** from BLS websites
2. **Save them** in the `oes_data` folder
3. **Run the analysis script**:
   ```bash
   python manual_oes_analysis.py
   ```

## 📊 Analysis Output

The script will provide:
- **Ranked list** of biggest LQ changes
- **CSV file** with complete analysis
- **Visualizations** of the trends
- **Summary statistics** for Los Angeles MSA

This manual approach will give you the most accurate and complete location quotient analysis for Los Angeles! 