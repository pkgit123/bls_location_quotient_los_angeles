# Research and Analysis Methodology: Los Angeles Location Quotient Analysis (2019-2024)

## Project Overview

This document outlines the methodology used to analyze Los Angeles occupational concentration patterns using Bureau of Labor Statistics (BLS) Occupational Employment Statistics (OES) data from 2019 to 2024. The analysis focuses on Location Quotients (LQ) to identify which occupations are over- or under-represented in the Los Angeles metropolitan area compared to national averages.

## Research Objectives

1. **Extract Location Quotient Data**: Gather comprehensive occupational data for Los Angeles from BLS OES datasets
2. **Temporal Comparison**: Compare occupational concentrations between 2019 and 2024 to identify trends
3. **Identify Specializations**: Determine which occupations show high concentration in Los Angeles
4. **Track Changes**: Analyze how occupational concentrations have evolved over the 5-year period

## Data Sources

### Primary Data Source
- **Bureau of Labor Statistics (BLS) Occupational Employment Statistics (OES)**
- **2019 Data**: https://www.bls.gov/oes/2019/may/oes_31080.htm
- **2024 Data**: https://data.bls.gov/oes/#/area/0031080
- **Geographic Coverage**: Los Angeles-Long Beach-Anaheim, CA Metropolitan Statistical Area (MSA)
- **Data Period**: May 2019 and May 2024

### Data Format Differences
- **2019 Format**: Static HTML table with 757 occupations, 11 columns
- **2024 Format**: Dynamic JavaScript-based interface with 749 occupations, 18 columns

## Methodology

### Phase 1: Data Extraction

#### 1.1 Web Scraping Setup
- **Tool**: Selenium WebDriver with Chrome browser
- **Configuration**: Headless mode for automated extraction
- **User Agent**: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36

#### 1.2 2019 Data Extraction
```python
# Key Parameters
URL: "https://www.bls.gov/oes/2019/may/oes_31080.htm"
Data Format: Static HTML table
Extraction Method: Direct table parsing
Output: 757 occupations × 11 columns
```

**Process Steps:**
1. Navigate to 2019 BLS OES page
2. Wait for page load (5 seconds)
3. Extract all HTML tables using `pd.read_html()`
4. Identify main data table (largest table with occupation data)
5. Save raw data to CSV format

#### 1.3 2024 Data Extraction
```python
# Key Parameters
URL: "https://data.bls.gov/oes/#/area/0031080"
Data Format: JavaScript-rendered dynamic content
Extraction Method: Selenium with element waiting
Output: 749 occupations × 18 columns
```

**Process Steps:**
1. Navigate to 2024 BLS OES query system
2. Wait for JavaScript content to load (30 seconds timeout)
3. Extract table data using multiple selectors
4. Handle dynamic content rendering
5. Save raw data and page source for debugging

### Phase 2: Data Cleaning and Processing

#### 2.1 Data Structure Analysis
- **2019 Data**: 757 occupations, clean Location Quotient values
- **2024 Data**: 749 occupations, Location Quotient values with "()  " prefix

#### 2.2 Data Cleaning Procedures

**For 2019 Data:**
```python
# Location Quotient Cleaning
df['Location quotient'] = pd.to_numeric(df['Location quotient'], errors='coerce')

# Occupation Name Cleaning
df['Occupation_clean'] = df['Occupation title'].str.replace(
    r'\(click on the occupation title to view its profile\)', '', regex=True
).str.strip()
```

**For 2024 Data:**
```python
# Location Quotient Cleaning (Remove "()  " prefix)
df['Location Quotient  ()'] = df['Location Quotient  ()'].astype(str).str.replace(
    r'\(\)\s*', '', regex=True
)
df['Location Quotient  ()'] = pd.to_numeric(df['Location Quotient  ()'], errors='coerce')

# Occupation Name Cleaning
df['Occupation_clean'] = df['Occupation (SOC code)'].str.replace(
    r'\(\d+-\d+\)', '', regex=True
).str.strip()
```

#### 2.3 Data Validation
- Remove completely empty rows
- Filter out header rows containing column names
- Validate numeric Location Quotient values
- Check for data completeness and consistency

### Phase 3: Statistical Analysis

#### 3.1 Descriptive Statistics
```python
# Calculate for each dataset
- Count of valid observations
- Mean Location Quotient
- Median Location Quotient
- Standard deviation
- Minimum and maximum values
- Distribution by concentration categories
```

#### 3.2 Concentration Categories
- **Very High Concentration**: LQ > 2.0
- **High Concentration**: 1.0 < LQ ≤ 2.0
- **Average Concentration**: 0.5 < LQ ≤ 1.0
- **Low Concentration**: LQ ≤ 0.5

#### 3.3 Ranking Analysis
- Rank occupations by Location Quotient (highest to lowest)
- Identify top 10 and bottom 10 occupations
- Calculate percentile rankings

### Phase 4: Comparative Analysis

#### 4.1 Occupation Matching
```python
# Matching Strategy
1. Clean occupation names (remove SOC codes, formatting)
2. Convert to lowercase for comparison
3. Find intersection of occupation sets
4. Create merged dataset with 2019 and 2024 values
```

**Results:**
- **Total 2019 Occupations**: 757
- **Total 2024 Occupations**: 749
- **Common Occupations**: 670
- **Matched for Analysis**: 611

#### 4.2 Change Calculations
```python
# Absolute Change
Change = LQ_2024 - LQ_2019

# Percentage Change
Percent_Change = ((LQ_2024 - LQ_2019) / LQ_2019) * 100
```

#### 4.3 Trend Analysis
- Identify occupations with largest increases/decreases
- Calculate mean changes across all occupations
- Analyze distribution of changes (increased vs decreased)
- Identify emerging and declining occupational concentrations

### Phase 5: Data Quality Assurance

#### 5.1 Validation Checks
- **Data Completeness**: Ensure all required fields are present
- **Value Ranges**: Verify Location Quotients are within expected ranges (0-15)
- **Consistency**: Check for logical relationships between employment and LQ values
- **Outlier Detection**: Identify and investigate extreme values

#### 5.2 Error Handling
- **Missing Data**: Handle NaN values appropriately
- **Format Errors**: Clean inconsistent data formats
- **Extraction Failures**: Implement fallback extraction methods
- **Processing Errors**: Log and handle exceptions gracefully

## Technical Implementation

### Software Stack
- **Python 3.x**: Primary programming language
- **Selenium WebDriver**: Web scraping automation
- **Pandas**: Data manipulation and analysis
- **Chrome Browser**: Web rendering engine
- **Regular Expressions**: Text cleaning and pattern matching

### File Organization
```
bls_api/
├── scrapers/
│   ├── selenium_oes_scraper.py (2024 data)
│   ├── selenium_oes_scraper_2019.py (2019 data)
│   └── oes_data_2019/ (2019 extracted data)
├── utils/
│   ├── process_extracted_data.py (2024 processing)
│   ├── analyze_2019_data.py (2019 analysis)
│   └── compare_2019_2024.py (comparative analysis)
├── oes_data/ (2024 processed data)
└── docs/ (documentation)
```

### Output Files Generated
1. **Raw Data**: `la_oes_selenium_data.csv` (2024), `la_oes_2019_selenium_data.csv` (2019)
2. **Cleaned Data**: `la_oes_cleaned_data.csv` (2024), processed 2019 data
3. **Analysis Results**: `la_oes_analysis_results.csv` (2024), `la_oes_2019_analysis_results.csv` (2019)
4. **Ranked Reports**: `la_location_quotient_report.csv` (2024), `la_location_quotient_2019_report.csv` (2019)
5. **Comparison Results**: `la_location_quotient_comparison_2019_2024.csv`

## Limitations and Considerations

### Data Limitations
- **Sample Size**: Limited to occupations with sufficient employment for statistical reliability
- **Geographic Scope**: Analysis limited to Los Angeles MSA
- **Time Period**: Comparison limited to 2019-2024 period
- **Data Availability**: Dependent on BLS data release schedules

### Methodological Limitations
- **Web Scraping**: Subject to website structure changes
- **Occupation Matching**: Some occupations may not match perfectly between years
- **Data Quality**: Relies on BLS data accuracy and completeness
- **Causality**: Correlation does not imply causation

### Technical Limitations
- **Browser Dependencies**: Requires Chrome browser and chromedriver
- **Network Dependencies**: Requires stable internet connection
- **Processing Time**: Web scraping can be time-intensive
- **Error Handling**: Limited to known error patterns

## Future Enhancements

### Potential Improvements
1. **Automated Scheduling**: Regular data updates
2. **Additional Years**: Extend analysis to more historical data
3. **Geographic Expansion**: Include other metropolitan areas
4. **Advanced Analytics**: Machine learning for trend prediction
5. **Interactive Visualization**: Web-based dashboard
6. **API Integration**: Direct BLS API access when available

### Scalability Considerations
- **Parallel Processing**: Multiple browser instances for faster extraction
- **Database Storage**: Move from CSV to database for larger datasets
- **Cloud Deployment**: Web-based scraping infrastructure
- **Caching**: Store intermediate results to reduce processing time

## Conclusion

This methodology provides a comprehensive framework for extracting, cleaning, and analyzing BLS OES Location Quotient data. The approach combines automated web scraping with robust data processing to enable meaningful temporal comparisons of occupational concentrations in the Los Angeles metropolitan area.

The methodology is designed to be reproducible, scalable, and adaptable to future data releases and research needs. By following this systematic approach, we can reliably track changes in regional occupational specializations over time and provide valuable insights for economic development and workforce planning. 