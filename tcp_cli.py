"""
TCP Contract Processing CLI

Command-line interface for processing TCP contracts with the following features:
1. Process a single TCP by filename
2. Process all TCPs in the folder
3. Query for a specific vessel name
4. Export results to Excel
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional
import pandas as pd
from datetime import datetime

# Import from existing modules
from src.main import (
    extract_text_from_pdf,
    extract_contract_data,
    export_to_excel,
    OUTPUT_DIR,
    CONTRACTS_DIR
)
from src.data_standardization import standardize_and_validate, TCPDataStandardizer


class TCPDatabase:
    """Simple in-memory database for processed TCP contracts."""

    def __init__(self):
        self.contracts = []

    def add_contract(self, contract_data: dict, filename: str):
        """Add a processed contract to the database."""
        contract_data['_source_file'] = filename
        contract_data['_processed_at'] = datetime.now().isoformat()
        self.contracts.append(contract_data)

    def query_by_vessel_name(self, vessel_name: str) -> List[dict]:
        """
        Query contracts by vessel name (case-insensitive partial match).
        Returns list of contracts ordered by contract_date descending.
        """
        vessel_name_upper = vessel_name.upper()

        # Filter contracts that match the vessel name
        matching = [
            contract for contract in self.contracts
            if contract.get('vessel_name') and
            vessel_name_upper in contract['vessel_name'].upper()
        ]

        # Sort by contract_date descending (most recent first)
        matching.sort(
            key=lambda x: x.get('contract_date') or '0000-00-00',
            reverse=True
        )

        return matching

    def get_all_contracts(self) -> List[dict]:
        """Get all contracts in the database."""
        return self.contracts

    def clear(self):
        """Clear all contracts from database."""
        self.contracts = []


# Global database instance
db = TCPDatabase()


def process_single_tcp(filename: str) -> Optional[dict]:
    """
    Process a single TCP contract file.

    Args:
        filename: Name of the PDF file (with or without .pdf extension)

    Returns:
        Standardized contract data or None if processing fails
    """
    # Add .pdf extension if not present
    if not filename.endswith('.pdf'):
        filename = f"{filename}.pdf"

    pdf_path = CONTRACTS_DIR / filename

    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        return None

    print(f"\nProcessing: {filename}")
    print("-" * 60)

    try:
        # Extract text from PDF
        print("Step 1/3: Extracting text from PDF...")
        text = extract_text_from_pdf(str(pdf_path))
        print(f"  - Extracted {len(text)} characters")

        # Extract structured data using Claude
        print("Step 2/3: Extracting contract data using Claude AI...")
        raw_contract_data = extract_contract_data(text)

        # Standardize the data
        print("Step 3/3: Standardizing data...")
        contract_data = standardize_and_validate(raw_contract_data)

        # Add to database
        db.add_contract(contract_data, filename)

        print(f"\n✓ Successfully processed: {filename}")
        print(f"  Vessel: {contract_data.get('vessel_name', 'N/A')}")
        print(f"  Contract Date: {contract_data.get('contract_date', 'N/A')}")

        return contract_data

    except Exception as e:
        print(f"\n✗ Error processing {filename}: {str(e)}")
        return None


def process_all_tcps() -> List[dict]:
    """
    Process all TCP PDF files in the contracts directory.

    Returns:
        List of successfully processed contract data
    """
    pdf_files = list(CONTRACTS_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {CONTRACTS_DIR}")
        return []

    print(f"\nFound {len(pdf_files)} PDF file(s) to process")
    print("=" * 60)

    successful = []
    failed = []

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")

        contract_data = process_single_tcp(pdf_file.name)

        if contract_data:
            successful.append(contract_data)
        else:
            failed.append(pdf_file.name)

    print("\n" + "=" * 60)
    print(f"Processing complete!")
    print(f"  ✓ Successful: {len(successful)}")
    print(f"  ✗ Failed: {len(failed)}")

    if failed:
        print(f"\nFailed files:")
        for f in failed:
            print(f"  - {f}")

    return successful


def query_vessel(vessel_name: str):
    """
    Query for contracts by vessel name and display results.

    Args:
        vessel_name: Vessel name to search for (partial match supported)
    """
    if not db.contracts:
        print("\nNo contracts in database. Please process contracts first.")
        return

    print(f"\nSearching for vessels matching: '{vessel_name}'")
    print("-" * 60)

    results = db.query_by_vessel_name(vessel_name)

    if not results:
        print(f"No vessels found matching '{vessel_name}'")
        return

    print(f"Found {len(results)} contract(s):\n")

    for i, contract in enumerate(results, 1):
        print(f"{i}. Vessel Name: {contract.get('vessel_name', 'N/A')}")
        print(f"   Contract Date: {contract.get('contract_date', 'N/A')}")
        print(f"   Created At: {contract.get('_processed_at', 'N/A')}")
        print(f"   Source File: {contract.get('_source_file', 'N/A')}")
        print(f"   Charter Period: {contract.get('charter_period_months', 'N/A')} months")
        print(f"   Daily Hire Rate: ${contract.get('daily_hire_rate_usd', 'N/A')}")
        print()


def export_to_excel_file(output_filename: str = None):
    """
    Export all processed contracts to Excel file.

    Args:
        output_filename: Optional custom output filename
    """
    if not db.contracts:
        print("\nNo contracts to export. Please process contracts first.")
        return

    # Generate filename if not provided
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"tcp_contracts_export_{timestamp}.xlsx"

    # Add .xlsx extension if not present
    if not output_filename.endswith('.xlsx'):
        output_filename = f"{output_filename}.xlsx"

    output_path = OUTPUT_DIR / output_filename

    print(f"\nExporting {len(db.contracts)} contract(s) to Excel...")

    try:
        # Create a columnar DataFrame (each contract is a row)
        df = TCPDataStandardizer.create_columnar_dataframe(db.contracts)

        # Export to Excel
        df.to_excel(
            output_path,
            index=False,
            engine='openpyxl',
            sheet_name='TCP Contracts'
        )

        print(f"✓ Successfully exported to: {output_path}")
        print(f"  Total contracts: {len(db.contracts)}")
        print(f"  Total columns: {len(df.columns)}")

    except Exception as e:
        print(f"✗ Error exporting to Excel: {str(e)}")


def interactive_menu():
    """Run an interactive menu-based CLI."""
    print("\n" + "=" * 60)
    print("TCP CONTRACT PROCESSING CLI")
    print("=" * 60)

    while True:
        print("\nMain Menu:")
        print("  1. Process a single TCP by filename")
        print("  2. Process all TCPs in folder")
        print("  3. Query for a specific vessel name")
        print("  4. Export results to Excel")
        print("  5. Show database statistics")
        print("  6. Clear database")
        print("  0. Exit")

        choice = input("\nEnter your choice (0-6): ").strip()

        if choice == '1':
            filename = input("\nEnter TCP filename (e.g., tcp_contract_001.pdf): ").strip()
            if filename:
                process_single_tcp(filename)
            else:
                print("Invalid filename")

        elif choice == '2':
            confirm = input("\nThis will process all PDF files. Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                process_all_tcps()

        elif choice == '3':
            vessel_name = input("\nEnter vessel name to search: ").strip()
            if vessel_name:
                query_vessel(vessel_name)
            else:
                print("Invalid vessel name")

        elif choice == '4':
            filename = input("\nEnter output filename (or press Enter for auto-generated): ").strip()
            export_to_excel_file(filename if filename else None)

        elif choice == '5':
            print(f"\nDatabase Statistics:")
            print(f"  Total contracts: {len(db.contracts)}")
            if db.contracts:
                vessels = [c.get('vessel_name', 'N/A') for c in db.contracts]
                print(f"  Unique vessels: {len(set(vessels))}")
                print(f"  Vessels: {', '.join(set(vessels))}")

        elif choice == '6':
            confirm = input("\nAre you sure you want to clear the database? (y/n): ").strip().lower()
            if confirm == 'y':
                db.clear()
                print("✓ Database cleared")

        elif choice == '0':
            print("\nGoodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='TCP Contract Processing CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python tcp_cli.py

  # Process a single contract
  python tcp_cli.py --process tcp_contract_001.pdf

  # Process all contracts
  python tcp_cli.py --process-all

  # Query by vessel name
  python tcp_cli.py --query "Pacific Star"

  # Process all and export to Excel
  python tcp_cli.py --process-all --export contracts.xlsx
        """
    )

    parser.add_argument(
        '--process',
        metavar='FILENAME',
        help='Process a single TCP contract file'
    )

    parser.add_argument(
        '--process-all',
        action='store_true',
        help='Process all TCP contracts in the folder'
    )

    parser.add_argument(
        '--query',
        metavar='VESSEL_NAME',
        help='Query for a specific vessel name'
    )

    parser.add_argument(
        '--export',
        metavar='OUTPUT_FILE',
        nargs='?',
        const='auto',
        help='Export results to Excel (optional: specify filename)'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive menu mode'
    )

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(exist_ok=True)

    # If no arguments provided, run interactive mode
    if len(sys.argv) == 1:
        interactive_menu()
        return

    # Process arguments
    if args.interactive:
        interactive_menu()
        return

    # Process single file
    if args.process:
        process_single_tcp(args.process)

    # Process all files
    if args.process_all:
        process_all_tcps()

    # Query vessel
    if args.query:
        if not db.contracts:
            print("\nWarning: No contracts in database.")
            print("Tip: Use --process or --process-all first to load contracts.")
        else:
            query_vessel(args.query)

    # Export to Excel
    if args.export:
        if args.export == 'auto':
            export_to_excel_file()
        else:
            export_to_excel_file(args.export)


if __name__ == "__main__":
    main()
