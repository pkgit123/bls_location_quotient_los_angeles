# BLS API Exploration

This project explores the Bureau of Labor Statistics (BLS) API to retrieve Occupational Employment and Wage Statistics (OES) data, specifically location quotient data for metropolitan areas.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get BLS API Key

1. Visit [BLS Registration Page](https://data.bls.gov/registrationEngine/)
2. Register for a free API key
3. Copy your API key

### 3. Configure Environment

Create a `.env` file in the project root:

```bash
cp env_example.txt .env
```

Edit `.env` and add your API key:

```
BLS_API_KEY=your_actual_api_key_here
```

## Usage

### Basic Example

Run the sample script to fetch OES location quotient data:

```bash
python example_oes_location_quotient.py
```

### Using the BLS Client

```python
from bls_client import BLSClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client
client = BLSClient()

# Fetch data for specific series IDs
series_ids = ['OES12345678900000000000000000000000']
response = client.get_series_data(series_ids, 2020, 2023)

# Parse response to DataFrame
df = client.parse_series_response(response)
print(df.head())
```

## Data Sources

### OES Location Quotients

Location quotients measure the concentration of employment in an occupation relative to the national average:

- **Location Quotient > 1.0**: Higher concentration than national average
- **Location Quotient = 1.0**: Same concentration as national average  
- **Location Quotient < 1.0**: Lower concentration than national average

### Finding Series IDs

1. Visit [BLS OES Data](https://data.bls.gov/PDQWeb/oe)
2. Navigate to "Location Quotients" section
3. Select metropolitan areas and occupations
4. Note the series IDs from generated data

## API Limits

- **Rate Limit**: 500 requests per day
- **Series Limit**: 25 series per request
- **Year Range**: Up to 20 years per request

## Project Structure

```
bls_api/
├── bls_client.py              # Main API client class
├── example_oes_location_quotient.py  # Sample script
├── requirements.txt           # Python dependencies
├── env_example.txt           # Environment variables template
└── README.md                 # This file
```

## Resources

- [BLS API Documentation](https://www.bls.gov/developers/)
- [OES Data Homepage](https://www.bls.gov/oes/)
- [Location Quotients Guide](https://www.bls.gov/oes/oes_emp.htm)
- [API Registration](https://data.bls.gov/registrationEngine/)

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your API key is correctly set in `.env`
2. **Rate Limiting**: BLS limits to 500 requests per day
3. **Invalid Series ID**: Verify series IDs from BLS data portal
4. **Network Issues**: Check internet connectivity

### Getting Help

- Check BLS API documentation for latest changes
- Verify series IDs using BLS data portal
- Monitor API response for error messages 