#!/usr/bin/env python3
"""
BLS OES Web Scraper for Los Angeles Location Quotient Analysis
Downloads and analyzes OES data directly from BLS websites
"""

import requests
import pandas as pd
import os
import zipfile
import io
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re

class BLSWebScraper:
    """Web scraper for BLS OES data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Los Angeles MSA information
        self.la_msa_code = "31080"
        self.la_msa_name = "Los Angeles-Long Beach-Anaheim, CA"
        
        # Create data directory
        self.data_dir = "oes_data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_oes_links(self, year):
        """Get OES data links for a specific year"""
        if year == 2024:
            base_url = "https://www.bls.gov/oes/2024/may/"
        elif year == 2019:
            base_url = "https://www.bls.gov/oes/2019/may/"
        else:
            raise ValueError(f"Year {year} not supported. Only 2019 and 2024 are supported.")
        
        # OES data file patterns
        file_patterns = [
            "oessrcma.xlsx",  # Location quotients by MSA
            "oessrcma.xls",   # Alternative format
            "oes_2024_may_srcma.xlsx",  # 2024 specific
            "oes_2019_may_srcma.xlsx",  # 2019 specific
        ]
        
        links = []
        for pattern in file_patterns:
            url = urljoin(base_url, pattern)
            try:
                response = self.session.head(url)
                if response.status_code == 200:
                    links.append(url)
                    print(f"✅ Found: {url}")
            except Exception as e:
                print(f"❌ Error checking {url}: {e}")
        
        return links
    
    def download_oes_file(self, url, year):
        """Download OES data file"""
        filename = f"oes_{year}_srcma.xlsx"
        filepath = os.path.join(self.data_dir, filename)
        
        print(f"🔍 Downloading {url}...")
        
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            # Check if it's a zip file
            if 'zip' in response.headers.get('content-type', ''):
                # Handle zip file
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                    # Extract Excel files
                    for file_info in zip_file.filelist:
                        if file_info.filename.endswith(('.xlsx', '.xls')):
                            with zip_file.open(file_info.filename) as file:
                                with open(filepath, 'wb') as f:
                                    f.write(file.read())
                            print(f"✅ Extracted: {file_info.filename} -> {filepath}")
                            break
            else:
                # Direct file download
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"✅ Downloaded: {filepath}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")
            return None
    
    def find_oes_data_links(self, year):
        """Find OES data links by scraping the main page"""
        if year == 2024:
            url = "https://www.bls.gov/oes/2024/may/oessrcma.htm"
        elif year == 2019:
            url = "https://www.bls.gov/oes/2019/may/oessrcma.htm"
        else:
            raise ValueError(f"Year {year} not supported")
        
        print(f"🔍 Scraping {url} for data links...")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Look for Excel file links
            excel_patterns = [
                r'href=["\']([^"\']*\.xlsx)["\']',
                r'href=["\']([^"\']*\.xls)["\']',
                r'href=["\']([^"\']*srcma[^"\']*)["\']',
            ]
            
            links = []
            for pattern in excel_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    if match.startswith('http'):
                        full_url = match
                    else:
                        full_url = urljoin(url, match)
                    
                    if full_url not in links:
                        links.append(full_url)
                        print(f"🔗 Found link: {full_url}")
            
            return links
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return []
    
    def download_all_oes_data(self):
        """Download OES data for both years"""
        years = [2019, 2024]
        downloaded_files = {}
        
        for year in years:
            print(f"\n📊 Processing {year} OES data...")
            print("=" * 50)
            
            # Try direct links first
            direct_links = self.get_oes_links(year)
            
            # If no direct links, scrape the page
            if not direct_links:
                print("🔍 No direct links found, scraping page...")
                direct_links = self.find_oes_data_links(year)
            
            # Download files
            for link in direct_links:
                filepath = self.download_oes_file(link, year)
                if filepath and os.path.exists(filepath):
                    downloaded_files[year] = filepath
                    break
            
            # Rate limiting
            time.sleep(2)
        
        return downloaded_files
    
    def read_oes_excel(self, filepath):
        """Read OES Excel file and extract Los Angeles data"""
        print(f"📖 Reading {filepath}...")
        
        try:
            # Try different sheet names
            sheet_names = ['Location Quotients', 'Location quotients', 'OES', 'Data', 'Sheet1']
            
            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet_name)
                    print(f"✅ Successfully read sheet: {sheet_name}")
                    break
                except:
                    continue
            else:
                # If no specific sheet works, try the first sheet
                df = pd.read_excel(filepath, sheet_name=0)
                print(f"✅ Read first sheet")
            
            # Display basic info
            print(f"📊 File shape: {df.shape}")
            print(f"📋 Columns: {list(df.columns)}")
            print(f"📄 First few rows:")
            print(df.head())
            
            return df
            
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            return None
    
    def extract_la_data(self, df, year):
        """Extract Los Angeles metropolitan area data"""
        if df is None or df.empty:
            return None
        
        print(f"\n🔍 Extracting Los Angeles data from {year}...")
        
        # Look for Los Angeles data
        la_data = None
        
        # Try different approaches to find LA data
        search_patterns = [
            self.la_msa_name,
            "Los Angeles",
            "LA",
            self.la_msa_code,
            "31080"
        ]
        
        for pattern in search_patterns:
            # Search in all columns
            for col in df.columns:
                if df[col].dtype == 'object':  # String columns
                    mask = df[col].astype(str).str.contains(pattern, case=False, na=False)
                    if mask.any():
                        la_data = df[mask].copy()
                        print(f"✅ Found LA data using pattern '{pattern}' in column '{col}'")
                        print(f"📊 Found {len(la_data)} rows")
                        break
            if la_data is not None:
                break
        
        if la_data is None:
            print("⚠️  Could not find Los Angeles data with common patterns")
            print("🔍 Showing all unique values in first few columns...")
            for col in df.columns[:5]:
                if df[col].dtype == 'object':
                    unique_vals = df[col].dropna().unique()
                    print(f"Column '{col}': {unique_vals[:10]}...")
        
        return la_data
    
    def analyze_location_quotients(self, data_2019, data_2024):
        """Analyze location quotient changes between 2019 and 2024"""
        print("\n📊 ANALYZING LOCATION QUOTIENT CHANGES (2019-2024)")
        print("=" * 70)
        
        if data_2019 is None or data_2024 is None:
            print("❌ Missing data for analysis")
            return None
        
        # Try to identify occupation and location quotient columns
        occupation_col = None
        lq_col_2019 = None
        lq_col_2024 = None
        
        # Look for occupation-related columns
        for col in data_2019.columns:
            if any(keyword in col.lower() for keyword in ['occupation', 'title', 'job', 'code']):
                occupation_col = col
                break
        
        # Look for location quotient columns
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
        
        # Merge data on occupation
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
        
        # Remove rows with missing data
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
        output_file = os.path.join(self.data_dir, "la_location_quotient_analysis_2019_2024.csv")
        merged.to_csv(output_file, index=False)
        print(f"\n💾 Complete analysis saved to {output_file}")
        
        return merged

def main():
    """Main function to run the web scraper and analysis"""
    print("🚀 BLS OES Web Scraper for Los Angeles Location Quotient Analysis")
    print("=" * 70)
    
    scraper = BLSWebScraper()
    
    # Download OES data
    print("📥 Downloading OES data...")
    downloaded_files = scraper.download_all_oes_data()
    
    if not downloaded_files:
        print("❌ No files downloaded")
        return
    
    print(f"\n✅ Downloaded files: {downloaded_files}")
    
    # Read and analyze data
    data_2019 = None
    data_2024 = None
    
    if 2019 in downloaded_files:
        df_2019 = scraper.read_oes_excel(downloaded_files[2019])
        data_2019 = scraper.extract_la_data(df_2019, 2019)
    
    if 2024 in downloaded_files:
        df_2024 = scraper.read_oes_excel(downloaded_files[2024])
        data_2024 = scraper.extract_la_data(df_2024, 2024)
    
    # Analyze location quotient changes
    results = scraper.analyze_location_quotients(data_2019, data_2024)
    
    if results is not None:
        print(f"\n✅ Analysis completed successfully!")
        print(f"📊 Analyzed {len(results)} occupations in Los Angeles MSA")
        print(f"📈 Data covers 2019-2024 period")
    else:
        print("\n❌ Analysis could not be completed")
        print("This may be due to:")
        print("- Different file formats than expected")
        print("- Different column names in the Excel files")
        print("- Los Angeles data not found in the expected format")

if __name__ == "__main__":
    main() 