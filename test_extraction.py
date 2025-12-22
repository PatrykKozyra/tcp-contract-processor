"""
Test script for PDF text extraction
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import extract_text_from_pdf

def test_pdf_extraction():
    """Test PDF extraction with sample contracts."""

    contracts_dir = Path("sample_contracts")
    pdf_files = list(contracts_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in sample_contracts directory!")
        return

    print(f"Found {len(pdf_files)} PDF file(s) to test\n")
    print("=" * 80)

    # Test the first PDF
    test_file = pdf_files[0]
    print(f"\nTesting extraction with: {test_file.name}")
    print("-" * 80)

    try:
        # Extract text
        text = extract_text_from_pdf(str(test_file))

        # Display statistics
        print(f"\n[SUCCESS] Extraction successful!")
        print(f"\nText Statistics:")
        print(f"  - Total characters: {len(text):,}")
        print(f"  - Total lines: {len(text.splitlines()):,}")
        print(f"  - Total words: {len(text.split()):,}")

        # Display first 1500 characters as preview
        print(f"\n{'='*80}")
        print("Preview (first 1500 characters):")
        print(f"{'='*80}\n")
        print(text[:1500])

        if len(text) > 1500:
            print("\n[... content truncated ...]")

        # Save extracted text to output for inspection
        output_file = Path("output") / f"{test_file.stem}_extracted.txt"
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"\n{'='*80}")
        print(f"[SUCCESS] Full extracted text saved to: {output_file}")
        print(f"{'='*80}")

        # Test all PDFs briefly
        print(f"\n\nTesting all PDFs:")
        print("-" * 80)
        for pdf_file in pdf_files:
            try:
                text = extract_text_from_pdf(str(pdf_file))
                char_count = len(text)
                word_count = len(text.split())
                print(f"[OK] {pdf_file.name:30} - {char_count:>6,} chars, {word_count:>5,} words")
            except Exception as e:
                print(f"[FAIL] {pdf_file.name:30} - Error: {str(e)}")

        print("\n" + "=" * 80)
        print("Test completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] Error during extraction: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_pdf_extraction()
