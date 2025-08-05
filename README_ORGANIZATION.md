# BLS API Project Organization

This folder contains the latest BLS (Bureau of Labor Statistics) data processing efforts using Selenium scrapers.

## Folder Structure

### `/scrapers/`
Contains the main Selenium-based web scrapers:
- `selenium_oes_scraper.py` - Latest Selenium scraper for OES data
- `bls_oes_web_scraper.py` - Alternative web scraper implementation
- `web_scraper_oes.py` - Additional scraper variant

### `/analysis/`
Contains analysis and processing scripts:
- `la_employment_analysis.py` - Los Angeles employment analysis
- `la_location_quotient_analysis.py` - Location quotient analysis
- `manual_oes_analysis.py` - Manual OES data analysis
- `working_employment_analysis.py` - Working employment analysis
- `explore_oes_series.py` - OES series exploration
- `example_oes_location_quotient.py` - Example location quotient analysis

### `/docs/`
Documentation and guides:
- `README.md` - Main project README
- `README_FINAL.md` - Final project documentation
- `manual_download_guide.md` - Manual download instructions
- `la_location_quotient_guide.md` - Location quotient guide
- `analysis_summary.md` - Analysis summary
- `research_methodology.md` - **Complete research methodology and technical approach**
- `analysis_results.md` - **Comprehensive analysis results and findings**

### `/data/`
Data files and visualizations:
- `employment_data_2020_2024.csv` - Employment data
- `employment_analysis_visualization.png` - Analysis visualization

### `/utils/`
Utility scripts and configuration:
- `bls_client.py` - BLS API client
- `test_bls_api.py` - API testing script
- `process_extracted_data.py` - Data processing utilities
- `requirements.txt` - Python dependencies
- `env_example.txt` - Environment variables example

### `/oes_data/`
OES-specific data files (existing folder)

### `/bls_data_download/`
BLS data download utilities (existing folder)

## Getting Started

1. **Start with the documentation**: 
   - `docs/research_methodology.md` - Complete technical methodology
   - `docs/analysis_results.md` - Key findings and insights
2. Check the `/docs/` folder for additional guides
3. The latest Selenium scraper is in `/scrapers/selenium_oes_scraper.py`
4. Configuration files are in `/utils/`
5. Analysis scripts are in `/analysis/` 