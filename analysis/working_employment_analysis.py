#!/usr/bin/env python3
"""
Working script to analyze BLS employment data that we can successfully retrieve.
This demonstrates the API functionality with data that's actually available.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from dotenv import load_dotenv
from bls_client import BLSClient

# Load environment variables
load_dotenv()

def get_employment_data():
    """Get employment data for analysis"""
    try:
        client = BLSClient()
        print("✅ BLS client initialized successfully")
    except ValueError as e:
        print(f"❌ Error initializing BLS client: {e}")
        return None
    
    # Employment series that work well
    employment_series = {
        "CEU0000000001": "Total Nonfarm Employment",
        "CEU0500000001": "Private Employment", 
        "CEU9000000001": "Government Employment",
        "CEU1000000001": "Mining and Logging",
        "CEU2000000001": "Construction",
        "CEU3000000001": "Manufacturing",
        "CEU4000000001": "Trade, Transportation, and Utilities",
        "CEU5000000001": "Information",
        "CEU5500000001": "Financial Activities",
        "CEU6000000001": "Professional and Business Services",
        "CEU6500000001": "Education and Health Services",
        "CEU7000000001": "Leisure and Hospitality",
        "CEU8000000001": "Other Services"
    }
    
    # Get data for the past 10 years
    current_year = datetime.now().year
    start_year = current_year - 10
    end_year = current_year
    
    print(f"📊 Fetching employment data from {start_year} to {end_year}")
    
    all_data = []
    
    for series_id, description in employment_series.items():
        try:
            print(f"🔍 Fetching: {description} ({series_id})")
            response = client.get_series_data([series_id], start_year, end_year)
            df = client.parse_series_response(response)
            
            if not df.empty:
                df['description'] = description
                all_data.append(df)
                print(f"✅ Retrieved {len(df)} data points")
            else:
                print(f"⚠️  No data for {description}")
                
        except Exception as e:
            print(f"❌ Error fetching {description}: {e}")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"\n📈 Total data points: {len(combined_df)}")
        return combined_df
    else:
        print("❌ No data retrieved")
        return None

def analyze_employment_trends(df):
    """Analyze employment trends"""
    if df is None or df.empty:
        return
    
    print("\n📊 Employment Trends Analysis")
    print("=" * 50)
    
    # Convert year to datetime for better plotting
    df['date'] = pd.to_datetime(df['year'] + '-' + df['period'].str[1:], format='%Y-%m')
    
    # Get latest data for each series
    latest_data = df.groupby('description')['value'].last().sort_values(ascending=False)
    
    print("\n🏢 Latest Employment Levels (thousands):")
    for description, value in latest_data.items():
        try:
            numeric_value = float(value)
            print(f"  {description}: {numeric_value:,.0f}")
        except (ValueError, TypeError):
            print(f"  {description}: {value}")
    
    # Calculate growth rates
    growth_data = []
    for description in df['description'].unique():
        series_data = df[df['description'] == description].sort_values('date')
        if len(series_data) > 1:
            try:
                first_value = float(series_data.iloc[0]['value'])
                last_value = float(series_data.iloc[-1]['value'])
                growth_rate = ((last_value - first_value) / first_value) * 100
                growth_data.append({
                    'description': description,
                    'growth_rate': growth_rate,
                    'start_value': first_value,
                    'end_value': last_value
                })
            except (ValueError, TypeError):
                continue
    
    growth_df = pd.DataFrame(growth_data)
    growth_df = growth_df.sort_values('growth_rate', ascending=False)
    
    print("\n📈 Employment Growth Rates (10-year):")
    for _, row in growth_df.iterrows():
        print(f"  {row['description']}: {row['growth_rate']:+.1f}%")
    
    return df, growth_df

def create_visualizations(df, growth_df):
    """Create visualizations of the employment data"""
    if df is None or df.empty:
        return
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('BLS Employment Data Analysis (10-Year Trends)', fontsize=16, fontweight='bold')
    
    # 1. Employment levels over time
    ax1 = axes[0, 0]
    for description in ['Total Nonfarm Employment', 'Private Employment', 'Government Employment']:
        series_data = df[df['description'] == description].sort_values('date')
        if not series_data.empty:
            ax1.plot(series_data['date'], series_data['value'], label=description, linewidth=2)
    
    ax1.set_title('Employment Levels Over Time')
    ax1.set_ylabel('Employment (thousands)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Growth rates by sector
    ax2 = axes[0, 1]
    if not growth_df.empty:
        colors = ['green' if x > 0 else 'red' for x in growth_df['growth_rate']]
        bars = ax2.barh(growth_df['description'], growth_df['growth_rate'], color=colors, alpha=0.7)
        ax2.set_title('Employment Growth by Sector (10-Year)')
        ax2.set_xlabel('Growth Rate (%)')
        ax2.axvline(x=0, color='black', linestyle='-', alpha=0.5)
        
        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            ax2.text(width + (0.5 if width > 0 else -0.5), bar.get_y() + bar.get_height()/2, 
                    f'{width:.1f}%', ha='left' if width > 0 else 'right', va='center')
    
    # 3. Latest employment distribution
    ax3 = axes[1, 0]
    latest_data = df.groupby('description')['value'].last().sort_values(ascending=False)
    if not latest_data.empty:
        ax3.pie(latest_data.values, labels=latest_data.index, autopct='%1.1f%%', startangle=90)
        ax3.set_title('Latest Employment Distribution')
    
    # 4. Employment volatility (standard deviation)
    ax4 = axes[1, 1]
    volatility = df.groupby('description')['value'].std().sort_values(ascending=False)
    if not volatility.empty:
        ax4.bar(range(len(volatility)), volatility.values, alpha=0.7)
        ax4.set_title('Employment Volatility (Standard Deviation)')
        ax4.set_ylabel('Standard Deviation')
        ax4.set_xticks(range(len(volatility)))
        ax4.set_xticklabels(volatility.index, rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "employment_analysis_visualization.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"📊 Visualization saved to {output_file}")
    
    plt.show()

def save_analysis_results(df, growth_df):
    """Save analysis results to CSV files"""
    if df is not None and not df.empty:
        # Save raw data
        df.to_csv("employment_data_analysis.csv", index=False)
        print("💾 Raw employment data saved to employment_data_analysis.csv")
    
    if growth_df is not None and not growth_df.empty:
        # Save growth analysis
        growth_df.to_csv("employment_growth_analysis.csv", index=False)
        print("💾 Growth analysis saved to employment_growth_analysis.csv")

def main():
    """Main function to run the employment analysis"""
    print("🚀 BLS Employment Data Analysis")
    print("=" * 50)
    
    # Get employment data
    df = get_employment_data()
    
    if df is not None:
        # Analyze trends
        df, growth_df = analyze_employment_trends(df)
        
        # Create visualizations
        create_visualizations(df, growth_df)
        
        # Save results
        save_analysis_results(df, growth_df)
        
        print("\n✅ Analysis completed successfully!")
    else:
        print("❌ Could not retrieve employment data")

if __name__ == "__main__":
    main() 