"""
Verify the Excel output format and demonstrate CSV conversion
"""

import pandas as pd
from pathlib import Path

def verify_and_convert():
    """Verify Excel format and convert to CSV."""

    excel_file = Path("output/tcp_contract_001_extracted.xlsx")

    if not excel_file.exists():
        print(f"Error: {excel_file} not found!")
        return

    print("="*80)
    print("EXCEL FILE VERIFICATION AND CSV CONVERSION")
    print("="*80)

    # Read Excel file
    print(f"\nReading: {excel_file}")
    df = pd.read_excel(excel_file)

    # Display structure
    print(f"\n[Excel Structure]")
    print(f"  - Rows: {len(df)}")
    print(f"  - Columns: {len(df.columns)}")
    print(f"  - Column names: {list(df.columns)}")

    # Display first 10 rows
    print(f"\n[First 10 Rows]")
    print("-"*80)
    print(df.head(10).to_string(index=False))

    # Display last 5 rows
    print(f"\n[Last 5 Rows]")
    print("-"*80)
    print(df.tail(5).to_string(index=False))

    # Convert to CSV
    csv_file = Path("output/tcp_contract_001_extracted.csv")
    df.to_csv(csv_file, index=False)

    print(f"\n[CSV Conversion]")
    print(f"  - CSV file created: {csv_file}")
    print(f"  - File size: {csv_file.stat().st_size:,} bytes")

    # Display CSV preview
    print(f"\n[CSV File Preview]")
    print("-"*80)
    with open(csv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:15]
        for line in lines:
            print(line.rstrip())

    print("\n" + "="*80)
    print("[SUCCESS] Verification complete!")
    print("="*80)
    print(f"\nOutput files:")
    print(f"  - Excel: {excel_file}")
    print(f"  - CSV:   {csv_file}")


if __name__ == "__main__":
    verify_and_convert()
