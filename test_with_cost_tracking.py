"""
Test the enhanced Claude API extraction with cost tracking and retry logic
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import extract_text_from_pdf, extract_contract_data

def test_extraction_with_cost():
    """Test extraction with cost tracking."""

    pdf_file = Path("sample_contracts/tcp_contract_001.pdf")

    print("="*80)
    print("CLAUDE API EXTRACTION TEST WITH COST TRACKING")
    print("="*80)
    print(f"\nProcessing: {pdf_file.name}")
    print("-"*80)

    try:
        # Step 1: Extract text
        print("\n[STEP 1] Extracting text from PDF...")
        text = extract_text_from_pdf(str(pdf_file))
        print(f"  - Extracted {len(text):,} characters ({len(text.split()):,} words)")

        # Step 2: Extract data with Claude (includes cost tracking)
        print("\n[STEP 2] Extracting structured data with Claude AI...")
        contract_data = extract_contract_data(text)

        # Display key fields
        print("\n[STEP 3] Key extracted fields:")
        print("-"*80)
        key_fields = [
            "vessel_name", "owner_name", "contract_date",
            "daily_hire_rate_usd", "delivery_date",
            "redelivery_port", "drydocking_policy", "off_hire_threshold_hours"
        ]

        for field in key_fields:
            if field in contract_data:
                value = contract_data[field]
                display_field = field.replace('_', ' ').title()
                # Truncate long values
                if value and isinstance(value, str) and len(str(value)) > 60:
                    value = str(value)[:60] + "..."
                print(f"  {display_field:30} : {value}")

        print("\n" + "="*80)
        print("[SUCCESS] Extraction completed!")
        print("="*80)

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_extraction_with_cost()
