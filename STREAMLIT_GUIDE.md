# TCP Contract Processor - Streamlit Web UI Guide

A simple and intuitive web interface for processing Time Charter Party contracts using AI.

## Quick Start

### Installation

1. Install Streamlit (if not already installed):
```bash
pip install streamlit
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your `.env` file contains your Anthropic API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

### Running the App

Start the Streamlit web server:

```bash
streamlit run streamlit_app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## Features Overview

### 1. File Upload Widget
- **Location:** "Upload & Process" tab
- **Functionality:**
  - Upload single or multiple PDF files
  - Supports drag-and-drop
  - Shows number of selected files
  - Accepts only `.pdf` format

### 2. Process Contracts Button
- **Location:** Below file upload widget
- **Functionality:**
  - Processes all selected PDFs
  - Shows real-time progress bar
  - Displays success/failure for each file
  - Shows vessel name after successful extraction
  - Stores contracts in session memory

### 3. Vessel Name Search
- **Location:** "View & Search" tab
- **Functionality:**
  - Real-time search as you type
  - Case-insensitive partial matching
  - Automatically filters the data table
  - Results sorted by contract date (descending)

### 4. Data Table Display
- **Location:** "View & Search" tab
- **Functionality:**
  - Shows all processed contracts
  - Two viewing modes:
    - **Compact:** Shows key fields only
    - **Show all fields:** Displays all extracted data
  - Interactive and scrollable
  - Responsive to search queries

### 5. Excel Download Button
- **Location:** "View & Search" tab, Export Data section
- **Functionality:**
  - Downloads filtered contracts as Excel
  - Auto-generated filename with timestamp
  - One-click download
  - Also includes CSV download option

## User Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│  Sidebar                │  Main Content Area            │
│  ─────────              │  ─────────────────            │
│  About                  │                               │
│  Statistics             │  Tab 1: Upload & Process      │
│  - Total Contracts      │  - File uploader              │
│  - Unique Vessels       │  - Process button             │
│  Clear All Button       │  - Progress display           │
│                         │                               │
│                         │  Tab 2: View & Search         │
│                         │  - Search bar                 │
│                         │  - Data table                 │
│                         │  - Download buttons           │
│                         │  - Detailed contract view     │
└─────────────────────────────────────────────────────────┘
```

## Workflow Examples

### Example 1: Process and View Single Contract

1. Open the app: `streamlit run streamlit_app.py`
2. Go to "Upload & Process" tab
3. Click "Browse files" and select `tcp_contract_001.pdf`
4. Click "🚀 Process Contracts"
5. Wait for processing (shows progress and result)
6. Go to "View & Search" tab
7. See the contract in the data table
8. Click on detailed view to see all fields

### Example 2: Batch Process Multiple Contracts

1. Go to "Upload & Process" tab
2. Select multiple PDF files (Ctrl+Click or Cmd+Click)
3. Click "🚀 Process Contracts"
4. Watch progress bar as each file is processed
5. See summary: "3 successful, 0 failed out of 3 total"
6. Go to "View & Search" tab to see all contracts

### Example 3: Search and Export Specific Vessels

1. Go to "View & Search" tab
2. Type vessel name in search box (e.g., "Pacific")
3. Table automatically filters to matching vessels
4. Review the filtered data
5. Click "📥 Download as Excel" to export filtered results
6. File downloads with timestamp: `tcp_contracts_20241222_143045.xlsx`

### Example 4: View Detailed Contract Information

1. Go to "View & Search" tab
2. Scroll down to "Detailed Contract View"
3. Select a contract from the dropdown
4. Expand different sections:
   - 📋 Basic Information
   - 🤝 Parties
   - 💰 Commercial Terms
   - 🚢 Delivery & Redelivery
   - 📝 Additional Information
5. See all extracted fields organized by category

## Key Features

### Real-Time Search
- Type in the search box
- Table updates instantly
- Download buttons export only filtered results
- Shows count: "Showing 2 contract(s)"

### Session State Management
- Contracts stored in browser session
- Data persists while browser tab is open
- "Clear All Contracts" button in sidebar to reset
- No data saved to disk (except downloads)

### Visual Feedback
- ✓ Green success messages
- ✗ Red error messages
- Progress bars during processing
- Balloon animation on successful batch processing
- Real-time status updates

### Responsive Design
- Wide layout for better data viewing
- Columns adjust to screen size
- Scrollable tables for large datasets
- Mobile-friendly interface

## Tips and Best Practices

### Performance
- Process contracts one at a time for testing
- Batch processing saves time for multiple files
- Each contract takes ~10-30 seconds to process
- Processing time depends on PDF complexity and API response

### Cost Management
- Each contract uses Claude API (~$0.01-0.05 per contract)
- Cost displayed in terminal during processing
- Process only necessary files to control costs
- Use search to find existing contracts before reprocessing

### Data Management
- Download Excel/CSV regularly to save your data
- Use "Clear All Contracts" to free up memory
- Session data is lost when browser is closed
- Filter before downloading to export specific contracts

### Search Tips
- Search by vessel name: "Pacific Star"
- Partial matches work: "Pacific" finds "M/V PACIFIC STAR"
- Case doesn't matter: "pacific" = "PACIFIC"
- Search box updates results in real-time

## Troubleshooting

### "No contracts processed yet"
- **Solution:** Upload and process PDFs in the "Upload & Process" tab first

### Upload button not working
- **Solution:** Check file format is `.pdf`
- Try drag-and-drop instead of clicking
- Ensure file is not corrupted

### Processing fails with API error
- **Solution:** Check `.env` file has valid `ANTHROPIC_API_KEY`
- Verify API key has available credits
- Check internet connection

### Excel download not working
- **Solution:** Ensure openpyxl is installed: `pip install openpyxl`
- Check browser download settings
- Try CSV download instead

### App doesn't start
- **Solution:** Ensure Streamlit is installed: `pip install streamlit`
- Check Python version (3.8+)
- Run from project root directory

### Data disappeared
- **Solution:** Session state is cleared when browser closes
- Download Excel before closing browser
- Process contracts again if needed

## Advanced Features

### Viewing Modes
- **Compact view** (default): Shows key fields for quick overview
- **Show all fields**: Enables checkbox to see all 40+ extracted fields

### Download Options
- **Excel (.xlsx)**: Best for data analysis in Excel/Sheets
- **CSV (.csv)**: Best for importing to other systems

### Statistics Sidebar
- Shows total number of processed contracts
- Shows number of unique vessels
- Updates in real-time as you process files

## Command-Line Alternative

If you prefer command-line interface, use:
```bash
python tcp_cli.py
```

See [CLI_README.md](CLI_README.md) for details.

## File Structure

```
tc-agent-project/
├── streamlit_app.py          # Web UI application
├── tcp_cli.py                # Command-line interface
├── src/
│   ├── main.py               # Core processing functions
│   └── data_standardization.py  # Data standardization
├── sample_contracts/         # Input PDF files
├── output/                   # Excel exports (CLI)
└── .env                      # API key configuration
```

## Support

For issues or questions:
1. Check this guide first
2. Review error messages in the app
3. Check terminal output for detailed errors
4. Verify `.env` configuration

## Next Steps

1. **Process your first contract** - Upload a PDF and click Process
2. **Explore the data** - Use the detailed view to see all fields
3. **Search functionality** - Try searching for vessel names
4. **Export data** - Download as Excel for further analysis
5. **Batch processing** - Upload multiple contracts at once

Enjoy using the TCP Contract Processor! 🚢
