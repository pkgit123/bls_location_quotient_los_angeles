import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

class BLSClient:
    """Client for interacting with the Bureau of Labor Statistics API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize BLS client
        
        Args:
            api_key: BLS API key. If not provided, will try to get from BLS_API_KEY env var
        """
        self.api_key = api_key or os.getenv('BLS_API_KEY')
        if not self.api_key:
            raise ValueError("BLS API key is required. Set BLS_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = "https://api.bls.gov/publicAPI/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'BLS-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def get_series_data(self, series_ids: List[str], start_year: int, end_year: int) -> Dict:
        """
        Fetch data for multiple series IDs
        
        Args:
            series_ids: List of BLS series IDs
            start_year: Start year for data
            end_year: End year for data
            
        Returns:
            Dictionary containing the API response
        """
        payload = {
            "seriesid": series_ids,
            "startyear": str(start_year),
            "endyear": str(end_year),
            "registrationkey": self.api_key
        }
        
        response = self.session.post(f"{self.base_url}/timeseries/data/", json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def get_survey_data(self, survey_abbreviation: str, start_year: int, end_year: int) -> Dict:
        """
        Fetch data for a specific survey
        
        Args:
            survey_abbreviation: Survey abbreviation (e.g., 'OES' for Occupational Employment Statistics)
            start_year: Start year for data
            end_year: End year for data
            
        Returns:
            Dictionary containing the API response
        """
        payload = {
            "survey": survey_abbreviation,
            "startyear": str(start_year),
            "endyear": str(end_year),
            "registrationkey": self.api_key
        }
        
        response = self.session.post(f"{self.base_url}/timeseries/data/", json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def parse_series_response(self, response: Dict) -> pd.DataFrame:
        """
        Parse BLS API response into a pandas DataFrame
        
        Args:
            response: API response dictionary
            
        Returns:
            DataFrame with the parsed data
        """
        data_list = []
        
        if 'Results' not in response or 'series' not in response['Results']:
            print("No data found in response")
            return pd.DataFrame()
        
        for series in response['Results']['series']:
            series_id = series.get('seriesID', 'Unknown')
            
            for item in series.get('data', []):
                row = {
                    'series_id': series_id,
                    'year': item.get('year'),
                    'period': item.get('period'),
                    'periodName': item.get('periodName'),
                    'value': item.get('value'),
                    'footnotes': [note.get('text', '') for note in item.get('footnotes', [])]
                }
                data_list.append(row)
        
        return pd.DataFrame(data_list)
    
    def get_location_quotient_series(self, area_code: str, occupation_code: str) -> str:
        """
        Generate series ID for location quotient data
        
        Args:
            area_code: Metropolitan area code
            occupation_code: Occupation code
            
        Returns:
            Series ID for location quotient
        """
        # Format: OES + area_code + occupation_code + 00000000000000000000
        # For location quotient, we need to identify the correct series ID format
        # This is a simplified example - actual series IDs may vary
        return f"OES{area_code}{occupation_code}00000000000000000000" 