#!/usr/bin/env python3
"""
Selenium-based BLS OES Web Scraper for Los Angeles Location Quotient Data
Handles JavaScript-heavy websites and extracts data from the BLS OES Query System
"""

import pandas as pd
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SeleniumBLSOESScraper:
    """Selenium-based scraper for BLS OES data"""
    
    def __init__(self):
        # Los Angeles MSA information
        self.la_area_code = "0031080"  # Los Angeles-Long Beach-Anaheim, CA MSA
        self.base_url = "https://data.bls.gov/oes"
        
        # Create data directory
        self.data_dir = "oes_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize webdriver
        self.driver = None
    
    def setup_driver(self):
        """Setup Chrome webdriver with appropriate options"""
        print("🔧 Setting up Chrome webdriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chrome webdriver initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing Chrome webdriver: {e}")
            print("💡 Make sure Chrome is installed and chromedriver is available")
            return False
    
    def navigate_to_oes_page(self):
        """Navigate to the BLS OES page for Los Angeles"""
        print("🌐 Navigating to BLS OES Query System...")
        
        url = f"{self.base_url}/#/area/{self.la_area_code}"
        print(f"📍 Target URL: {url}")
        
        try:
            self.driver.get(url)
            print("✅ Successfully loaded the page")
            
            # Wait for page to load
            time.sleep(5)
            
            # Check if page loaded correctly
            if "Los Angeles" in self.driver.page_source or "OES" in self.driver.page_source:
                print("✅ Page contains Los Angeles OES data")
                return True
            else:
                print("❌ Page does not contain expected data")
                return False
                
        except Exception as e:
            print(f"❌ Error navigating to page: {e}")
            return False
    
    def wait_for_data_to_load(self, timeout=30):
        """Wait for data to load on the page"""
        print("⏳ Waiting for data to load...")
        
        try:
            # Wait for common data elements to appear
            selectors = [
                "table",
                "[data-testid='data-table']",
                ".data-table",
                ".oes-data",
                "tbody",
                "tr"
            ]
            
            for selector in selectors:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Found data element: {selector}")
                    return True
                except TimeoutException:
                    continue
            
            print("⚠️  No standard data elements found, continuing anyway")
            return True
            
        except Exception as e:
            print(f"❌ Error waiting for data: {e}")
            return False
    
    def extract_table_data(self):
        """Extract table data from the page"""
        print("📋 Extracting table data...")
        
        try:
            # Find all tables on the page
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            print(f"📊 Found {len(tables)} tables on the page")
            
            all_data = []
            
            for i, table in enumerate(tables):
                print(f"🔍 Processing table {i+1}...")
                
                try:
                    # Get table HTML and convert to DataFrame
                    table_html = table.get_attribute('outerHTML')
                    df = pd.read_html(table_html)[0]
                    
                    print(f"📊 Table {i+1} shape: {df.shape}")
                    print(f"📋 Table {i+1} columns: {list(df.columns)}")
                    
                    # Check if this table contains Los Angeles data
                    if self.is_la_data_table(df):
                        print(f"✅ Found Los Angeles data in table {i+1}")
                        all_data.append(df)
                    
                except Exception as e:
                    print(f"❌ Error processing table {i+1}: {e}")
                    continue
            
            if all_data:
                # Combine all tables
                combined_df = pd.concat(all_data, ignore_index=True)
                print(f"📊 Combined data shape: {combined_df.shape}")
                return combined_df
            else:
                print("❌ No Los Angeles data found in tables")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting table data: {e}")
            return None
    
    def extract_data_from_elements(self):
        """Extract data from various page elements"""
        print("🔍 Extracting data from page elements...")
        
        try:
            # Look for data in different types of elements
            data_selectors = [
                "tbody tr",
                ".data-row",
                "[data-testid='data-row']",
                ".oes-row",
                "tr"
            ]
            
            all_rows = []
            
            for selector in data_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"📊 Found {len(elements)} elements with selector: {selector}")
                    
                    for element in elements[:10]:  # Limit to first 10 for testing
                        try:
                            text = element.text
                            if text and len(text.strip()) > 0:
                                # Split by whitespace or tabs
                                row_data = [cell.strip() for cell in text.split('\n') if cell.strip()]
                                if row_data:
                                    all_rows.append(row_data)
                        except Exception as e:
                            continue
                    
                    if all_rows:
                        break
                        
                except Exception as e:
                    continue
            
            if all_rows:
                # Convert to DataFrame
                df = pd.DataFrame(all_rows)
                print(f"📊 Extracted data shape: {df.shape}")
                return df
            else:
                print("❌ No data found in page elements")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting data from elements: {e}")
            return None
    
    def is_la_data_table(self, df):
        """Check if a table contains Los Angeles data"""
        if df.empty:
            return False
        
        # Convert all values to string and search for LA indicators
        df_str = df.astype(str)
        
        la_indicators = [
            'los angeles',
            'long beach',
            'anaheim',
            '31080',
            '0031080'
        ]
        
        for indicator in la_indicators:
            if df_str.apply(lambda x: x.str.contains(indicator, case=False, na=False)).any().any():
                return True
        
        return False
    
    def save_page_source(self):
        """Save the page source for debugging"""
        try:
            page_source = self.driver.page_source
            output_file = os.path.join(self.data_dir, "bls_oes_page_source.html")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(page_source)
            
            print(f"💾 Page source saved to {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Error saving page source: {e}")
            return None
    
    def take_screenshot(self):
        """Take a screenshot of the page"""
        try:
            screenshot_file = os.path.join(self.data_dir, "bls_oes_screenshot.png")
            self.driver.save_screenshot(screenshot_file)
            print(f"📸 Screenshot saved to {screenshot_file}")
            return screenshot_file
            
        except Exception as e:
            print(f"❌ Error taking screenshot: {e}")
            return None
    
    def get_oes_data(self):
        """Main method to get OES data"""
        print("🚀 Starting Selenium-based OES data extraction...")
        
        # Setup webdriver
        if not self.setup_driver():
            return None
        
        try:
            # Navigate to the page
            if not self.navigate_to_oes_page():
                return None
            
            # Wait for data to load
            self.wait_for_data_to_load()
            
            # Take screenshot for debugging
            self.take_screenshot()
            
            # Save page source for debugging
            self.save_page_source()
            
            # Try to extract table data
            data = self.extract_table_data()
            
            if data is None:
                # Try alternative extraction method
                print("🔄 Trying alternative data extraction method...")
                data = self.extract_data_from_elements()
            
            if data is not None:
                # Save the data
                output_file = os.path.join(self.data_dir, "la_oes_selenium_data.csv")
                data.to_csv(output_file, index=False)
                print(f"💾 Data saved to {output_file}")
                
                return data
            else:
                print("❌ Could not extract any data")
                return None
                
        except Exception as e:
            print(f"❌ Error during data extraction: {e}")
            return None
        
        finally:
            # Clean up
            if self.driver:
                self.driver.quit()
                print("🧹 Webdriver closed")
    
    def analyze_extracted_data(self, data):
        """Analyze the extracted data"""
        if data is None or data.empty:
            print("❌ No data to analyze")
            return None
        
        print("\n📊 ANALYZING EXTRACTED DATA")
        print("=" * 50)
        
        print(f"📊 Data shape: {data.shape}")
        print(f"📋 Columns: {list(data.columns)}")
        print(f"📄 First few rows:")
        print(data.head())
        
        # Try to identify location quotient data
        lq_columns = []
        for col in data.columns:
            if any(term in str(col).lower() for term in ['location quotient', 'lq', 'quotient']):
                lq_columns.append(col)
        
        if lq_columns:
            print(f"🎯 Found location quotient columns: {lq_columns}")
            
            # Basic statistics for LQ columns
            for col in lq_columns:
                try:
                    numeric_data = pd.to_numeric(data[col], errors='coerce')
                    print(f"\n📈 Statistics for {col}:")
                    print(f"   Mean: {numeric_data.mean():.3f}")
                    print(f"   Median: {numeric_data.median():.3f}")
                    print(f"   Min: {numeric_data.min():.3f}")
                    print(f"   Max: {numeric_data.max():.3f}")
                    print(f"   Count: {numeric_data.count()}")
                except Exception as e:
                    print(f"❌ Error analyzing {col}: {e}")
        else:
            print("⚠️  No location quotient columns found")
        
        return data

def main():
    """Main function to run the Selenium scraper"""
    print("🚀 Selenium-based BLS OES Web Scraper")
    print("=" * 50)
    
    scraper = SeleniumBLSOESScraper()
    
    # Get OES data
    data = scraper.get_oes_data()
    
    if data is not None:
        # Analyze the data
        scraper.analyze_extracted_data(data)
        
        print(f"\n✅ Successfully extracted OES data!")
        print(f"📊 Data shape: {data.shape}")
        print(f"📋 Columns: {list(data.columns)}")
        
    else:
        print("\n❌ Could not extract OES data")
        print("This may be because:")
        print("- The website structure has changed")
        print("- JavaScript is required but not working")
        print("- The data is loaded differently")
        print("- Authentication is required")
        
        print("\n💡 Next steps:")
        print("1. Check the saved page source and screenshot")
        print("2. Try manual download from the website")
        print("3. Use the BLS API if available")
        print("4. Contact BLS for direct data access")

if __name__ == "__main__":
    main() 