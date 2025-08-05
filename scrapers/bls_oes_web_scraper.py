#!/usr/bin/env python3
"""
BLS OES Web Scraper for Los Angeles Location Quotient Data
Extracts data directly from the BLS OES Query System web interface
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime
import os

class BLSOESWebScraper:
    """Web scraper for BLS OES Query System"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Los Angeles MSA information
        self.la_area_code = "0031080"  # Los Angeles-Long Beach-Anaheim, CA MSA
        self.base_url = "https://data.bls.gov/oes"
        
        # Create data directory
        self.data_dir = "oes_data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_oes_data_from_web(self):
        """Get OES data directly from the BLS web interface"""
        print("🔍 Accessing BLS OES Query System...")
        print(f"📍 Target Area: Los Angeles-Long Beach-Anaheim, CA MSA ({self.la_area_code})")
        
        # The main URL for Los Angeles OES data
        url = f"{self.base_url}/#/area/{self.la_area_code}"
        
        try:
            print(f"🌐 Accessing: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            print(f"✅ Successfully accessed BLS OES website")
            print(f"📊 Response status: {response.status_code}")
            
            # Check if we can access the data
            if "Los Angeles" in response.text or "OES" in response.text:
                print("✅ Found Los Angeles OES data on the page")
                return self.extract_data_from_page(response.text)
            else:
                print("❌ Los Angeles data not found on the page")
                return None
                
        except Exception as e:
            print(f"❌ Error accessing BLS OES website: {e}")
            return None
    
    def extract_data_from_page(self, html_content):
        """Extract data from the HTML page"""
        print("🔍 Extracting data from webpage...")
        
        # Look for JSON data in the page
        try:
            # Try to find JSON data embedded in the page
            json_patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'var\s+data\s*=\s*({.*?});',
                r'"data":\s*({.*?})',
            ]
            
            for pattern in json_patterns:
                import re
                matches = re.findall(pattern, html_content, re.DOTALL)
                if matches:
                    print(f"✅ Found JSON data pattern")
                    try:
                        data = json.loads(matches[0])
                        return self.parse_json_data(data)
                    except json.JSONDecodeError:
                        continue
            
            # If no JSON found, try to extract table data
            return self.extract_table_data(html_content)
            
        except Exception as e:
            print(f"❌ Error extracting data: {e}")
            return None
    
    def parse_json_data(self, data):
        """Parse JSON data from the page"""
        print("📊 Parsing JSON data...")
        
        try:
            # Navigate through the JSON structure to find OES data
            if isinstance(data, dict):
                # Look for common keys that might contain OES data
                for key in ['oes', 'data', 'results', 'occupations', 'employment']:
                    if key in data:
                        print(f"✅ Found data key: {key}")
                        return self.process_oes_data(data[key])
                
                # If no direct key found, search recursively
                return self.search_json_recursively(data)
            
            return None
            
        except Exception as e:
            print(f"❌ Error parsing JSON: {e}")
            return None
    
    def search_json_recursively(self, obj, path=""):
        """Search recursively through JSON for OES data"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Look for occupation-related data
                if any(term in key.lower() for term in ['occupation', 'employment', 'wage', 'oes']):
                    print(f"🔍 Found potential data at: {current_path}")
                    return self.process_oes_data(value)
                
                # Recursively search
                result = self.search_json_recursively(value, current_path)
                if result is not None:
                    return result
                    
        elif isinstance(obj, list) and len(obj) > 0:
            # Check first few items in lists
            for i, item in enumerate(obj[:5]):
                result = self.search_json_recursively(item, f"{path}[{i}]")
                if result is not None:
                    return result
        
        return None
    
    def extract_table_data(self, html_content):
        """Extract table data from HTML"""
        print("📋 Extracting table data from HTML...")
        
        try:
            # Use pandas to read HTML tables
            tables = pd.read_html(html_content)
            
            if tables:
                print(f"✅ Found {len(tables)} tables in the HTML")
                
                for i, table in enumerate(tables):
                    print(f"📊 Table {i+1} shape: {table.shape}")
                    print(f"📋 Table {i+1} columns: {list(table.columns)}")
                    
                    # Check if this table contains Los Angeles data
                    if self.is_la_data_table(table):
                        print(f"✅ Found Los Angeles data in table {i+1}")
                        return self.process_table_data(table)
                
                print("❌ No Los Angeles data found in tables")
            else:
                print("❌ No tables found in HTML")
            
            return None
            
        except Exception as e:
            print(f"❌ Error extracting table data: {e}")
            return None
    
    def is_la_data_table(self, table):
        """Check if a table contains Los Angeles data"""
        if table.empty:
            return False
        
        # Convert all values to string and search for LA indicators
        table_str = table.astype(str)
        
        la_indicators = [
            'los angeles',
            'long beach',
            'anaheim',
            '31080',
            '0031080'
        ]
        
        for indicator in la_indicators:
            if table_str.apply(lambda x: x.str.contains(indicator, case=False, na=False)).any().any():
                return True
        
        return False
    
    def process_table_data(self, table):
        """Process table data into structured format"""
        print("🔄 Processing table data...")
        
        # Clean up the table
        table = table.dropna(how='all')
        
        # Try to identify columns
        occupation_col = None
        employment_col = None
        wage_col = None
        lq_col = None
        
        for col in table.columns:
            col_lower = str(col).lower()
            if any(term in col_lower for term in ['occupation', 'title', 'job']):
                occupation_col = col
            elif any(term in col_lower for term in ['employment', 'jobs']):
                employment_col = col
            elif any(term in col_lower for term in ['wage', 'salary', 'pay']):
                wage_col = col
            elif any(term in col_lower for term in ['location quotient', 'lq', 'quotient']):
                lq_col = col
        
        print(f"🔍 Identified columns:")
        print(f"   Occupation: {occupation_col}")
        print(f"   Employment: {employment_col}")
        print(f"   Wage: {wage_col}")
        print(f"   Location Quotient: {lq_col}")
        
        # Save the raw table
        output_file = os.path.join(self.data_dir, "la_oes_raw_data.csv")
        table.to_csv(output_file, index=False)
        print(f"💾 Raw data saved to {output_file}")
        
        return table
    
    def process_oes_data(self, data):
        """Process OES data into structured format"""
        print("🔄 Processing OES data...")
        
        if isinstance(data, list):
            # Convert list to DataFrame
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Convert dict to DataFrame
            df = pd.DataFrame([data])
        else:
            print(f"❌ Unexpected data type: {type(data)}")
            return None
        
        print(f"📊 Data shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Save the data
        output_file = os.path.join(self.data_dir, "la_oes_data.csv")
        df.to_csv(output_file, index=False)
        print(f"💾 Data saved to {output_file}")
        
        return df
    
    def get_location_quotient_data(self):
        """Get location quotient data specifically"""
        print("🎯 Attempting to get location quotient data...")
        
        # Try different approaches to get LQ data
        approaches = [
            self.get_oes_data_from_web,
            self.try_api_endpoints,
            self.try_alternative_urls
        ]
        
        for approach in approaches:
            try:
                print(f"\n🔍 Trying approach: {approach.__name__}")
                data = approach()
                if data is not None and not data.empty:
                    print(f"✅ Success with {approach.__name__}")
                    return data
            except Exception as e:
                print(f"❌ Approach {approach.__name__} failed: {e}")
                continue
        
        print("❌ All approaches failed")
        return None
    
    def try_api_endpoints(self):
        """Try to access API endpoints"""
        print("🔌 Trying API endpoints...")
        
        # Common API endpoints for OES data
        endpoints = [
            f"{self.base_url}/api/area/{self.la_area_code}/oes",
            f"{self.base_url}/api/area/{self.la_area_code}/location-quotients",
            f"{self.base_url}/api/area/{self.la_area_code}/data",
        ]
        
        for endpoint in endpoints:
            try:
                print(f"🔍 Trying endpoint: {endpoint}")
                response = self.session.get(endpoint)
                
                if response.status_code == 200:
                    print(f"✅ Success with endpoint: {endpoint}")
                    data = response.json()
                    return self.process_oes_data(data)
                else:
                    print(f"❌ Endpoint failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error with endpoint {endpoint}: {e}")
                continue
        
        return None
    
    def try_alternative_urls(self):
        """Try alternative URLs for OES data"""
        print("🌐 Trying alternative URLs...")
        
        # Alternative URLs that might contain OES data
        urls = [
            f"{self.base_url}/oes/area/{self.la_area_code}",
            f"{self.base_url}/oes/area/{self.la_area_code}/location-quotients",
            f"{self.base_url}/oes/area/{self.la_area_code}/data",
        ]
        
        for url in urls:
            try:
                print(f"🔍 Trying URL: {url}")
                response = self.session.get(url)
                
                if response.status_code == 200:
                    print(f"✅ Success with URL: {url}")
                    return self.extract_data_from_page(response.text)
                else:
                    print(f"❌ URL failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error with URL {url}: {e}")
                continue
        
        return None

def main():
    """Main function to run the web scraper"""
    print("🚀 BLS OES Web Scraper for Los Angeles Location Quotient Data")
    print("=" * 70)
    
    scraper = BLSOESWebScraper()
    
    # Get OES data
    data = scraper.get_location_quotient_data()
    
    if data is not None:
        print(f"\n✅ Successfully retrieved OES data!")
        print(f"📊 Data shape: {data.shape}")
        print(f"📋 Columns: {list(data.columns)}")
        print(f"📄 First few rows:")
        print(data.head())
        
        # Save final results
        output_file = os.path.join("oes_data", "la_oes_final_data.csv")
        data.to_csv(output_file, index=False)
        print(f"\n💾 Final data saved to {output_file}")
        
    else:
        print("\n❌ Could not retrieve OES data")
        print("This may be because:")
        print("- The website requires JavaScript to load data")
        print("- The data is loaded dynamically")
        print("- Authentication is required")
        print("- The website structure has changed")
        
        print("\n💡 Alternative approaches:")
        print("1. Use a browser automation tool like Selenium")
        print("2. Download data manually from the website")
        print("3. Use the BLS API if available")
        print("4. Contact BLS for direct data access")

if __name__ == "__main__":
    main() 