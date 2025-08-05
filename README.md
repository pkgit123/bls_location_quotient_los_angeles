# BLS Location Quotient Analysis: Los Angeles (2019-2024)

A comprehensive analysis of occupational concentration patterns in the Los Angeles metropolitan area using Bureau of Labor Statistics (BLS) Occupational Employment Statistics (OES) data from 2019 to 2024.

## 🎯 Project Overview

This project analyzes Location Quotients (LQ) to identify which occupations are over- or under-represented in Los Angeles compared to national averages. The analysis reveals significant shifts in the region's occupational landscape over a 5-year period, with notable changes in entertainment, personal services, and technical occupations.

## 📊 Key Findings

### Overall Trends (2019-2024)
- **Total Occupations Analyzed**: 611 matched occupations
- **Mean LQ 2019**: 1.090 → **Mean LQ 2024**: 1.112 (+11.6% increase)
- **Distribution**: Nearly equal split between increasing (48.9%) and decreasing (49.4%) occupations

### Most Significant Changes
- **Biggest Increase**: Shampooers (0.380 → 4.250, +1018.4%)
- **Biggest Decrease**: Actors (7.810 → 2.490, -68.1%)
- **Emerging Strengths**: Personal services, technical writing, content creation
- **Declining Areas**: Traditional entertainment acting, environmental services

## 🏗️ Project Structure

```
bls_api/
├── scrapers/                    # Web scraping infrastructure
│   ├── selenium_oes_scraper.py           # 2024 data scraper
│   ├── selenium_oes_scraper_2019.py      # 2019 data scraper
│   └── oes_data_2019/                    # 2019 extracted data
├── analysis/                    # Analysis scripts
│   ├── la_location_quotient_analysis.py  # Location quotient analysis
│   ├── la_employment_analysis.py         # Employment analysis
│   └── working_employment_analysis.py    # Working analysis
├── utils/                       # Utility scripts
│   ├── process_extracted_data.py         # Data processing
│   ├── analyze_2019_data.py              # 2019 data analysis
│   ├── compare_2019_2024.py              # Comparative analysis
│   └── requirements.txt                  # Python dependencies
├── docs/                        # Documentation
│   ├── research_methodology.md           # Complete methodology
│   ├── analysis_results.md               # Comprehensive results
│   └── README_ORGANIZATION.md            # Project organization
└── oes_data/                    # 2024 processed data
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Chrome browser
- ChromeDriver

### Installation
```bash
# Clone the repository
git clone https://github.com/pkgit123/bls_location_quotient_los_angeles.git
cd bls_location_quotient_los_angeles

# Install dependencies
pip install -r utils/requirements.txt
```

### Running the Analysis
```bash
# Extract 2024 data
python scrapers/selenium_oes_scraper.py

# Process and analyze 2024 data
python utils/process_extracted_data.py

# Extract 2019 data
python scrapers/selenium_oes_scraper_2019.py

# Analyze 2019 data
python utils/analyze_2019_data.py

# Compare 2019-2024
python utils/compare_2019_2024.py
```

## 📚 Documentation

### Essential Reading
1. **[Research Methodology](docs/research_methodology.md)** - Complete technical approach and methodology
2. **[Analysis Results](docs/analysis_results.md)** - Comprehensive findings and insights
3. **[Occupational Growth Factors](docs/occupational_growth_factors.md)** - Deep dive into technical writers and textile workers growth
4. **[Project Organization](README_ORGANIZATION.md)** - Detailed project structure guide

### Additional Guides
- `docs/manual_download_guide.md` - Manual data download instructions
- `docs/la_location_quotient_guide.md` - Location quotient analysis guide
- `docs/analysis_summary.md` - Summary of analysis results

## 🔍 Key Insights

### Entertainment Industry Evolution
- **Actors**: Dramatic decline (-68.1%) suggests industry restructuring
- **Media & Communication**: Remains extremely strong (7.98 LQ)
- **Film & Video**: Still high concentration despite moderate decline

### Emerging Sectors
- **Personal Services**: Explosive growth in beauty and wellness
- **Technical Writing**: Massive growth (+342.5%) in content creation
- **Education**: Strong growth in postsecondary teaching

### Declining Areas
- **Environmental Services**: Significant decline across multiple roles
- **Legal Services**: Reduction in judicial support positions
- **Insurance Services**: Decline in specialized insurance roles

## 📈 Data Sources

- **2019 Data**: [BLS OES 2019 Los Angeles](https://www.bls.gov/oes/2019/may/oes_31080.htm)
- **2024 Data**: [BLS OES 2024 Los Angeles](https://data.bls.gov/oes/#/area/0031080)
- **Geographic Coverage**: Los Angeles-Long Beach-Anaheim, CA MSA
- **Data Period**: May 2019 and May 2024

## 🛠️ Technical Implementation

### Web Scraping
- **Tool**: Selenium WebDriver with Chrome
- **Approach**: Automated extraction with fallback methods
- **Data Formats**: Handles both static HTML (2019) and dynamic JavaScript (2024)

### Data Processing
- **Cleaning**: Automated removal of formatting artifacts
- **Validation**: Comprehensive data quality checks
- **Analysis**: Statistical analysis with concentration categorization

### Output Files
- Raw extracted data (CSV format)
- Cleaned and processed datasets
- Analysis results and reports
- Comparative analysis between years

## 📊 Statistical Categories

- **Very High Concentration**: LQ > 2.0
- **High Concentration**: 1.0 < LQ ≤ 2.0
- **Average Concentration**: 0.5 < LQ ≤ 1.0
- **Low Concentration**: LQ ≤ 0.5

## 🤝 Contributing

This project is open for contributions! Areas for improvement:
- Additional years of data analysis
- Geographic expansion to other regions
- Advanced analytics and visualization
- API integration when available
- Enhanced error handling and robustness

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Bureau of Labor Statistics (BLS) for providing the OES data
- Selenium community for web scraping tools
- Python ecosystem for data analysis capabilities

## 📞 Contact

For questions or contributions, please open an issue on GitHub or contact the project maintainer.

---

**Note**: This analysis provides valuable insights for workforce development, economic planning, and regional competitiveness strategies in Los Angeles. 