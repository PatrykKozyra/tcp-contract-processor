# TCP Contract Processor

An AI-powered system for extracting and managing Time Charter Party contract data with both web UI and command-line interfaces.

## Features

- **🌐 Web Interface**: Modern Streamlit UI with drag-and-drop file upload
- **💻 Command-Line Interface**: Full-featured CLI for automation and scripting
- **🤖 AI-Powered Extraction**: Uses Claude AI to extract 40+ structured fields from contracts
- **📊 Data Standardization**: Automatic normalization of dates (ISO format), vessel names, currency values
- **🔍 Vessel Search**: Query contracts by vessel name with partial matching
- **📥 Excel/CSV Export**: Export data in multiple formats for analysis
- **📦 Batch Processing**: Process multiple contracts simultaneously
- **💰 Cost Tracking**: Real-time API usage and cost monitoring
- **🔄 Retry Logic**: Automatic retry with exponential backoff for reliability
- **📄 Multiple PDF Layouts**: Handles different document formats and fonts

## Quick Start

### 1. Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/tcp-contract-processor.git
cd tcp-contract-processor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate.bat
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up API key
echo ANTHROPIC_API_KEY=your_api_key_here > .env
```

Get your API key from: https://console.anthropic.com/

### 2. Run the Web Interface

```bash
streamlit run streamlit_app.py
```

Opens at `http://localhost:8501` with features:
- Upload PDF contracts (single or multiple)
- Search contracts by vessel name
- View detailed contract information
- Download as Excel or CSV

### 3. Or Use the Command-Line Interface

```bash
# Interactive menu
python tcp_cli.py

# Process single contract
python tcp_cli.py --process tcp_contract_001.pdf

# Process all contracts
python tcp_cli.py --process-all

# Query by vessel name
python tcp_cli.py --query "Pacific Star"

# Export to Excel
python tcp_cli.py --export contracts.xlsx
```

## Project Structure

```
tcp-contract-processor/
├── streamlit_app.py           # Web UI application
├── tcp_cli.py                 # Command-line interface
├── generate_pdfs.py           # Generate sample contracts
├── src/
│   ├── main.py                # Core processing functions
│   └── data_standardization.py  # Data standardization layer
├── sample_contracts/          # Input PDF files
│   ├── tcp_contract_001.pdf   # Bulk Carrier
│   ├── tcp_contract_002.pdf   # Product Tanker
│   └── tcp_contract_003.pdf   # Container Feeder
├── output/                    # Exported Excel/CSV files
├── requirements.txt           # Python dependencies
├── .env                       # API key (not in git)
├── .gitignore                 # Git ignore rules
└── docs/
    ├── SETUP_GUIDE.md         # Detailed setup instructions
    ├── STREAMLIT_GUIDE.md     # Web UI guide
    └── CLI_README.md          # CLI documentation
```

## Extracted Data Fields

The system extracts 33 fields from each contract:

### Contract Information
- Contract Number
- Contract Date

### Vessel Particulars
- Vessel Name
- IMO Number
- Vessel Flag
- Year Built
- Vessel Type
- Deadweight
- Gross Tonnage
- Speed About
- Consumption Per Day

### Parties
- Owner Name
- Owner Location
- Charterer Name
- Charterer Location

### Charter Terms
- Charter Period (Months)
- Charter Period Description
- Daily Hire Rate (USD)
- Delivery Date
- Delivery Port
- Redelivery Port

### Bunkers
- Bunkers Delivery IFO
- Bunkers Delivery MGO
- Bunkers Redelivery IFO
- Bunkers Redelivery MGO

### Technical Details
- Last Special Survey
- Next Special Survey
- Drydocking Policy
- Off-Hire Threshold Hours

### Legal & Commercial
- Trading Limits
- Law and Arbitration
- Commission Rate
- Additional Notes

## Output Format

### Excel Format
Simple two-column table:
```
| Field                    | Value                |
|--------------------------|----------------------|
| Contract Number          | TCP-2024-001        |
| Vessel Name              | MV NORTHERN STAR    |
| Daily Hire Rate Usd      | 18500               |
| ...                      | ...                 |
```

### CSV Format
The Excel files can be easily converted to CSV:
```csv
Field,Value
Contract Number,TCP-2024-001
Vessel Name,MV NORTHERN STAR
Daily Hire Rate Usd,18500
...
```

## Sample Contracts

Three realistic mock contracts are included:

1. **tcp_contract_001.pdf** - Bulk Carrier (82,500 DWT)
   - 24-month charter at USD 18,500/day
   - Traditional formal layout (Times Roman font)

2. **tcp_contract_002.pdf** - Product Tanker (49,999 DWT)
   - 36-month charter at USD 22,750/day
   - Modern business layout (Helvetica font)

3. **tcp_contract_003.pdf** - Container Feeder (1,740 TEU)
   - 18-month charter at USD 11,850/day
   - Compact professional layout (Courier font)

## Testing

### Test PDF Extraction Only
```bash
python test_extraction.py
```

### Test Complete Pipeline
```bash
python test_full_pipeline.py
```

### Verify Excel Format and CSV Conversion
```bash
python verify_excel_format.py
```

## Technical Details

### Libraries Used
- **anthropic**: Claude AI API client
- **pdfplumber**: PDF text extraction
- **pandas**: Data manipulation
- **openpyxl**: Excel file creation
- **python-dotenv**: Environment variable management

### PDF Extraction Features
- Multi-page support with page markers
- Handles different fonts and layouts
- Cleans excessive whitespace
- Proper error handling

### AI Extraction Features
- Structured JSON output
- 33+ predefined fields
- Handles missing data gracefully
- Markdown code block parsing

### Excel Export Features
- Simple two-column format (Field | Value)
- No formatting (raw data table)
- Easy CSV conversion
- Preserves all extracted information

## API Costs

Using Claude Sonnet 4:
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens

Approximate cost per contract:
- 6,000-12,000 characters = ~1,500-3,000 input tokens
- Response = ~500-800 output tokens
- **Cost per contract: ~$0.01-0.02**

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Ensure `.env` file exists in project root
- Check that API key is correctly set in `.env`

### PDF text extraction fails
- Verify PDF is not password-protected
- Check PDF contains actual text (not just images)

### JSON parsing errors
- The code handles markdown code blocks automatically
- If issues persist, check Claude API response format

### Unicode errors on Windows
- The test scripts use ASCII-compatible output for Windows console
- Actual data processing handles Unicode correctly

## Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Step-by-step setup instructions with troubleshooting
- **[STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)** - Complete web UI user guide
- **[CLI_README.md](CLI_README.md)** - Command-line interface documentation
- **[COST_GUIDE.md](COST_GUIDE.md)** - API cost tracking and optimization
- **[STANDARDIZATION_GUIDE.md](STANDARDIZATION_GUIDE.md)** - Data standardization details

## Sample Contracts

Three realistic mock contracts are included:

1. **tcp_contract_001.pdf** - Bulk Carrier (82,500 DWT)
   - 24-month charter at USD 18,500/day
   - Traditional formal layout

2. **tcp_contract_002.pdf** - Product Tanker (49,999 DWT)
   - 36-month charter at USD 22,750/day
   - Modern business layout

3. **tcp_contract_003.pdf** - Container Feeder (1,740 TEU)
   - 18-month charter at USD 11,850/day
   - Compact professional layout

Generate new samples: `python generate_pdfs.py`

## Technology Stack

- **AI**: Anthropic Claude Sonnet 4.5
- **Web UI**: Streamlit
- **PDF Processing**: pdfplumber
- **Data Processing**: pandas, openpyxl
- **Python**: 3.8+

## Cost Estimation

Using Claude Sonnet 4:
- **Cost per contract**: ~$0.01-0.05
- **Input tokens**: ~1,500-3,000 per contract
- **Output tokens**: ~500-800 per contract

See [COST_GUIDE.md](COST_GUIDE.md) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Support

For issues or questions:
- Check the [SETUP_GUIDE.md](SETUP_GUIDE.md) for troubleshooting
- Review error messages in console/web UI
- Verify API key and internet connection
- Ensure all dependencies are installed
