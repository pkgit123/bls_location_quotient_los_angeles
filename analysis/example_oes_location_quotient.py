#!/usr/bin/env python3
"""
Sample script to pull BLS Occupational Employment and Wage Statistics (OES)
location quotient data for metropolitan areas over the past 10 years.

This script demonstrates how to:
1. Connect to the BLS API
2. Fetch OES survey data
3. Filter for location quotient data
4. Process and analyze the results
"""

import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from bls_client import BLSClient

# Load environment variables
load_dotenv()

def main():
    """Main function to demonstrate BLS OES location quotient data retrieval"""
    
    # Initialize BLS client
    try:
        client = BLSClient()
        print("✅ BLS client initialized successfully")
    except ValueError as e:
        print(f"❌ Error initializing BLS client: {e}")
        print("Please set your BLS_API_KEY environment variable or create a .env file")
        return
    
    # Calculate date range (past 10 years)
    current_year = datetime.now().year
    start_year = current_year - 10
    end_year = current_year
    
    print(f"📊 Fetching OES data from {start_year} to {end_year}")
    
    # Example: Fetch OES survey data
    # Note: The actual series IDs for location quotient data may need to be 
    # determined by exploring the BLS API documentation or data catalog
    try:
        print("🔍 Fetching OES survey data...")
        response = client.get_survey_data('OES', start_year, end_year)
        
        # Parse the response
        df = client.parse_series_response(response)
        
        if df.empty:
            print("⚠️  No data returned from API")
            return
        
        print(f"✅ Retrieved {len(df)} data points")
        print(f"📈 Data shape: {df.shape}")
        
        # Display sample data
        print("\n📋 Sample data:")
        print(df.head())
        
        # Filter for location quotient related data
        # This is a simplified filter - actual filtering logic may vary
        location_quotient_data = df[
            df['series_id'].str.contains('OES', na=False) & 
            df['series_id'].str.contains('00000000000000000000', na=False)
        ]
        
        print(f"\n🎯 Found {len(location_quotient_data)} location quotient data points")
        
        if not location_quotient_data.empty:
            print("\n📍 Location quotient sample data:")
            print(location_quotient_data.head())
            
            # Save to CSV
            output_file = f"oes_location_quotient_{start_year}_{end_year}.csv"
            location_quotient_data.to_csv(output_file, index=False)
            print(f"💾 Data saved to {output_file}")
        
        # Basic analysis
        print("\n📊 Basic analysis:")
        print(f"Unique series IDs: {df['series_id'].nunique()}")
        print(f"Year range: {df['year'].min()} - {df['year'].max()}")
        print(f"Available periods: {df['periodName'].unique()}")
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        print("This might be due to:")
        print("- Invalid API key")
        print("- Network connectivity issues")
        print("- API rate limiting")
        print("- Incorrect series ID format")

def explore_series_ids():
    """Helper function to explore available series IDs"""
    print("\n🔍 To find the correct series IDs for location quotient data:")
    print("1. Visit: https://data.bls.gov/PDQWeb/oe")
    print("2. Navigate to 'Location Quotients' section")
    print("3. Select metropolitan areas and occupations of interest")
    print("4. Note the series IDs from the generated data")
    print("\nExample series ID format for OES location quotient:")
    print("OES + Area Code + Occupation Code + 00000000000000000000")

if __name__ == "__main__":
    print("🚀 BLS OES Location Quotient Data Retrieval")
    print("=" * 50)
    
    main()
    
    print("\n" + "=" * 50)
    explore_series_ids()
    
    print("\n📚 Additional Resources:")
    print("- BLS API Documentation: https://www.bls.gov/developers/")
    print("- OES Data: https://www.bls.gov/oes/")
    print("- Location Quotients: https://www.bls.gov/oes/oes_emp.htm") 