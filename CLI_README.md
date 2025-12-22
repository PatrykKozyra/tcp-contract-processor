# TCP Contract Processing CLI

A command-line interface for processing Time Charter Party (TCP) contracts with AI-powered data extraction.

## Features

1. **Process Single TCP**: Extract data from a specific contract file
2. **Batch Processing**: Process all TCP contracts in the folder
3. **Vessel Query**: Search contracts by vessel name with sorting
4. **Excel Export**: Export processed contracts to Excel format

## Installation

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

Make sure you have your `ANTHROPIC_API_KEY` set in the `.env` file.

## Usage

### Interactive Mode (Recommended for beginners)

Simply run the CLI without arguments to enter interactive mode:

```bash
python tcp_cli.py
```

You'll see a menu with all available options:

```
TCP CONTRACT PROCESSING CLI
============================================================

Main Menu:
  1. Process a single TCP by filename
  2. Process all TCPs in folder
  3. Query for a specific vessel name
  4. Export results to Excel
  5. Show database statistics
  6. Clear database
  0. Exit

Enter your choice (0-6):
```

### Command-Line Arguments

#### 1. Process a Single TCP

```bash
python tcp_cli.py --process tcp_contract_001.pdf
```

Or without the `.pdf` extension:

```bash
python tcp_cli.py --process tcp_contract_001
```

**Output:**
- Extracts contract data using Claude AI
- Standardizes the data
- Adds to in-memory database
- Displays vessel name and contract date

#### 2. Process All TCPs

```bash
python tcp_cli.py --process-all
```

**Output:**
- Processes all PDF files in `sample_contracts/` folder
- Shows progress for each file
- Displays summary of successful and failed files

#### 3. Query by Vessel Name

```bash
python tcp_cli.py --query "Pacific Star"
```

**Features:**
- Case-insensitive partial matching
- Shows vessel name, contract date, and creation timestamp
- Orders results by contract date (descending - most recent first)

**Output example:**
```
Found 2 contract(s):

1. Vessel Name: M/V PACIFIC STAR
   Contract Date: 2024-01-15
   Created At: 2024-12-22T10:30:45.123456
   Source File: tcp_contract_001.pdf
   Charter Period: 24 months
   Daily Hire Rate: $12500.0
```

#### 4. Export to Excel

Auto-generated filename:
```bash
python tcp_cli.py --export
```

Custom filename:
```bash
python tcp_cli.py --export my_contracts.xlsx
```

**Output:**
- Creates Excel file in `output/` folder
- Each contract is a row
- All fields are columns
- Includes metadata (_source_file, _processed_at)

### Combining Commands

Process all contracts and export in one command:

```bash
python tcp_cli.py --process-all --export contracts_2024.xlsx
```

Process specific file, query, and export:

```bash
python tcp_cli.py --process tcp_contract_001.pdf --query "Pacific" --export
```

## Database

The CLI maintains an in-memory database during the session:

- **Add contracts**: Use `--process` or `--process-all`
- **Query contracts**: Use `--query` to search
- **View statistics**: Use interactive mode option 5
- **Clear database**: Use interactive mode option 6
- **Persist data**: Use `--export` to save to Excel

**Note:** Database is cleared when the CLI exits. Export to Excel to persist data.

## File Locations

- **Input PDFs**: `sample_contracts/*.pdf`
- **Excel Output**: `output/*.xlsx`
- **Source Code**: `src/main.py`, `src/data_standardization.py`

## Examples

### Example 1: Quick Processing and Export

```bash
python tcp_cli.py --process-all --export
```

This will:
1. Process all PDFs in `sample_contracts/`
2. Export to `output/tcp_contracts_export_YYYYMMDD_HHMMSS.xlsx`

### Example 2: Find All Contracts for a Vessel

```bash
# First, load all contracts
python tcp_cli.py --process-all

# Then query
python tcp_cli.py --query "Pacific Star"
```

Or in one command:
```bash
python tcp_cli.py --process-all --query "Pacific Star"
```

### Example 3: Interactive Workflow

```bash
python tcp_cli.py
```

Then:
1. Choose option 2 to process all TCPs
2. Choose option 3 to query for a vessel
3. Choose option 4 to export results
4. Choose option 0 to exit

## Query Features

When querying by vessel name:

- **Partial matching**: Search for "Pacific" to find "M/V PACIFIC STAR"
- **Case-insensitive**: "pacific" = "PACIFIC" = "Pacific"
- **Sorted results**: Most recent contracts first (by contract_date)
- **Full details**: Shows contract date, hire rate, charter period

## Excel Export Format

The exported Excel file has the following structure:

- **One sheet**: "TCP Contracts"
- **One row per contract**
- **Columns include**:
  - contract_number, contract_date, vessel_name, imo_number
  - vessel_flag, year_built, vessel_type, deadweight
  - owner_name, charterer_name
  - charter_period_months, daily_hire_rate_usd
  - delivery_date, delivery_port, redelivery_port
  - And many more fields...
  - _source_file (metadata)
  - _processed_at (metadata)

## Troubleshooting

### "No PDF files found"
- Check that PDF files exist in `sample_contracts/` folder
- Ensure files have `.pdf` extension

### "No contracts in database"
- Process contracts first using `--process` or `--process-all`
- The database is in-memory and cleared on exit

### "ANTHROPIC_API_KEY not found"
- Create a `.env` file in the project root
- Add: `ANTHROPIC_API_KEY=your_key_here`

### "Error processing contract"
- Check PDF is readable and not corrupted
- Ensure API key is valid and has credits
- Check network connection

## Help

View all available options:

```bash
python tcp_cli.py --help
```

## Cost Considerations

Each contract processing uses Claude AI API:
- Estimated cost: ~$0.01-0.05 per contract
- Cost shown during processing
- Use `--process` for single files to control costs
