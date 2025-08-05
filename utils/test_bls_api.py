#!/usr/bin/env python3
"""
Test script to debug BLS API connection and explore available data
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_connection():
    """Test basic API connection"""
    api_key = os.getenv('BLS_API_KEY')
    if not api_key:
        print("❌ BLS_API_KEY not found in environment variables")
        return
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    # Test with a simple request
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    
    # Try with a known series ID (CPI for All Urban Consumers)
    payload = {
        "seriesid": ["CUUR0000SA0"],
        "startyear": "2023",
        "endyear": "2024",
        "registrationkey": api_key
    }
    
    headers = {
        'BLS-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        print("🔍 Testing API connection with CPI data...")
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📋 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API connection successful!")
            print(f"📈 Response keys: {list(data.keys())}")
            
            if 'Results' in data:
                print(f"📊 Results keys: {list(data['Results'].keys())}")
                if 'series' in data['Results']:
                    print(f"📈 Number of series: {len(data['Results']['series'])}")
                    if data['Results']['series']:
                        first_series = data['Results']['series'][0]
                        print(f"📋 First series ID: {first_series.get('seriesID', 'Unknown')}")
                        print(f"📊 Number of data points: {len(first_series.get('data', []))}")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"📋 Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def test_oes_survey():
    """Test OES survey endpoint"""
    api_key = os.getenv('BLS_API_KEY')
    if not api_key:
        print("❌ BLS_API_KEY not found in environment variables")
        return
    
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    
    # Try OES survey endpoint
    payload = {
        "survey": "OES",
        "startyear": "2023",
        "endyear": "2024",
        "registrationkey": api_key
    }
    
    headers = {
        'BLS-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        print("\n🔍 Testing OES survey endpoint...")
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OES survey request successful!")
            print(f"📈 Response structure: {json.dumps(data, indent=2)[:500]}...")
        else:
            print(f"❌ OES survey request failed with status {response.status_code}")
            print(f"📋 Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing OES survey: {e}")

def explore_available_series():
    """Explore what series are available"""
    print("\n🔍 Available BLS Series Types:")
    print("- CUUR0000SA0: CPI for All Urban Consumers")
    print("- CEU0000000001: Total Nonfarm Employment")
    print("- OES series: Occupational Employment Statistics")
    print("- For OES location quotients, you need specific series IDs")
    print("\n📚 To find OES series IDs:")
    print("1. Visit: https://data.bls.gov/PDQWeb/oe")
    print("2. Select 'Location Quotients'")
    print("3. Choose metropolitan areas and occupations")
    print("4. Note the series IDs from the generated data")

if __name__ == "__main__":
    print("🧪 BLS API Connection Test")
    print("=" * 40)
    
    test_api_connection()
    test_oes_survey()
    explore_available_series()
    
    print("\n" + "=" * 40)
    print("✅ Test completed!") 