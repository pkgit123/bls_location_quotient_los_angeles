#!/usr/bin/env python3
"""
Selenium-based BLS OES Web Scraper for Los Angeles 2019 Data
Handles the 2019 BLS OES data format from the specific URL
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

class SeleniumBLSOESScraper2019:
    """Selenium-based scraper for 2019 BLS OES data"""
    
    def __init__(self):
        # 2019 Los Angeles OES data URL
        self.url = "https://www.bls.gov/oes/2019/may/oes_31080.htm"
        
        # Create data directory
        self.data_dir = "oes_data_2019"
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
        """Navigate to the 2019 BLS OES page for Los Angeles"""
        print("🌐 Navigating to 2019 BLS OES Data...")
        print(f"📍 Target URL: {self.url}")
        
        try:
            self.driver.get(self.url)
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
                "tbody",
                "tr",
                ".data-table",
                ".oes-data"
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
            
            print("⚠️  No standard data elements found, proceeding anyway...")
            return True
            
        except Exception as e:
            print(f"❌ Error waiting for data: {e}")
            return False
    
    def extract_table_data(self):
        """Extract data from tables on the page"""
        print("📋 Extracting table data...")
        
        try:
            # Find all tables on the page
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            print(f"📊 Found {len(tables)} tables on the page")
            
            main_table = None
            
            for i, table in enumerate(tables):
                print(f"🔍 Processing table {i+1}...")
                
                try:
                    # Get table HTML
                    table_html = table.get_attribute('outerHTML')
                    
                    # Try to read as pandas DataFrame
                    df = pd.read_html(table_html)[0]
                    print(f"📊 Table {i+1} shape: {df.shape}")
                    print(f"📋 Table {i+1} columns: {list(df.columns)}")
                    
                    # Check if this looks like the main data table
                    if self.is_la_data_table_2019(df):
                        main_table = df
                        print(f"✅ Found main data table: Table {i+1}")
                        break
                        
                except Exception as e:
                    print(f"❌ Error processing table {i+1}: {e}")
                    continue
            
            if main_table is not None:
                return main_table
            else:
                print("❌ No Los Angeles data found in tables")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting table data: {e}")
            return None
    
    def extract_data_from_elements(self):
        """Extract data from page elements as fallback"""
        print("🔍 Extracting data from page elements...")
        
        try:
            # Try different selectors for data rows
            selectors = [
                "tbody tr",
                ".data-row",
                "[data-testid='data-row']",
                ".oes-row",
                "tr"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"📊 Found {len(elements)} elements with selector: {selector}")
                    
                    if len(elements) > 10:  # Likely data rows
                        print(f"✅ Found potential data rows with selector: {selector}")
                        # Process these elements
                        return self.process_elements_to_dataframe(elements)
                        
                except Exception as e:
                    print(f"❌ Error with selector {selector}: {e}")
                    continue
            
            print("❌ No data found in page elements")
            return None
            
        except Exception as e:
            print(f"❌ Error extracting from elements: {e}")
            return None
    
    def process_elements_to_dataframe(self, elements):
        """Convert HTML elements to DataFrame"""
        try:
            data = []
            for element in elements:
                try:
                    # Get text from all cells
                    cells = element.find_elements(By.TAG_NAME, "td")
                    if cells:
                        row_data = [cell.text.strip() for cell in cells]
                        data.append(row_data)
                except Exception as e:
                    continue
            
            if data:
                # Create DataFrame
                df = pd.DataFrame(data)
                print(f"📊 Created DataFrame with {len(df)} rows")
                return df
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error processing elements: {e}")
            return None
    
    def is_la_data_table_2019(self, df):
        """Check if this table contains Los Angeles 2019 OES data"""
        try:
            # Check for expected columns in 2019 format
            expected_columns_2019 = [
                'occupation', 'employment', 'wage', 'location quotient', 'lq'
            ]
            
            columns_lower = [str(col).lower() for col in df.columns]
            
            # Check if any expected columns are present
            for expected in expected_columns_2019:
                if any(expected in col for col in columns_lower):
                    return True
            
            # Check if table has reasonable size (should have many rows)
            if len(df) > 100:
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking table: {e}")
            return False
    
    def save_page_source(self):
        """Save the page source for debugging"""
        try:
            page_source = self.driver.page_source
            output_file = os.path.join(self.data_dir, "bls_oes_2019_page_source.html")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(page_source)
            
            print(f"💾 Page source saved to {output_file}")
            
        except Exception as e:
            print(f"❌ Error saving page source: {e}")
    
    def take_screenshot(self):
        """Take a screenshot of the page"""
        try:
            screenshot_file = os.path.join(self.data_dir, "bls_oes_2019_screenshot.png")
            self.driver.save_screenshot(screenshot_file)
            print(f"📸 Screenshot saved to {screenshot_file}")
            
        except Exception as e:
            print(f"❌ Error taking screenshot: {e}")
    
    def get_oes_data(self):
        """Main method to get OES data"""
        print("🚀 Starting Selenium-based 2019 OES data extraction...")
        
        try:
            # Setup webdriver
            if not self.setup_driver():
                return None
            
            # Navigate to page
            if not self.navigate_to_oes_page():
                return None
            
            # Wait for data to load
            if not self.wait_for_data_to_load():
                print("⚠️  Data loading timeout, proceeding anyway...")
            
            # Save page source and screenshot for debugging
            self.save_page_source()
            self.take_screenshot()
            
            # Extract data
            data = self.extract_table_data()
            
            if data is None:
                # Try alternative extraction method
                print("🔄 Trying alternative data extraction method...")
                data = self.extract_data_from_elements()
            
            if data is not None:
                # Save the data
                output_file = os.path.join(self.data_dir, "la_oes_2019_selenium_data.csv")
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
        
        print("\n📊 ANALYZING EXTRACTED 2019 DATA")
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
    """Main function to run the 2019 Selenium scraper"""
    print("🚀 Selenium-based BLS OES 2019 Web Scraper")
    print("=" * 50)
    
    scraper = SeleniumBLSOESScraper2019()
    
    # Get OES data
    data = scraper.get_oes_data()
    
    if data is not None:
        # Analyze the data
        scraper.analyze_extracted_data(data)
        
        print(f"\n✅ Successfully extracted 2019 OES data!")
        print(f"📊 Data shape: {data.shape}")
        print(f"📋 Columns: {list(data.columns)}")
        
    else:
        print("\n❌ Could not extract 2019 OES data")
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