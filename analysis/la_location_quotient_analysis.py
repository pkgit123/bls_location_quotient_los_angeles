#!/usr/bin/env python3
"""
Los Angeles Metropolitan Area Location Quotient Analysis
Compare location quotients for all occupations between 2013 and 2023
"""

import os
import pandas as pd
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LALocationQuotientAnalyzer:
    """Analyzer for Los Angeles location quotient data"""
    
    def __init__(self):
        self.api_key = os.getenv('BLS_API_KEY')
        if not self.api_key:
            raise ValueError("BLS_API_KEY not found in environment variables")
        
        self.base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        self.la_area_code = "31080"  # Los Angeles-Long Beach-Anaheim MSA
        self.session = requests.Session()
        self.session.headers.update({
            'BLS-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def get_occupation_codes(self):
        """Get common occupation codes for analysis"""
        # Major occupation groups and specific occupations
        occupation_codes = {
            # Management Occupations
            "110000": "Management Occupations",
            "111000": "Chief Executives",
            "112000": "General and Operations Managers",
            "113000": "Advertising, Marketing, Promotions, Public Relations, and Sales Managers",
            
            # Business and Financial Operations
            "130000": "Business and Financial Operations Occupations",
            "132000": "Financial Analysts and Advisors",
            "133000": "Accountants and Auditors",
            
            # Computer and Mathematical
            "150000": "Computer and Mathematical Occupations",
            "151000": "Computer Occupations",
            "151132": "Software Developers, Applications",
            "151133": "Software Developers, Systems Software",
            "151134": "Software Quality Assurance Analysts and Testers",
            "151135": "Web Developers",
            "151136": "Web and Digital Interface Designers",
            
            # Architecture and Engineering
            "170000": "Architecture and Engineering Occupations",
            "171000": "Architects, Surveyors, and Cartographers",
            "172000": "Engineers",
            
            # Life, Physical, and Social Science
            "190000": "Life, Physical, and Social Science Occupations",
            "191000": "Life Scientists",
            "192000": "Physical Scientists",
            "193000": "Social Scientists and Related Workers",
            
            # Community and Social Service
            "210000": "Community and Social Service Occupations",
            "211000": "Counselors, Social Workers, and Other Community and Social Service Specialists",
            
            # Legal
            "230000": "Legal Occupations",
            "231000": "Lawyers, Judges, and Related Workers",
            
            # Education, Training, and Library
            "250000": "Education, Training, and Library Occupations",
            "251000": "Postsecondary Teachers",
            "252000": "Preschool, Primary, Secondary, and Special Education School Teachers",
            
            # Arts, Design, Entertainment, Sports, and Media
            "270000": "Arts, Design, Entertainment, Sports, and Media Occupations",
            "271000": "Artists and Related Workers",
            "272000": "Designers",
            "273000": "Actors, Producers, and Directors",
            "274000": "Athletes, Coaches, Umpires, and Related Workers",
            "275000": "Dancers and Choreographers",
            "276000": "Musicians, Singers, and Related Workers",
            "277000": "Entertainers and Performers, Sports and Related Workers, All Other",
            "279000": "Media and Communication Equipment Workers, All Other",
            
            # Healthcare Practitioners and Technical
            "290000": "Healthcare Practitioners and Technical Occupations",
            "291000": "Health Diagnosing and Treating Practitioners and Other Technical Occupations",
            "291141": "Registered Nurses",
            "291142": "Nurse Practitioners",
            "291143": "Physician Assistants",
            "291144": "Nurse Anesthetists",
            "291145": "Nurse Midwives",
            "291171": "Physicians and Surgeons, All Other",
            "291181": "Physicians, Pathologists",
            "291182": "Radiologists",
            "291183": "Cardiologists",
            "291184": "Endocrinologists",
            "291185": "Dermatologists",
            "291186": "Psychiatrists",
            "291187": "Neurologists",
            "291188": "Family Medicine Physicians",
            "291189": "Internists, General",
            "291191": "Surgeons",
            "291192": "Obstetricians and Gynecologists",
            "291193": "Pediatricians, General",
            "291194": "Anesthesiologists",
            "291195": "Emergency Medicine Physicians",
            "291196": "Psychiatrists",
            "291199": "Physicians and Surgeons, All Other",
            "292000": "Health Technologists and Technicians",
            "292021": "Medical and Clinical Laboratory Technicians",
            "292022": "Medical and Clinical Laboratory Technologists",
            "292023": "Cardiovascular Technologists and Technicians",
            "292024": "Diagnostic Medical Sonographers",
            "292025": "Nuclear Medicine Technologists",
            "292026": "Radiologic Technologists and Technicians",
            "292027": "Magnetic Resonance Imaging Technologists",
            "292029": "Diagnostic Related Technologists and Technicians, All Other",
            "292031": "Nuclear Medicine Technologists",
            "292032": "Radiologic Technologists and Technicians",
            "292033": "Magnetic Resonance Imaging Technologists",
            "292034": "Diagnostic Medical Sonographers",
            "292035": "Cardiovascular Technologists and Technicians",
            "292036": "Medical and Clinical Laboratory Technologists",
            "292037": "Medical and Clinical Laboratory Technicians",
            "292038": "Pharmacy Technicians",
            "292039": "Diagnostic Related Technologists and Technicians, All Other",
            
            # Healthcare Support
            "310000": "Healthcare Support Occupations",
            "311000": "Nursing, Psychiatric, and Home Health Aides",
            "312000": "Occupational Therapy and Physical Therapist Assistants and Aides",
            "313000": "Other Healthcare Support Occupations",
            
            # Protective Service
            "330000": "Protective Service Occupations",
            "331000": "Supervisors of Protective Service Workers",
            "332000": "Fire Fighting and Prevention Workers",
            "333000": "Law Enforcement Workers",
            
            # Food Preparation and Serving Related
            "350000": "Food Preparation and Serving Related Occupations",
            "351000": "Supervisors of Food Preparation and Serving Workers",
            "352000": "Cooks and Food Preparation Workers",
            "353000": "Food and Beverage Serving Workers",
            "354000": "Other Food Preparation and Serving Related Workers",
            
            # Building and Grounds Cleaning and Maintenance
            "370000": "Building and Grounds Cleaning and Maintenance Occupations",
            "371000": "Supervisors of Building and Grounds Cleaning and Maintenance Workers",
            "372000": "Building Cleaning and Pest Control Workers",
            "374000": "Grounds Maintenance Workers",
            
            # Personal Care and Service
            "390000": "Personal Care and Service Occupations",
            "391000": "Supervisors of Personal Care and Service Workers",
            "392000": "Animal Care and Service Workers",
            "393000": "Entertainment Attendants and Related Workers",
            "394000": "Funeral Service Workers",
            "395000": "Personal Appearance Workers",
            "396000": "Baggage Porters, Bellhops, and Concierges",
            "397000": "Tour and Travel Guides",
            "399000": "Personal Care and Service Workers, All Other",
            
            # Sales and Related
            "410000": "Sales and Related Occupations",
            "411000": "Supervisors of Sales Workers",
            "412000": "Retail Sales Workers",
            "413000": "Sales Representatives, Services",
            "414000": "Sales Representatives, Wholesale and Manufacturing",
            "415000": "Sales Representatives, Wholesale and Manufacturing, Technical and Scientific Products",
            "416000": "Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific Products",
            "419000": "Sales and Related Workers, All Other",
            
            # Office and Administrative Support
            "430000": "Office and Administrative Support Occupations",
            "431000": "Supervisors of Office and Administrative Support Workers",
            "432000": "Communications Equipment Operators",
            "433000": "Financial Clerks",
            "434000": "Information and Record Clerks",
            "435000": "Material Recording, Scheduling, Dispatching, and Distributing Workers",
            "436000": "Secretaries and Administrative Assistants",
            "439000": "Office and Administrative Support Workers, All Other",
            
            # Farming, Fishing, and Forestry
            "450000": "Farming, Fishing, and Forestry Occupations",
            "451000": "Supervisors of Farming, Fishing, and Forestry Workers",
            "452000": "Agricultural Workers",
            "453000": "Fishing and Hunting Workers",
            "454000": "Forest, Conservation, and Logging Workers",
            
            # Construction and Extraction
            "470000": "Construction and Extraction Occupations",
            "471000": "Supervisors of Construction and Extraction Workers",
            "472000": "Construction Trades Workers",
            "473000": "Helpers, Construction Trades",
            "474000": "Other Construction and Related Workers",
            "475000": "Extraction Workers",
            
            # Installation, Maintenance, and Repair
            "490000": "Installation, Maintenance, and Repair Occupations",
            "491000": "Supervisors of Installation, Maintenance, and Repair Workers",
            "492000": "Electrical and Electronic Equipment Mechanics, Installers, and Repairers",
            "493000": "Vehicle and Mobile Equipment Mechanics, Installers, and Repairers",
            "499000": "Other Installation, Maintenance, and Repair Workers",
            
            # Production
            "510000": "Production Occupations",
            "511000": "Supervisors of Production Workers",
            "512000": "Assemblers and Fabricators",
            "513000": "Food Processing Workers",
            "514000": "Metal Workers and Plastic Workers",
            "515000": "Printing Workers",
            "516000": "Textile, Apparel, and Furnishings Workers",
            "517000": "Woodworkers",
            "518000": "Plant and System Operators",
            "519000": "Other Production Workers",
            
            # Transportation and Material Moving
            "530000": "Transportation and Material Moving Occupations",
            "531000": "Supervisors of Transportation and Material Moving Workers",
            "532000": "Air Transportation Workers",
            "533000": "Motor Vehicle Operators",
            "534000": "Rail Transportation Workers",
            "535000": "Water Transportation Workers",
            "536000": "Other Transportation Workers",
            "537000": "Material Moving Workers",
            
            # Military Specific Occupations
            "550000": "Military Specific Occupations",
            "551000": "Military Officer Special and Tactical Operations Leaders",
            "552000": "First-Line Enlisted Military Supervisors",
            "553000": "Military Enlisted Tactical Operations and Air/Weapons Specialists and Crew Members",
        }
        
        return occupation_codes
    
    def generate_series_id(self, occupation_code):
        """Generate OES series ID for location quotient"""
        # Format: OES + Area Code + Occupation Code + 00000000000000000000
        return f"OES{self.la_area_code}{occupation_code}00000000000000000000"
    
    def fetch_location_quotient_data(self, occupation_code, start_year=2013, end_year=2023):
        """Fetch location quotient data for a specific occupation"""
        series_id = self.generate_series_id(occupation_code)
        
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
                    return series_data.get('data', [])
            
            return []
            
        except Exception as e:
            print(f"Error fetching data for {occupation_code}: {e}")
            return []
    
    def analyze_location_quotient_changes(self):
        """Analyze location quotient changes from 2013 to 2023"""
        print("🔍 Analyzing Los Angeles Location Quotient Changes (2013-2023)")
        print("=" * 70)
        
        occupation_codes = self.get_occupation_codes()
        results = []
        
        total_occupations = len(occupation_codes)
        print(f"📊 Analyzing {total_occupations} occupations...")
        
        for i, (code, description) in enumerate(occupation_codes.items(), 1):
            print(f"Progress: {i}/{total_occupations} - {description}")
            
            data = self.fetch_location_quotient_data(code)
            
            if data:
                # Find 2013 and 2023 data points
                data_2013 = None
                data_2023 = None
                
                for item in data:
                    year = int(item.get('year', 0))
                    if year == 2013:
                        data_2013 = item
                    elif year == 2023:
                        data_2023 = item
                
                if data_2013 and data_2023:
                    try:
                        lq_2013 = float(data_2013.get('value', 0))
                        lq_2023 = float(data_2023.get('value', 0))
                        
                        change = lq_2023 - lq_2013
                        percent_change = ((lq_2023 - lq_2013) / lq_2013) * 100 if lq_2013 > 0 else 0
                        
                        results.append({
                            'occupation_code': code,
                            'description': description,
                            'lq_2013': lq_2013,
                            'lq_2023': lq_2023,
                            'change': change,
                            'percent_change': percent_change
                        })
                        
                    except (ValueError, TypeError):
                        continue
            
            # Rate limiting - pause between requests
            time.sleep(0.1)
        
        return results
    
    def rank_changes(self, results):
        """Rank occupations by location quotient changes"""
        if not results:
            print("❌ No data found for analysis")
            return
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(results)
        
        # Sort by absolute change (biggest changes first)
        df_sorted_by_change = df.sort_values('change', key=abs, ascending=False)
        
        # Sort by percent change
        df_sorted_by_percent = df.sort_values('percent_change', key=abs, ascending=False)
        
        print(f"\n📈 Analysis Complete: {len(df)} occupations with data")
        print("=" * 70)
        
        # Show biggest absolute changes
        print("\n🏆 BIGGEST ABSOLUTE CHANGES IN LOCATION QUOTIENT (2013-2023)")
        print("-" * 70)
        print(f"{'Rank':<4} {'Occupation':<50} {'2013':<8} {'2023':<8} {'Change':<8} {'% Change':<10}")
        print("-" * 70)
        
        for i, (_, row) in enumerate(df_sorted_by_change.head(20).iterrows(), 1):
            change_symbol = "+" if row['change'] > 0 else ""
            percent_symbol = "+" if row['percent_change'] > 0 else ""
            print(f"{i:<4} {row['description'][:49]:<50} {row['lq_2013']:<8.2f} {row['lq_2023']:<8.2f} {change_symbol}{row['change']:<7.2f} {percent_symbol}{row['percent_change']:<9.1f}%")
        
        # Show biggest percent changes
        print(f"\n📊 BIGGEST PERCENTAGE CHANGES IN LOCATION QUOTIENT (2013-2023)")
        print("-" * 70)
        print(f"{'Rank':<4} {'Occupation':<50} {'2013':<8} {'2023':<8} {'Change':<8} {'% Change':<10}")
        print("-" * 70)
        
        for i, (_, row) in enumerate(df_sorted_by_percent.head(20).iterrows(), 1):
            change_symbol = "+" if row['change'] > 0 else ""
            percent_symbol = "+" if row['percent_change'] > 0 else ""
            print(f"{i:<4} {row['description'][:49]:<50} {row['lq_2013']:<8.2f} {row['lq_2023']:<8.2f} {change_symbol}{row['change']:<7.2f} {percent_symbol}{row['percent_change']:<9.1f}%")
        
        # Save results
        output_file = "la_location_quotient_changes_2013_2023.csv"
        df.to_csv(output_file, index=False)
        print(f"\n💾 Complete results saved to {output_file}")
        
        return df

def main():
    """Main function to run the analysis"""
    try:
        analyzer = LALocationQuotientAnalyzer()
        results = analyzer.analyze_location_quotient_changes()
        df = analyzer.rank_changes(results)
        
        if df is not None and not df.empty:
            print(f"\n✅ Analysis completed successfully!")
            print(f"📊 Analyzed {len(df)} occupations in Los Angeles MSA")
            print(f"📈 Data covers 2013-2023 period")
        else:
            print("\n❌ No location quotient data found")
            print("This may be because:")
            print("- OES location quotient data is not available through the API")
            print("- Different series ID format is needed")
            print("- Data is only available through the BLS data portal")
            
    except Exception as e:
        print(f"❌ Error running analysis: {e}")

if __name__ == "__main__":
    main() 