#!/usr/bin/env python3
"""
Analyze 2019 BLS OES Data
Analyze the already extracted 2019 data from CSV
"""

import pandas as pd
import os

def analyze_2019_data():
    """Analyze the 2019 OES data"""
    print("📊 ANALYZING 2019 BLS OES DATA")
    print("=" * 50)
    
    # Read the 2019 data
    data_file = "scrapers/oes_data_2019/la_oes_2019_selenium_data.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return None
    
    try:
        df = pd.read_csv(data_file)
        print(f"✅ Successfully loaded 2019 data")
        print(f"📊 Data shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Clean the data
        df = clean_2019_data(df)
        
        if df is not None:
            # Analyze the data
            analyze_oes_data_2019(df)
            
            # Create location quotient report
            create_location_quotient_report_2019(df)
            
            return df
        else:
            print("❌ Failed to clean the data")
            return None
            
    except Exception as e:
        print(f"❌ Error analyzing 2019 data: {e}")
        return None

def clean_2019_data(df):
    """Clean the 2019 data"""
    print("🧹 Cleaning 2019 data...")
    
    try:
        # Remove any completely empty rows
        df = df.dropna(how='all')
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Find occupation column
        occupation_col = None
        occupation_keywords = ['occupation', 'title', 'job', 'soc']
        for col in df.columns:
            if any(keyword in col.lower() for keyword in occupation_keywords):
                occupation_col = col
                break
        
        if occupation_col:
            # Remove rows that don't have proper occupation data
            df = df[df[occupation_col].notna()]
            df = df[df[occupation_col].astype(str).str.strip() != '']
            
            # Remove header rows (rows that contain column names)
            header_indicators = ['occupation', 'soc code', 'employment', 'wage', 'title']
            df = df[~df[occupation_col].astype(str).str.lower().str.contains('|'.join(header_indicators), na=False)]
        
        # Clean Location Quotient column
        lq_col = None
        lq_keywords = ['location quotient', 'lq', 'quotient']
        for col in df.columns:
            if any(keyword in col.lower() for keyword in lq_keywords):
                lq_col = col
                break
        
        if lq_col:
            print(f"🔧 Cleaning Location Quotient column: {lq_col}")
            # Convert to numeric (should already be clean)
            df[lq_col] = pd.to_numeric(df[lq_col], errors='coerce')
            print(f"✅ Location Quotient column cleaned")
        
        print(f"📊 Cleaned data shape: {df.shape}")
        
        # Show sample of cleaned data
        print("📄 Sample of cleaned data:")
        print(df.head())
        
        return df
        
    except Exception as e:
        print(f"❌ Error cleaning data: {e}")
        return None

def analyze_oes_data_2019(df):
    """Analyze the 2019 OES data"""
    print("\n📊 ANALYZING LOS ANGELES 2019 OES DATA")
    print("=" * 50)
    
    if df is None or df.empty:
        print("❌ No data to analyze")
        return
    
    print(f"📊 Total occupations: {len(df)}")
    
    # Find location quotient column
    lq_col = None
    lq_keywords = ['location quotient', 'lq', 'quotient']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in lq_keywords):
            lq_col = col
            break
    
    if lq_col is None:
        print("❌ Location Quotient column not found")
        return
    
    print(f"🎯 Location Quotient column: {lq_col}")
    
    # Basic statistics
    try:
        lq_stats = df[lq_col].describe()
        print(f"\n📈 Location Quotient Statistics:")
        print(f"   Count: {lq_stats['count']:.0f}")
        print(f"   Mean: {lq_stats['mean']:.3f}")
        print(f"   Median: {lq_stats['50%']:.3f}")
        print(f"   Min: {lq_stats['min']:.3f}")
        print(f"   Max: {lq_stats['max']:.3f}")
        print(f"   Std: {lq_stats['std']:.3f}")
        
        # Find highest LQ occupations
        print(f"\n🏆 TOP 10 HIGHEST LOCATION QUOTIENTS (2019):")
        print("-" * 60)
        
        top_lq = df.nlargest(10, lq_col)
        for i, (_, row) in enumerate(top_lq.iterrows(), 1):
            occupation = str(row.iloc[1])[:50]  # Second column should be occupation title
            lq_value = row[lq_col]
            print(f"{i:2d}. {occupation:<50} LQ: {lq_value:.3f}")
        
        # Find lowest LQ occupations
        print(f"\n📉 TOP 10 LOWEST LOCATION QUOTIENTS (2019):")
        print("-" * 60)
        
        bottom_lq = df.nsmallest(10, lq_col)
        for i, (_, row) in enumerate(bottom_lq.iterrows(), 1):
            occupation = str(row.iloc[1])[:50]  # Second column should be occupation title
            lq_value = row[lq_col]
            print(f"{i:2d}. {occupation:<50} LQ: {lq_value:.3f}")
        
        # Analyze by LQ categories
        print(f"\n📊 LOCATION QUOTIENT DISTRIBUTION (2019):")
        print("-" * 40)
        
        high_concentration = df[df[lq_col] > 2.0]
        moderate_concentration = df[(df[lq_col] > 1.0) & (df[lq_col] <= 2.0)]
        average_concentration = df[(df[lq_col] > 0.5) & (df[lq_col] <= 1.0)]
        low_concentration = df[df[lq_col] <= 0.5]
        
        print(f"   High concentration (LQ > 2.0): {len(high_concentration)} occupations")
        print(f"   Moderate concentration (1.0 < LQ ≤ 2.0): {len(moderate_concentration)} occupations")
        print(f"   Average concentration (0.5 < LQ ≤ 1.0): {len(average_concentration)} occupations")
        print(f"   Low concentration (LQ ≤ 0.5): {len(low_concentration)} occupations")
        
        # Save analysis results
        analysis_file = "scrapers/oes_data_2019/la_oes_2019_analysis_results.csv"
        
        # Create analysis summary
        analysis_summary = pd.DataFrame({
            'Metric': ['Total Occupations', 'High Concentration (LQ>2)', 'Moderate Concentration (1<LQ≤2)', 
                      'Average Concentration (0.5<LQ≤1)', 'Low Concentration (LQ≤0.5)', 'Mean LQ', 'Median LQ'],
            'Value': [len(df), len(high_concentration), len(moderate_concentration), 
                     len(average_concentration), len(low_concentration), 
                     lq_stats['mean'], lq_stats['50%']]
        })
        
        analysis_summary.to_csv(analysis_file, index=False)
        print(f"\n💾 Analysis results saved to {analysis_file}")
        
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")

def create_location_quotient_report_2019(df):
    """Create a comprehensive location quotient report for 2019"""
    print("\n📋 CREATING 2019 LOCATION QUOTIENT REPORT")
    print("=" * 50)
    
    if df is None or df.empty:
        print("❌ No data for report")
        return
    
    # Find key columns
    occupation_col = None
    lq_col = None
    
    # Find occupation column (should be the second column)
    occupation_col = df.columns[1]  # Occupation title column
    
    # Find location quotient column
    lq_keywords = ['location quotient', 'lq', 'quotient']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in lq_keywords):
            lq_col = col
            break
    
    if occupation_col is None or lq_col is None:
        print("❌ Could not find required columns")
        return
    
    try:
        # Create ranked report
        report_data = []
        
        for _, row in df.iterrows():
            occupation = str(row[occupation_col])
            lq_value = row[lq_col]
            
            # Categorize by LQ
            if lq_value > 2.0:
                category = "Very High Concentration"
            elif lq_value > 1.5:
                category = "High Concentration"
            elif lq_value > 1.0:
                category = "Above Average"
            elif lq_value > 0.5:
                category = "Average"
            else:
                category = "Low Concentration"
            
            report_data.append({
                'Occupation': occupation,
                'Location_Quotient': lq_value,
                'Category': category
            })
        
        # Create DataFrame and sort by LQ
        report_df = pd.DataFrame(report_data)
        report_df = report_df.sort_values('Location_Quotient', ascending=False)
        report_df.insert(0, 'Rank', range(1, len(report_df) + 1))
        
        # Save report
        report_file = "scrapers/oes_data_2019/la_location_quotient_2019_report.csv"
        report_df.to_csv(report_file, index=False)
        print(f"💾 Location quotient report saved to {report_file}")
        
        # Print summary
        print(f"\n📊 REPORT SUMMARY:")
        print(f"   Total occupations analyzed: {len(report_df)}")
        print(f"   Very High Concentration (LQ > 2.0): {len(report_df[report_df['Location_Quotient'] > 2.0])}")
        print(f"   High Concentration (LQ > 1.5): {len(report_df[report_df['Location_Quotient'] > 1.5])}")
        print(f"   Above Average (LQ > 1.0): {len(report_df[report_df['Location_Quotient'] > 1.0])}")
        
    except Exception as e:
        print(f"❌ Error creating report: {e}")

def main():
    """Main function to analyze 2019 data"""
    print("🚀 Analyzing 2019 BLS OES Data")
    print("=" * 50)
    
    try:
        # Analyze the 2019 data
        cleaned_data = analyze_2019_data()
        
        if cleaned_data is not None:
            print(f"\n✅ 2019 Data analysis completed successfully!")
            print(f"📊 Analyzed {len(cleaned_data)} occupations")
            print(f"📁 Files created in scrapers/oes_data_2019/")
            
        else:
            print("\n❌ Data analysis failed")
            
    except Exception as e:
        print(f"❌ Error in main analysis: {e}")

if __name__ == "__main__":
    main() 