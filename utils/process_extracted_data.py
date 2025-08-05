#!/usr/bin/env python3
"""
Process Extracted BLS OES Data
Extract and analyze Los Angeles location quotient data from the saved HTML
"""

import pandas as pd
import os
from io import StringIO
import re

def process_extracted_html():
    """Process the extracted HTML data"""
    print("🔍 Processing extracted BLS OES HTML data...")
    
    # Read the saved HTML file
    html_file = os.path.join("oes_data", "bls_oes_page_source.html")
    
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        return None
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"✅ Successfully read HTML file ({len(html_content)} characters)")
        
        # Extract tables from HTML
        tables = pd.read_html(StringIO(html_content))
        print(f"📊 Found {len(tables)} tables in HTML")
        
        # Find the main data table (should be the one with 780 rows and 18 columns)
        main_table = None
        for i, table in enumerate(tables):
            print(f"📋 Table {i+1}: {table.shape} columns: {list(table.columns)}")
            
            # Look for the table with Location Quotient column
            if 'Location Quotient' in str(table.columns):
                main_table = table
                print(f"✅ Found main data table: Table {i+1}")
                break
        
        if main_table is None:
            print("❌ Could not find main data table with Location Quotient column")
            return None
        
        print(f"📊 Main table shape: {main_table.shape}")
        print(f"📋 Main table columns: {list(main_table.columns)}")
        
        # Clean up the data
        cleaned_table = clean_oes_data(main_table)
        
        if cleaned_table is not None:
            # Save the cleaned data
            output_file = os.path.join("oes_data", "la_oes_cleaned_data.csv")
            cleaned_table.to_csv(output_file, index=False)
            print(f"💾 Cleaned data saved to {output_file}")
            
            # Analyze the data
            analyze_oes_data(cleaned_table)
            
            return cleaned_table
        else:
            print("❌ Failed to clean the data")
            return None
            
    except Exception as e:
        print(f"❌ Error processing HTML: {e}")
        return None

def clean_oes_data(df):
    """Clean and process the OES data"""
    print("🧹 Cleaning OES data...")
    
    try:
        # Remove any completely empty rows
        df = df.dropna(how='all')
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Remove rows where occupation is empty or contains header info
        if 'Occupation (SOC code)' in df.columns:
            occupation_col = 'Occupation (SOC code)'
        else:
            # Find occupation column
            occupation_col = None
            for col in df.columns:
                if 'occupation' in col.lower():
                    occupation_col = col
                    break
        
        if occupation_col:
            # Remove rows that don't have proper occupation data
            df = df[df[occupation_col].notna()]
            df = df[df[occupation_col].astype(str).str.strip() != '']
            
            # Remove header rows (rows that contain column names)
            header_indicators = ['occupation', 'soc code', 'employment', 'wage']
            df = df[~df[occupation_col].astype(str).str.lower().str.contains('|'.join(header_indicators), na=False)]
        
        # Clean Location Quotient column specifically
        lq_col = None
        for col in df.columns:
            if 'location quotient' in col.lower():
                lq_col = col
                break
        
        if lq_col:
            print(f"🔧 Cleaning Location Quotient column: {lq_col}")
            # Remove the "()  " prefix and convert to numeric
            df[lq_col] = df[lq_col].astype(str).str.replace(r'\(\)\s*', '', regex=True)
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

def analyze_oes_data(df):
    """Analyze the OES data"""
    print("\n📊 ANALYZING LOS ANGELES OES DATA")
    print("=" * 50)
    
    if df is None or df.empty:
        print("❌ No data to analyze")
        return
    
    print(f"📊 Total occupations: {len(df)}")
    
    # Find location quotient column
    lq_col = None
    for col in df.columns:
        if 'location quotient' in col.lower():
            lq_col = col
            break
    
    if lq_col is None:
        print("❌ Location Quotient column not found")
        return
    
    print(f"🎯 Location Quotient column: {lq_col}")
    
    # Convert LQ to numeric
    try:
        df[lq_col] = pd.to_numeric(df[lq_col], errors='coerce')
        
        # Basic statistics
        lq_stats = df[lq_col].describe()
        print(f"\n📈 Location Quotient Statistics:")
        print(f"   Count: {lq_stats['count']:.0f}")
        print(f"   Mean: {lq_stats['mean']:.3f}")
        print(f"   Median: {lq_stats['50%']:.3f}")
        print(f"   Min: {lq_stats['min']:.3f}")
        print(f"   Max: {lq_stats['max']:.3f}")
        print(f"   Std: {lq_stats['std']:.3f}")
        
        # Find highest LQ occupations
        print(f"\n🏆 TOP 10 HIGHEST LOCATION QUOTIENTS:")
        print("-" * 60)
        
        top_lq = df.nlargest(10, lq_col)
        for i, (_, row) in enumerate(top_lq.iterrows(), 1):
            occupation = str(row.iloc[0])[:50]  # First column should be occupation
            lq_value = row[lq_col]
            print(f"{i:2d}. {occupation:<50} LQ: {lq_value:.3f}")
        
        # Find lowest LQ occupations
        print(f"\n📉 TOP 10 LOWEST LOCATION QUOTIENTS:")
        print("-" * 60)
        
        bottom_lq = df.nsmallest(10, lq_col)
        for i, (_, row) in enumerate(bottom_lq.iterrows(), 1):
            occupation = str(row.iloc[0])[:50]  # First column should be occupation
            lq_value = row[lq_col]
            print(f"{i:2d}. {occupation:<50} LQ: {lq_value:.3f}")
        
        # Analyze by LQ categories
        print(f"\n📊 LOCATION QUOTIENT DISTRIBUTION:")
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
        analysis_file = os.path.join("oes_data", "la_oes_analysis_results.csv")
        
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

def create_location_quotient_report(df):
    """Create a comprehensive location quotient report"""
    print("\n📋 CREATING LOCATION QUOTIENT REPORT")
    print("=" * 50)
    
    if df is None or df.empty:
        print("❌ No data for report")
        return
    
    # Find key columns
    occupation_col = None
    lq_col = None
    employment_col = None
    
    for col in df.columns:
        if 'occupation' in col.lower():
            occupation_col = col
        elif 'location quotient' in col.lower():
            lq_col = col
        elif 'employment' in col.lower() and 'percent' not in col.lower():
            employment_col = col
    
    if not all([occupation_col, lq_col]):
        print("❌ Required columns not found")
        return
    
    # Create detailed report
    report_data = []
    
    # Sort by location quotient
    sorted_df = df.sort_values(lq_col, ascending=False)
    
    for i, (_, row) in enumerate(sorted_df.iterrows(), 1):
        occupation = str(row[occupation_col])
        lq_value = row[lq_col]
        
        # Categorize by LQ level
        if lq_value > 2.0:
            category = "Very High Concentration"
        elif lq_value > 1.5:
            category = "High Concentration"
        elif lq_value > 1.0:
            category = "Above Average"
        elif lq_value > 0.5:
            category = "Below Average"
        else:
            category = "Low Concentration"
        
        report_data.append({
            'Rank': i,
            'Occupation': occupation,
            'Location_Quotient': lq_value,
            'Category': category
        })
    
    # Create report DataFrame
    report_df = pd.DataFrame(report_data)
    
    # Save report
    report_file = os.path.join("oes_data", "la_location_quotient_report.csv")
    report_df.to_csv(report_file, index=False)
    print(f"💾 Location quotient report saved to {report_file}")
    
    # Print summary
    print(f"\n📊 REPORT SUMMARY:")
    print(f"   Total occupations analyzed: {len(report_df)}")
    print(f"   Very High Concentration (LQ > 2.0): {len(report_df[report_df['Location_Quotient'] > 2.0])}")
    print(f"   High Concentration (LQ > 1.5): {len(report_df[report_df['Location_Quotient'] > 1.5])}")
    print(f"   Above Average (LQ > 1.0): {len(report_df[report_df['Location_Quotient'] > 1.0])}")
    
    return report_df

def main():
    """Main function to process extracted data"""
    print("🚀 Processing Extracted BLS OES Data")
    print("=" * 50)
    
    # Process the extracted HTML data
    data = process_extracted_html()
    
    if data is not None:
        # Create location quotient report
        report = create_location_quotient_report(data)
        
        print(f"\n✅ Data processing completed successfully!")
        print(f"📊 Processed {len(data)} occupations")
        print(f"📁 Files created:")
        print(f"   - oes_data/la_oes_cleaned_data.csv")
        print(f"   - oes_data/la_oes_analysis_results.csv")
        print(f"   - oes_data/la_location_quotient_report.csv")
        
        print(f"\n🎯 Key findings:")
        print(f"   - Los Angeles has {len(data)} occupations with location quotient data")
        print(f"   - Data includes employment, wages, and location quotients")
        print(f"   - Ready for comparison with other years or areas")
        
    else:
        print("\n❌ Data processing failed")
        print("Please ensure the HTML file exists and contains valid data")

if __name__ == "__main__":
    main() 