#!/usr/bin/env python3
"""
Manual OES Data Analysis for Los Angeles Location Quotients
Analyze manually downloaded OES data files for Los Angeles MSA
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

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
        print("Visit: https://www.bls.gov/oes/2019/may/oessrcma.htm")
        return None
    
    if not os.path.exists(file_2024):
        print(f"❌ File not found: {file_2024}")
        print("Please download the 2024 OES data file first")
        print("Visit: https://www.bls.gov/oes/2024/may/oessrcma.htm")
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
    
    if results is not None:
        # Create visualizations
        create_visualizations(results, la_data_2019, la_data_2024)
    
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
        print("📋 Available columns in 2019 data:")
        print(data_2019.columns.tolist())
        print("📋 Available columns in 2024 data:")
        print(data_2024.columns.tolist())
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
    
    # Show biggest percentage changes
    biggest_percent = merged.sort_values('lq_percent_change', key=abs, ascending=False)
    
    print(f"\n📈 BIGGEST PERCENTAGE CHANGES (2019-2024)")
    print("-" * 80)
    print(f"{'Rank':<4} {'Occupation':<50} {'2019':<8} {'2024':<8} {'Change':<8} {'% Change':<10}")
    print("-" * 80)
    
    for i, (_, row) in enumerate(biggest_percent.head(10).iterrows(), 1):
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

def create_visualizations(results, data_2019, data_2024):
    """Create visualizations of the analysis"""
    if results is None or results.empty:
        return
    
    print("\n📊 Creating visualizations...")
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Los Angeles Location Quotient Analysis (2019-2024)', fontsize=16, fontweight='bold')
    
    # 1. Biggest absolute changes
    ax1 = axes[0, 0]
    top_10_changes = results.sort_values('lq_change', key=abs, ascending=False).head(10)
    
    colors = ['green' if x > 0 else 'red' for x in top_10_changes['lq_change']]
    bars = ax1.barh(range(len(top_10_changes)), top_10_changes['lq_change'], color=colors, alpha=0.7)
    ax1.set_title('Biggest Location Quotient Changes (2019-2024)')
    ax1.set_xlabel('Change in Location Quotient')
    ax1.set_yticks(range(len(top_10_changes)))
    ax1.set_yticklabels([str(x)[:30] + '...' if len(str(x)) > 30 else str(x) for x in top_10_changes.iloc[:, 0]], fontsize=8)
    ax1.axvline(x=0, color='black', linestyle='-', alpha=0.5)
    
    # 2. Biggest percentage changes
    ax2 = axes[0, 1]
    top_10_percent = results.sort_values('lq_percent_change', key=abs, ascending=False).head(10)
    
    colors = ['green' if x > 0 else 'red' for x in top_10_percent['lq_percent_change']]
    bars = ax2.barh(range(len(top_10_percent)), top_10_percent['lq_percent_change'], color=colors, alpha=0.7)
    ax2.set_title('Biggest Percentage Changes (2019-2024)')
    ax2.set_xlabel('Percentage Change (%)')
    ax2.set_yticks(range(len(top_10_percent)))
    ax2.set_yticklabels([str(x)[:30] + '...' if len(str(x)) > 30 else str(x) for x in top_10_percent.iloc[:, 0]], fontsize=8)
    ax2.axvline(x=0, color='black', linestyle='-', alpha=0.5)
    
    # 3. Distribution of changes
    ax3 = axes[1, 0]
    ax3.hist(results['lq_change'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    ax3.set_title('Distribution of Location Quotient Changes')
    ax3.set_xlabel('Change in Location Quotient')
    ax3.set_ylabel('Number of Occupations')
    ax3.axvline(x=0, color='red', linestyle='--', alpha=0.7)
    
    # 4. Scatter plot of 2019 vs 2024
    ax4 = axes[1, 1]
    # Get the LQ column names
    lq_cols = [col for col in results.columns if 'lq' in col.lower() and any(year in col for year in ['2019', '2024'])]
    if len(lq_cols) >= 2:
        ax4.scatter(results[lq_cols[0]], results[lq_cols[1]], alpha=0.6, s=20)
        ax4.plot([0, max(results[lq_cols[0]].max(), results[lq_cols[1]].max())], 
                [0, max(results[lq_cols[0]].max(), results[lq_cols[1]].max())], 
                'r--', alpha=0.5)
        ax4.set_title('2019 vs 2024 Location Quotients')
        ax4.set_xlabel('2019 Location Quotient')
        ax4.set_ylabel('2024 Location Quotient')
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    output_file = os.path.join("oes_data", "la_location_quotient_visualization.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"📊 Visualization saved to {output_file}")
    
    plt.show()

def print_summary_statistics(results):
    """Print summary statistics"""
    if results is None or results.empty:
        return
    
    print("\n📊 SUMMARY STATISTICS")
    print("=" * 50)
    
    # Basic stats
    print(f"Total occupations analyzed: {len(results)}")
    print(f"Average LQ change: {results['lq_change'].mean():.3f}")
    print(f"Median LQ change: {results['lq_change'].median():.3f}")
    print(f"Standard deviation: {results['lq_change'].std():.3f}")
    
    # Positive vs negative changes
    positive_changes = results[results['lq_change'] > 0]
    negative_changes = results[results['lq_change'] < 0]
    
    print(f"\n📈 Positive changes: {len(positive_changes)} occupations ({len(positive_changes)/len(results)*100:.1f}%)")
    print(f"📉 Negative changes: {len(negative_changes)} occupations ({len(negative_changes)/len(results)*100:.1f}%)")
    
    # Top sectors
    print(f"\n🏆 Top 5 increasing sectors:")
    top_increasing = results.sort_values('lq_change', ascending=False).head(5)
    for i, (_, row) in enumerate(top_increasing.iterrows(), 1):
        occupation = str(row.iloc[0])[:40]
        change = row['lq_change']
        print(f"  {i}. {occupation}: +{change:.3f}")
    
    print(f"\n📉 Top 5 decreasing sectors:")
    top_decreasing = results.sort_values('lq_change', ascending=True).head(5)
    for i, (_, row) in enumerate(top_decreasing.iterrows(), 1):
        occupation = str(row.iloc[0])[:40]
        change = row['lq_change']
        print(f"  {i}. {occupation}: {change:.3f}")

if __name__ == "__main__":
    print("🚀 Manual OES Data Analysis for Los Angeles Location Quotients")
    print("=" * 70)
    
    results = analyze_manual_oes_data()
    
    if results is not None:
        print_summary_statistics(results)
        print(f"\n✅ Analysis completed successfully!")
        print(f"📊 Analyzed {len(results)} occupations in Los Angeles MSA")
        print(f"📈 Data covers 2019-2024 period")
        print(f"\n📁 Files created:")
        print(f"  - oes_data/la_location_quotient_analysis_2019_2024.csv")
        print(f"  - oes_data/la_location_quotient_visualization.png")
    else:
        print("\n❌ Analysis could not be completed")
        print("Please ensure you have downloaded the OES data files:")
        print("  - oes_data/oes_2019_srcma.xlsx")
        print("  - oes_data/oes_2024_srcma.xlsx") 