"""
Project Summary - TCP Document Processing Agent
Display project status and sample output
"""

import pandas as pd
from pathlib import Path

def display_summary():
    """Display project summary and sample output."""

    print("="*80)
    print("TIME CHARTER PARTY (TCP) DOCUMENT PROCESSING AGENT")
    print("="*80)

    # Project Structure
    print("\n[PROJECT STRUCTURE]")
    print("-"*80)

    structure = {
        "sample_contracts/": "Input PDF files (3 contracts with different layouts)",
        "output/": "Generated Excel/CSV files",
        "src/main.py": "Main application code",
        "requirements.txt": "Python dependencies",
        ".env": "API key configuration",
        "README.md": "Complete documentation"
    }

    for path, description in structure.items():
        print(f"  {path:30} - {description}")

    # Sample Contracts
    print("\n[SAMPLE CONTRACTS]")
    print("-"*80)

    contracts_dir = Path("sample_contracts")
    if contracts_dir.exists():
        for pdf in sorted(contracts_dir.glob("*.pdf")):
            size_kb = pdf.stat().st_size / 1024
            print(f"  {pdf.name:30} - {size_kb:>6.1f} KB")

    # Output Files
    print("\n[OUTPUT FILES]")
    print("-"*80)

    output_dir = Path("output")
    if output_dir.exists():
        excel_files = sorted(output_dir.glob("*.xlsx"))
        csv_files = sorted(output_dir.glob("*.csv"))

        print(f"  Excel files: {len(excel_files)}")
        for excel in excel_files:
            size_kb = excel.stat().st_size / 1024
            print(f"    - {excel.name:30} {size_kb:>6.1f} KB")

        if csv_files:
            print(f"\n  CSV files: {len(csv_files)}")
            for csv in csv_files:
                size_kb = csv.stat().st_size / 1024
                print(f"    - {csv.name:30} {size_kb:>6.1f} KB")

    # Sample Data
    print("\n[SAMPLE EXTRACTED DATA]")
    print("-"*80)

    sample_excel = output_dir / "tcp_contract_001_extracted.xlsx"
    if sample_excel.exists():
        df = pd.read_excel(sample_excel)
        print(f"  File: {sample_excel.name}")
        print(f"  Total fields extracted: {len(df)}")
        print(f"\n  Key fields preview:")

        # Show key fields
        key_fields = [
            "Contract Number", "Vessel Name", "Vessel Type",
            "Daily Hire Rate Usd", "Charter Period Months",
            "Delivery Port", "Owner Name"
        ]

        for field in key_fields:
            row = df[df['Field'] == field]
            if not row.empty:
                value = row['Value'].values[0]
                # Truncate long values
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"    {field:30} : {value}")

    # Features
    print("\n[KEY FEATURES]")
    print("-"*80)
    features = [
        "PDF text extraction (multi-page, multiple layouts)",
        "Claude AI-powered data extraction (33+ fields)",
        "Excel export in simple table format (Field | Value)",
        "Easy CSV conversion",
        "Batch processing of multiple contracts",
        "Error handling and logging"
    ]
    for feature in features:
        print(f"  - {feature}")

    # Usage
    print("\n[QUICK START]")
    print("-"*80)
    print("  1. Ensure API key is set in .env file")
    print("  2. Place PDF contracts in sample_contracts/")
    print("  3. Run: python src/main.py")
    print("  4. Find Excel files in output/")
    print("  5. Convert to CSV using pandas or Excel")

    # Example CSV Output
    print("\n[CSV OUTPUT FORMAT]")
    print("-"*80)
    csv_file = output_dir / "tcp_contract_001_extracted.csv"
    if csv_file.exists():
        print(f"  Example from: {csv_file.name}\n")
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]
            for line in lines:
                print(f"  {line.rstrip()}")
        print("  ...")

    print("\n" + "="*80)
    print("PROJECT READY FOR USE!")
    print("="*80)
    print("\nFor detailed documentation, see README.md")
    print("For testing, run: python test_full_pipeline.py")


if __name__ == "__main__":
    display_summary()
