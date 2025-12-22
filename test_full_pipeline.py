"""
Test the complete TCP processing pipeline:
1. Extract text from PDF
2. Extract structured data with Claude AI
3. Export to Excel
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import extract_text_from_pdf, extract_contract_data, export_to_excel, OUTPUT_DIR

def test_pipeline():
    """Test the complete pipeline with one sample contract."""

    # Use the first contract
    pdf_file = Path("sample_contracts/tcp_contract_001.pdf")

    if not pdf_file.exists():
        print(f"Error: {pdf_file} not found!")
        return

    print("="*80)
    print("TCP CONTRACT PROCESSING PIPELINE TEST")
    print("="*80)
    print(f"\nProcessing: {pdf_file.name}")
    print("-"*80)

    try:
        # Step 1: Extract text from PDF
        print("\n[STEP 1] Extracting text from PDF...")
        text = extract_text_from_pdf(str(pdf_file))
        print(f"  - Extracted {len(text):,} characters")
        print(f"  - {len(text.split()):,} words")

        # Step 2: Extract structured data with Claude AI
        print("\n[STEP 2] Extracting structured data with Claude AI...")
        print("  - Sending request to Claude API...")
        contract_data = extract_contract_data(text)
        print(f"  - Received {len(contract_data)} fields")

        # Display extracted data
        print("\n[STEP 3] Extracted Contract Data:")
        print("-"*80)
        for key, value in contract_data.items():
            display_key = key.replace('_', ' ').title()
            # Truncate long values
            if value and isinstance(value, str) and len(str(value)) > 60:
                display_value = str(value)[:60] + "..."
            else:
                display_value = value
            print(f"  {display_key:35} : {display_value}")

        # Step 3: Export to Excel
        print("\n[STEP 4] Exporting to Excel...")
        output_filename = f"{pdf_file.stem}_extracted.xlsx"
        export_to_excel(contract_data, output_filename)

        # Verify file was created
        output_path = OUTPUT_DIR / output_filename
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"  - File created: {output_path}")
            print(f"  - File size: {file_size:,} bytes")

        print("\n" + "="*80)
        print("[SUCCESS] Pipeline completed successfully!")
        print("="*80)
        print(f"\nOutput file: {output_path}")
        print("\nYou can now:")
        print("  1. Open the Excel file to view the data")
        print("  2. Convert to CSV using Excel's 'Save As' feature")
        print("  3. Or use pandas: pd.read_excel('{output_filename}').to_csv('output.csv', index=False)")

    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_pipeline()
