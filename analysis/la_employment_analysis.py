#!/usr/bin/env python3
"""
Los Angeles Employment Analysis - Alternative to Location Quotients
Analyze Los Angeles employment trends and sector concentration changes from 2013-2023
"""

import os
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LAEmploymentAnalyzer:
    """Analyzer for Los Angeles employment data"""
    
    def __init__(self):
        self.api_key = os.getenv('BLS_API_KEY')
        if not self.api_key:
            raise ValueError("BLS_API_KEY not found in environment variables")
        
        self.base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        self.session = requests.Session()
        self.session.headers.update({
            'BLS-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def get_la_employment_series(self):
        """Get Los Angeles employment series IDs"""
        # Los Angeles MSA employment series
        la_series = {
            # Total employment
            "CEU3108000001": "Los Angeles Total Nonfarm Employment",
            "CEU3108000501": "Los Angeles Private Employment",
            "CEU3108009001": "Los Angeles Government Employment",
            
            # Major sectors
            "CEU3108001001": "Los Angeles Mining and Logging",
            "CEU3108002001": "Los Angeles Construction",
            "CEU3108003001": "Los Angeles Manufacturing",
            "CEU3108004001": "Los Angeles Trade, Transportation, and Utilities",
            "CEU3108005001": "Los Angeles Information",
            "CEU3108005501": "Los Angeles Financial Activities",
            "CEU3108006001": "Los Angeles Professional and Business Services",
            "CEU3108006501": "Los Angeles Education and Health Services",
            "CEU3108007001": "Los Angeles Leisure and Hospitality",
            "CEU3108008001": "Los Angeles Other Services",
        }
        
        return la_series
    
    def get_national_employment_series(self):
        """Get national employment series for comparison"""
        national_series = {
            "CEU0000000001": "National Total Nonfarm Employment",
            "CEU0500000001": "National Private Employment",
            "CEU9000000001": "National Government Employment",
            "CEU1000000001": "National Mining and Logging",
            "CEU2000000001": "National Construction",
            "CEU3000000001": "National Manufacturing",
            "CEU4000000001": "National Trade, Transportation, and Utilities",
            "CEU5000000001": "National Information",
            "CEU5500000001": "National Financial Activities",
            "CEU6000000001": "National Professional and Business Services",
            "CEU6500000001": "National Education and Health Services",
            "CEU7000000001": "National Leisure and Hospitality",
            "CEU8000000001": "National Other Services",
        }
        
        return national_series
    
    def fetch_employment_data(self, series_dict, start_year=2013, end_year=2023):
        """Fetch employment data for multiple series"""
        all_data = []
        
        for series_id, description in series_dict.items():
            print(f"🔍 Fetching: {description}")
            
            payload = {
                "seriesid": [series_id],
                "startyear": str(start_year),
                "endyear": str(end_year),
                "registrationkey": self.api_key
            }
            
            try:
                response = self.session.post(self.base_url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                if data.get('status') == 'REQUEST_SUCCEEDED':
                    if data['Results']['series'][0] is not None:
                        series_data = data['Results']['series'][0]
                        
                        for item in series_data.get('data', []):
                            all_data.append({
                                'series_id': series_id,
                                'description': description,
                                'year': item.get('year'),
                                'period': item.get('period'),
                                'periodName': item.get('periodName'),
                                'value': item.get('value'),
                            })
                        
                        print(f"✅ Retrieved {len(series_data.get('data', []))} data points")
                    else:
                        print(f"⚠️  No data for {description}")
                else:
                    print(f"❌ Request failed for {description}")
                    
            except Exception as e:
                print(f"❌ Error fetching {description}: {e}")
        
        return all_data
    
    def calculate_concentration_metrics(self, la_data, national_data):
        """Calculate employment concentration metrics"""
        # Convert to DataFrames
        la_df = pd.DataFrame(la_data)
        national_df = pd.DataFrame(national_data)
        
        # Convert values to numeric
        la_df['value'] = pd.to_numeric(la_df['value'], errors='coerce')
        national_df['value'] = pd.to_numeric(national_df['value'], errors='coerce')
        
        # Create date column
        la_df['date'] = pd.to_datetime(la_df['year'] + '-' + la_df['period'].str[1:], format='%Y-%m')
        national_df['date'] = pd.to_datetime(national_df['year'] + '-' + national_df['period'].str[1:], format='%Y-%m')
        
        # Calculate concentration ratios (similar to location quotients)
        concentration_data = []
        
        for la_series in la_df['series_id'].unique():
            la_series_data = la_df[la_df['series_id'] == la_series]
            la_description = la_series_data['description'].iloc[0]
            
            # Find corresponding national series
            national_series = la_series.replace('3108', '0000')  # Convert LA to national
            national_series_data = national_df[national_df['series_id'] == national_series]
            
            if not national_series_data.empty:
                national_description = national_series_data['description'].iloc[0]
                
                # Merge on date
                merged = pd.merge(la_series_data, national_series_data, 
                                on='date', suffixes=('_la', '_national'))
                
                for _, row in merged.iterrows():
                    try:
                        la_value = float(row['value_la'])
                        national_value = float(row['value_national'])
                        
                        # Calculate concentration ratio
                        concentration_ratio = (la_value / national_value) * 100
                        
                        concentration_data.append({
                            'date': row['date'],
                            'sector': la_description.replace('Los Angeles ', ''),
                            'la_employment': la_value,
                            'national_employment': national_value,
                            'concentration_ratio': concentration_ratio,
                            'year': row['year_la']
                        })
                    except (ValueError, TypeError, ZeroDivisionError):
                        continue
        
        return pd.DataFrame(concentration_data)
    
    def analyze_concentration_changes(self, concentration_df):
        """Analyze concentration changes from 2013 to 2023"""
        if concentration_df.empty:
            print("❌ No concentration data available")
            return None
        
        # Get 2013 and 2023 data
        data_2013 = concentration_df[concentration_df['year'] == '2013']
        data_2023 = concentration_df[concentration_df['year'] == '2023']
        
        # Calculate changes
        changes = []
        for sector in concentration_df['sector'].unique():
            sector_2013 = data_2013[data_2013['sector'] == sector]
            sector_2023 = data_2023[data_2023['sector'] == sector]
            
            if not sector_2013.empty and not sector_2023.empty:
                conc_2013 = sector_2013['concentration_ratio'].iloc[0]
                conc_2023 = sector_2023['concentration_ratio'].iloc[0]
                
                change = conc_2023 - conc_2013
                percent_change = ((conc_2023 - conc_2013) / conc_2013) * 100 if conc_2013 > 0 else 0
                
                changes.append({
                    'sector': sector,
                    'concentration_2013': conc_2013,
                    'concentration_2023': conc_2023,
                    'change': change,
                    'percent_change': percent_change
                })
        
        return pd.DataFrame(changes)
    
    def create_visualizations(self, concentration_df, changes_df):
        """Create visualizations of the analysis"""
        if concentration_df.empty:
            return
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Los Angeles Employment Concentration Analysis (2013-2023)', fontsize=16, fontweight='bold')
        
        # 1. Concentration ratios over time
        ax1 = axes[0, 0]
        for sector in concentration_df['sector'].unique():
            sector_data = concentration_df[concentration_df['sector'] == sector].sort_values('date')
            if not sector_data.empty:
                ax1.plot(sector_data['date'], sector_data['concentration_ratio'], label=sector, linewidth=2)
        
        ax1.set_title('Employment Concentration Ratios Over Time')
        ax1.set_ylabel('Concentration Ratio (% of National)')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 2. Concentration changes (2013-2023)
        ax2 = axes[0, 1]
        if not changes_df.empty:
            colors = ['green' if x > 0 else 'red' for x in changes_df['change']]
            bars = ax2.barh(changes_df['sector'], changes_df['change'], color=colors, alpha=0.7)
            ax2.set_title('Concentration Changes (2013-2023)')
            ax2.set_xlabel('Change in Concentration Ratio')
            ax2.axvline(x=0, color='black', linestyle='-', alpha=0.5)
        
        # 3. Latest concentration levels
        ax3 = axes[1, 0]
        latest_data = concentration_df.groupby('sector')['concentration_ratio'].last().sort_values(ascending=False)
        if not latest_data.empty:
            ax3.bar(range(len(latest_data)), latest_data.values, alpha=0.7)
            ax3.set_title('Latest Employment Concentration Levels')
            ax3.set_ylabel('Concentration Ratio (% of National)')
            ax3.set_xticks(range(len(latest_data)))
            ax3.set_xticklabels(latest_data.index, rotation=45, ha='right')
        
        # 4. Employment growth comparison
        ax4 = axes[1, 1]
        if not changes_df.empty:
            # Calculate employment growth
            la_growth = []
            national_growth = []
            sectors = []
            
            for sector in changes_df['sector']:
                sector_data = concentration_df[concentration_df['sector'] == sector]
                if len(sector_data) > 1:
                    first_la = sector_data.iloc[0]['la_employment']
                    last_la = sector_data.iloc[-1]['la_employment']
                    first_national = sector_data.iloc[0]['national_employment']
                    last_national = sector_data.iloc[-1]['national_employment']
                    
                    if first_la > 0 and first_national > 0:
                        la_growth.append(((last_la - first_la) / first_la) * 100)
                        national_growth.append(((last_national - first_national) / first_national) * 100)
                        sectors.append(sector)
            
            if la_growth and national_growth:
                x = range(len(sectors))
                width = 0.35
                ax4.bar([i - width/2 for i in x], la_growth, width, label='Los Angeles', alpha=0.7)
                ax4.bar([i + width/2 for i in x], national_growth, width, label='National', alpha=0.7)
                ax4.set_title('Employment Growth Comparison (2013-2023)')
                ax4.set_ylabel('Growth Rate (%)')
                ax4.set_xticks(x)
                ax4.set_xticklabels(sectors, rotation=45, ha='right')
                ax4.legend()
        
        plt.tight_layout()
        
        # Save the plot
        output_file = "la_employment_concentration_analysis.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"📊 Visualization saved to {output_file}")
        
        plt.show()
    
    def print_analysis_results(self, changes_df):
        """Print analysis results"""
        if changes_df is None or changes_df.empty:
            print("❌ No analysis results available")
            return
        
        print("\n📊 LOS ANGELES EMPLOYMENT CONCENTRATION ANALYSIS (2013-2023)")
        print("=" * 80)
        
        # Sort by absolute change
        changes_df_sorted = changes_df.sort_values('change', key=abs, ascending=False)
        
        print("\n🏆 BIGGEST CONCENTRATION CHANGES")
        print("-" * 80)
        print(f"{'Rank':<4} {'Sector':<40} {'2013':<8} {'2023':<8} {'Change':<8} {'% Change':<10}")
        print("-" * 80)
        
        for i, (_, row) in enumerate(changes_df_sorted.iterrows(), 1):
            change_symbol = "+" if row['change'] > 0 else ""
            percent_symbol = "+" if row['percent_change'] > 0 else ""
            print(f"{i:<4} {row['sector'][:39]:<40} {row['concentration_2013']:<8.2f} {row['concentration_2023']:<8.2f} {change_symbol}{row['change']:<7.2f} {percent_symbol}{row['percent_change']:<9.1f}%")
        
        # Save results
        output_file = "la_employment_concentration_changes.csv"
        changes_df.to_csv(output_file, index=False)
        print(f"\n💾 Complete results saved to {output_file}")

def main():
    """Main function to run the analysis"""
    print("🚀 Los Angeles Employment Concentration Analysis")
    print("=" * 60)
    
    try:
        analyzer = LAEmploymentAnalyzer()
        
        # Get series definitions
        la_series = analyzer.get_la_employment_series()
        national_series = analyzer.get_national_employment_series()
        
        print(f"📊 Analyzing {len(la_series)} Los Angeles employment sectors")
        print(f"📊 Comparing with {len(national_series)} national employment sectors")
        
        # Fetch data
        print("\n🔍 Fetching Los Angeles employment data...")
        la_data = analyzer.fetch_employment_data(la_series)
        
        print("\n🔍 Fetching national employment data...")
        national_data = analyzer.fetch_employment_data(national_series)
        
        if la_data and national_data:
            # Calculate concentration metrics
            print("\n📈 Calculating concentration metrics...")
            concentration_df = analyzer.calculate_concentration_metrics(la_data, national_data)
            
            # Analyze changes
            print("\n📊 Analyzing concentration changes...")
            changes_df = analyzer.analyze_concentration_changes(concentration_df)
            
            # Print results
            analyzer.print_analysis_results(changes_df)
            
            # Create visualizations
            print("\n📊 Creating visualizations...")
            analyzer.create_visualizations(concentration_df, changes_df)
            
            print(f"\n✅ Analysis completed successfully!")
        else:
            print("❌ Could not retrieve employment data")
            
    except Exception as e:
        print(f"❌ Error running analysis: {e}")

if __name__ == "__main__":
    main() 