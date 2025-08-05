#!/usr/bin/env python3
"""
Compare 2019 and 2024 BLS OES Data
Analyze changes in Los Angeles location quotients over time
"""

import pandas as pd
import os

def load_2019_data():
    """Load 2019 data"""
    data_file = "scrapers/oes_data_2019/la_oes_2019_selenium_data.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ 2019 data file not found: {data_file}")
        return None
    
    try:
        df = pd.read_csv(data_file)
        print(f"✅ Loaded 2019 data: {df.shape}")
        return df
    except Exception as e:
        print(f"❌ Error loading 2019 data: {e}")
        return None

def load_2024_data():
    """Load 2024 data"""
    data_file = "oes_data/la_oes_cleaned_data.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ 2024 data file not found: {data_file}")
        return None
    
    try:
        df = pd.read_csv(data_file)
        print(f"✅ Loaded 2024 data: {df.shape}")
        return df
    except Exception as e:
        print(f"❌ Error loading 2024 data: {e}")
        return None

def clean_and_prepare_data(df_2019, df_2024):
    """Clean and prepare data for comparison"""
    print("🧹 Preparing data for comparison...")
    
    try:
        # Clean 2019 data
        df_2019_clean = df_2019.copy()
        df_2019_clean['Location quotient'] = pd.to_numeric(df_2019_clean['Location quotient'], errors='coerce')
        
        # Clean 2024 data
        df_2024_clean = df_2024.copy()
        df_2024_clean['Location Quotient  ()'] = pd.to_numeric(df_2024_clean['Location Quotient  ()'], errors='coerce')
        
        # Create occupation mapping
        # 2019: 'Occupation title (click on the occupation title to view its profile)'
        # 2024: 'Occupation (SOC code)'
        
        # Extract occupation names and clean them
        df_2019_clean['Occupation_clean'] = df_2019_clean['Occupation title (click on the occupation title to view its profile)'].str.replace(r'\(click on the occupation title to view its profile\)', '', regex=True).str.strip()
        df_2024_clean['Occupation_clean'] = df_2024_clean['Occupation (SOC code)'].str.replace(r'\(\d+-\d+\)', '', regex=True).str.strip()
        
        print(f"📊 2019 occupations: {len(df_2019_clean)}")
        print(f"📊 2024 occupations: {len(df_2024_clean)}")
        
        return df_2019_clean, df_2024_clean
        
    except Exception as e:
        print(f"❌ Error preparing data: {e}")
        return None, None

def find_matching_occupations(df_2019, df_2024):
    """Find matching occupations between 2019 and 2024"""
    print("🔍 Finding matching occupations...")
    
    try:
        # Create sets of occupation names
        occupations_2019 = set(df_2019['Occupation_clean'].str.lower())
        occupations_2024 = set(df_2024['Occupation_clean'].str.lower())
        
        # Find common occupations
        common_occupations = occupations_2019.intersection(occupations_2024)
        
        print(f"📊 Common occupations found: {len(common_occupations)}")
        
        # Create merged dataset
        merged_data = []
        
        for occupation in common_occupations:
            # Find in 2019 data
            row_2019 = df_2019[df_2019['Occupation_clean'].str.lower() == occupation]
            row_2024 = df_2024[df_2024['Occupation_clean'].str.lower() == occupation]
            
            if not row_2019.empty and not row_2024.empty:
                lq_2019 = row_2019['Location quotient'].iloc[0]
                lq_2024 = row_2024['Location Quotient  ()'].iloc[0]
                
                if pd.notna(lq_2019) and pd.notna(lq_2024):
                    merged_data.append({
                        'Occupation': occupation.title(),
                        'LQ_2019': lq_2019,
                        'LQ_2024': lq_2024,
                        'Change': lq_2024 - lq_2019,
                        'Percent_Change': ((lq_2024 - lq_2019) / lq_2019) * 100 if lq_2019 > 0 else 0
                    })
        
        merged_df = pd.DataFrame(merged_data)
        print(f"📊 Merged dataset: {len(merged_df)} occupations")
        
        return merged_df
        
    except Exception as e:
        print(f"❌ Error finding matching occupations: {e}")
        return None

def analyze_changes(merged_df):
    """Analyze changes between 2019 and 2024"""
    print("\n📊 ANALYZING CHANGES (2019-2024)")
    print("=" * 50)
    
    if merged_df is None or merged_df.empty:
        print("❌ No data to analyze")
        return
    
    try:
        # Basic statistics
        print(f"📊 Total occupations compared: {len(merged_df)}")
        print(f"📈 Mean LQ 2019: {merged_df['LQ_2019'].mean():.3f}")
        print(f"📈 Mean LQ 2024: {merged_df['LQ_2024'].mean():.3f}")
        print(f"📈 Mean change: {merged_df['Change'].mean():.3f}")
        print(f"📈 Mean percent change: {merged_df['Percent_Change'].mean():.1f}%")
        
        # Biggest increases
        print(f"\n🚀 TOP 10 BIGGEST INCREASES (2019-2024):")
        print("-" * 70)
        print(f"{'Rank':<4} {'Occupation':<40} {'2019':<8} {'2024':<8} {'Change':<8} {'% Change':<10}")
        print("-" * 70)
        
        biggest_increases = merged_df.nlargest(10, 'Change')
        for i, (_, row) in enumerate(biggest_increases.iterrows(), 1):
            print(f"{i:<4} {row['Occupation'][:39]:<40} {row['LQ_2019']:<8.3f} {row['LQ_2024']:<8.3f} {row['Change']:<8.3f} {row['Percent_Change']:<9.1f}%")
        
        # Biggest decreases
        print(f"\n📉 TOP 10 BIGGEST DECREASES (2019-2024):")
        print("-" * 70)
        print(f"{'Rank':<4} {'Occupation':<40} {'2019':<8} {'2024':<8} {'Change':<8} {'% Change':<10}")
        print("-" * 70)
        
        biggest_decreases = merged_df.nsmallest(10, 'Change')
        for i, (_, row) in enumerate(biggest_decreases.iterrows(), 1):
            print(f"{i:<4} {row['Occupation'][:39]:<40} {row['LQ_2019']:<8.3f} {row['LQ_2024']:<8.3f} {row['Change']:<8.3f} {row['Percent_Change']:<9.1f}%")
        
        # Biggest percentage changes
        print(f"\n📊 TOP 10 BIGGEST PERCENTAGE CHANGES (2019-2024):")
        print("-" * 70)
        print(f"{'Rank':<4} {'Occupation':<40} {'2019':<8} {'2024':<8} {'Change':<8} {'% Change':<10}")
        print("-" * 70)
        
        biggest_percent_changes = merged_df.nlargest(10, 'Percent_Change')
        for i, (_, row) in enumerate(biggest_percent_changes.iterrows(), 1):
            print(f"{i:<4} {row['Occupation'][:39]:<40} {row['LQ_2019']:<8.3f} {row['LQ_2024']:<8.3f} {row['Change']:<8.3f} {row['Percent_Change']:<9.1f}%")
        
        # Summary statistics
        print(f"\n📈 CHANGE SUMMARY:")
        print("-" * 40)
        
        increased = merged_df[merged_df['Change'] > 0]
        decreased = merged_df[merged_df['Change'] < 0]
        no_change = merged_df[merged_df['Change'] == 0]
        
        print(f"   Occupations with increased LQ: {len(increased)} ({len(increased)/len(merged_df)*100:.1f}%)")
        print(f"   Occupations with decreased LQ: {len(decreased)} ({len(decreased)/len(merged_df)*100:.1f}%)")
        print(f"   Occupations with no change: {len(no_change)} ({len(no_change)/len(merged_df)*100:.1f}%)")
        
        # Save results
        output_file = "oes_data/la_location_quotient_comparison_2019_2024.csv"
        merged_df.to_csv(output_file, index=False)
        print(f"\n💾 Comparison results saved to {output_file}")
        
        return merged_df
        
    except Exception as e:
        print(f"❌ Error analyzing changes: {e}")
        return None

def main():
    """Main function to compare 2019 and 2024 data"""
    print("🚀 Comparing 2019 and 2024 BLS OES Data")
    print("=" * 50)
    
    try:
        # Load data
        df_2019 = load_2019_data()
        df_2024 = load_2024_data()
        
        if df_2019 is None or df_2024 is None:
            print("❌ Could not load data")
            return
        
        # Clean and prepare data
        df_2019_clean, df_2024_clean = clean_and_prepare_data(df_2019, df_2024)
        
        if df_2019_clean is None or df_2024_clean is None:
            print("❌ Could not prepare data")
            return
        
        # Find matching occupations
        merged_df = find_matching_occupations(df_2019_clean, df_2024_clean)
        
        if merged_df is None:
            print("❌ Could not find matching occupations")
            return
        
        # Analyze changes
        results = analyze_changes(merged_df)
        
        if results is not None:
            print(f"\n✅ Comparison completed successfully!")
            print(f"📊 Compared {len(results)} occupations")
            print(f"📁 Results saved to oes_data/la_location_quotient_comparison_2019_2024.csv")
            
        else:
            print("\n❌ Comparison failed")
            
    except Exception as e:
        print(f"❌ Error in main comparison: {e}")

if __name__ == "__main__":
    main() 