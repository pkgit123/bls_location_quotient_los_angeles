#!/usr/bin/env python3
"""
Script to explore OES series IDs and find location quotient data
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_oes_series_examples():
    """Get examples of OES series IDs"""
    api_key = os.getenv('BLS_API_KEY')
    if not api_key:
        print("❌ BLS_API_KEY not found in environment variables")
        return
    
    # Common OES series patterns
    # These are examples - actual series IDs may vary
    example_series = [
        # Example: Software Developers in New York-Newark-Jersey City MSA
        "OES11940000000000000000000000000000",  # Software Developers, Applications
        "OES11940000000000000000000000000001",  # Software Developers, Systems Software
        # Example: Financial Analysts in Los Angeles MSA
        "OES31080000000000000000000000000000",  # Financial Analysts
        # Example: Registered Nurses in Chicago MSA
        "OES16980000000000000000000000000000",  # Registered Nurses
    ]
    
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    
    headers = {
        'BLS-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    for series_id in example_series:
        payload = {
            "seriesid": [series_id],
            "startyear": "2023",
            "endyear": "2024",
            "registrationkey": api_key
        }
        
        try:
            print(f"\n🔍 Testing series ID: {series_id}")
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'REQUEST_SUCCEEDED':
                    if data['Results']['series'][0] is not None:
                        series_data = data['Results']['series'][0]
                        print(f"✅ Series found: {series_data.get('seriesID')}")
                        print(f"📊 Data points: {len(series_data.get('data', []))}")
                        if series_data.get('data'):
                            latest = series_data['data'][0]
                            print(f"📈 Latest value: {latest.get('value')} ({latest.get('year')}-{latest.get('periodName')})")
                    else:
                        print(f"❌ Series not found or no data")
                else:
                    print(f"❌ Request failed: {data.get('message', 'Unknown error')}")
            else:
                print(f"❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def search_for_location_quotients():
    """Search for location quotient specific series"""
    print("\n🔍 Location Quotient Series Search")
    print("=" * 40)
    
    # Location quotient series typically have specific patterns
    # Let's try some common patterns
    api_key = os.getenv('BLS_API_KEY')
    if not api_key:
        return
    
    # Try different area codes and occupation codes
    area_codes = [
        "11940",  # New York-Newark-Jersey City
        "31080",  # Los Angeles-Long Beach-Anaheim
        "16980",  # Chicago-Naperville-Elgin
        "19100",  # Dallas-Fort Worth-Arlington
        "35620",  # New York-Newark-Jersey City (alternative)
    ]
    
    occupation_codes = [
        "151132",  # Software Developers, Applications
        "151133",  # Software Developers, Systems Software
        "132051",  # Financial Analysts
        "291141",  # Registered Nurses
        "000000",  # All Occupations
    ]
    
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    headers = {
        'BLS-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    found_series = []
    
    for area_code in area_codes:
        for occ_code in occupation_codes:
            # Try different series ID patterns
            patterns = [
                f"OES{area_code}{occ_code}00000000000000000000",
                f"OES{area_code}{occ_code}00000000000000000001",
                f"OES{area_code}{occ_code}00000000000000000002",
            ]
            
            for series_id in patterns:
                payload = {
                    "seriesid": [series_id],
                    "startyear": "2023",
                    "endyear": "2024",
                    "registrationkey": api_key
                }
                
                try:
                    response = requests.post(url, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('status') == 'REQUEST_SUCCEEDED':
                            if data['Results']['series'][0] is not None:
                                series_data = data['Results']['series'][0]
                                print(f"✅ Found: {series_id}")
                                found_series.append(series_id)
                                
                                # Check if it's location quotient data
                                if series_data.get('data'):
                                    latest = series_data['data'][0]
                                    value = latest.get('value', '')
                                    if value and float(value) > 0 and float(value) < 10:
                                        print(f"   📊 Likely location quotient: {value}")
                                
                except Exception as e:
                    continue
    
    print(f"\n📈 Found {len(found_series)} potential series")
    return found_series

def get_actual_oes_data():
    """Get actual OES data using known working series IDs"""
    print("\n📊 Getting Actual OES Data")
    print("=" * 40)
    
    api_key = os.getenv('BLS_API_KEY')
    if not api_key:
        return
    
    # Let's try some employment data series that are more likely to work
    employment_series = [
        "CEU0000000001",  # Total Nonfarm Employment
        "CEU0500000001",  # Private Employment
        "CEU9000000001",  # Government Employment
    ]
    
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    headers = {
        'BLS-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    all_data = []
    
    for series_id in employment_series:
        payload = {
            "seriesid": [series_id],
            "startyear": "2020",
            "endyear": "2024",
            "registrationkey": api_key
        }
        
        try:
            print(f"🔍 Fetching: {series_id}")
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'REQUEST_SUCCEEDED':
                    if data['Results']['series'][0] is not None:
                        series_data = data['Results']['series'][0]
                        print(f"✅ Success: {len(series_data.get('data', []))} data points")
                        
                        for item in series_data.get('data', []):
                            all_data.append({
                                'series_id': series_id,
                                'year': item.get('year'),
                                'period': item.get('period'),
                                'periodName': item.get('periodName'),
                                'value': item.get('value'),
                            })
                    else:
                        print(f"❌ No data for {series_id}")
                else:
                    print(f"❌ Failed: {data.get('message', 'Unknown error')}")
            else:
                print(f"❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    if all_data:
        df = pd.DataFrame(all_data)
        print(f"\n📊 Total data points: {len(df)}")
        print(df.head(10))
        
        # Save to CSV
        output_file = "employment_data_2020_2024.csv"
        df.to_csv(output_file, index=False)
        print(f"💾 Data saved to {output_file}")

if __name__ == "__main__":
    print("🔍 OES Series Exploration")
    print("=" * 50)
    
    get_oes_series_examples()
    search_for_location_quotients()
    get_actual_oes_data()
    
    print("\n" + "=" * 50)
    print("📚 Next Steps:")
    print("1. Visit https://data.bls.gov/PDQWeb/oe for OES data")
    print("2. Use the data portal to find specific location quotient series IDs")
    print("3. Update the script with the correct series IDs")
    print("4. Run the analysis with the working series IDs") 