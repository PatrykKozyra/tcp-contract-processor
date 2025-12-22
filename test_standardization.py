"""
Test the data standardization layer
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_standardization import TCPDataStandardizer, standardize_and_validate


def test_date_standardization():
    """Test date parsing and ISO conversion."""
    print("="*80)
    print("DATE STANDARDIZATION TESTS")
    print("="*80)

    test_dates = [
        ("January 15, 2024", "2024-01-15"),
        ("15 January 2024", "2024-01-15"),
        ("Jan 15, 2024", "2024-01-15"),
        ("2024-01-15", "2024-01-15"),
        ("01/15/2024", "2024-01-15"),
        ("15/01/2024", "2024-01-15"),
        ("January 2024", "2024-01-01"),
        ("December 2025", "2025-12-01"),
        ("2026", "2026-01-01"),
        ("On or about February 1, 2024", "2024-01-01"),  # Extracts "February 2024"
        (None, None),
    ]

    print("\nTest Cases:")
    print("-"*80)
    for input_date, expected in test_dates:
        result = TCPDataStandardizer.standardize_date(input_date)
        status = "[OK]" if result == expected else "[FAIL]"
        result_str = str(result) if result else "None"
        expected_str = str(expected) if expected else "None"
        print(f"{status} Input: {str(input_date):35} => {result_str:15} (expected: {expected_str})")

def test_vessel_name_standardization():
    """Test vessel name normalization."""
    print("\n" + "="*80)
    print("VESSEL NAME STANDARDIZATION TESTS")
    print("="*80)

    test_vessels = [
        ("northern star", "M/V NORTHERN STAR"),
        ("MV NORTHERN STAR", "M/V NORTHERN STAR"),
        ("M.V. PACIFIC DAWN", "M/V PACIFIC DAWN"),
        ("MT PACIFIC DAWN", "MT PACIFIC DAWN"),
        ("AEGEAN EXPRESS", "M/V AEGEAN EXPRESS"),
        ("  northern  star  ", "M/V NORTHERN STAR"),
        (None, None),
    ]

    print("\nTest Cases:")
    print("-"*80)
    for input_name, expected in test_vessels:
        result = TCPDataStandardizer.standardize_vessel_name(input_name)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"{status} Input: {str(input_name):30} => {result}")


def test_currency_standardization():
    """Test currency value extraction and standardization."""
    print("\n" + "="*80)
    print("CURRENCY STANDARDIZATION TESTS")
    print("="*80)

    test_values = [
        ("$18,500", 18500.00),
        ("USD 18,500 per day", 18500.00),
        ("22750", 22750.00),
        ("$11,850.50", 11850.50),
        ("18500.00", 18500.00),
        (18500, 18500.00),
        (None, None),
    ]

    print("\nTest Cases:")
    print("-"*80)
    for input_val, expected in test_values:
        result = TCPDataStandardizer.standardize_currency(input_val)
        status = "[OK]" if result == expected else "[FAIL]"
        result_str = str(result) if result is not None else "None"
        expected_str = str(expected) if expected is not None else "None"
        print(f"{status} Input: {str(input_val):30} => {result_str:>12} (expected: {expected_str})")


def test_numeric_extraction():
    """Test numeric value extraction."""
    print("\n" + "="*80)
    print("NUMERIC EXTRACTION TESTS")
    print("="*80)

    test_values = [
        ("24 months", 24.0),
        ("24", 24.0),
        ("36-month charter", 36.0),
        ("82,500 metric tons", 82500.0),
        ("2018", 2018.0),
        ("IMO 9876543", 9876543.0),
        (24, 24.0),
        (None, None),
    ]

    print("\nTest Cases:")
    print("-"*80)
    for input_val, expected in test_values:
        result = TCPDataStandardizer.extract_numeric_value(input_val)
        status = "[OK]" if result == expected else "[FAIL]"
        result_str = str(result) if result is not None else "None"
        expected_str = str(expected) if expected is not None else "None"
        print(f"{status} Input: {str(input_val):30} => {result_str:>12} (expected: {expected_str})")


def test_full_standardization():
    """Test full standardization with sample contract data."""
    print("\n" + "="*80)
    print("FULL CONTRACT DATA STANDARDIZATION TEST")
    print("="*80)

    # Simulate raw data from Claude (with various formats)
    raw_data = {
        "contract_number": "TCP-2024-001",
        "contract_date": "January 15, 2024",
        "vessel_name": "northern star",
        "imo_number": "9876543",
        "vessel_flag": "Norwegian",
        "year_built": "2018",
        "vessel_type": "Bulk Carrier",
        "deadweight": "82,500 metric tons (about 25% more grain)",
        "gross_tonnage": "45,678 GT",
        "owner_name": "Nordic Maritime Holdings AS",
        "owner_location": "Oslo, Norway",
        "charterer_name": "Global Shipping Solutions Ltd",
        "charterer_location": "London, United Kingdom",
        "charter_period_months": "24",
        "charter_period_description": "24 months, with option to extend",
        "daily_hire_rate_usd": "$18,500 per day",
        "delivery_date": "February 1, 2024",
        "delivery_port": "Busan, South Korea",
        "redelivery_port": "Worldwide, between Singapore and Hamburg range",
        "bunkers_delivery_ifo": "Approximately 1,200 metric tons",
        "off_hire_threshold_hours": "24 consecutive hours",
        "next_special_survey": "December 2025",
        "last_special_survey": None,
    }

    print("\nRaw Data Sample:")
    print("-"*80)
    for key, value in list(raw_data.items())[:5]:
        print(f"  {key:30} : {value}")
    print("  ...")

    # Standardize
    standardized = TCPDataStandardizer.standardize_contract_data(raw_data)

    print("\nStandardized Data Sample:")
    print("-"*80)

    # Show key standardizations
    checks = [
        ("contract_date", "2024-01-15", "Date converted to ISO"),
        ("vessel_name", "M/V NORTHERN STAR", "Vessel name normalized"),
        ("year_built", 2018, "Year extracted as integer"),
        ("charter_period_months", 24, "Period extracted as integer"),
        ("daily_hire_rate_usd", 18500.00, "Currency extracted as float"),
        ("next_special_survey", "2025-12-01", "Date converted to ISO"),
        ("off_hire_threshold_hours", 24, "Hours extracted as integer"),
    ]

    all_passed = True
    for field, expected, description in checks:
        actual = standardized.get(field)
        status = "[OK]" if actual == expected else "[FAIL]"
        if actual != expected:
            all_passed = False
        print(f"{status} {field:30} : {actual:20} ({description})")

    print("\n" + "="*80)
    if all_passed:
        print("[SUCCESS] All standardization tests passed!")
    else:
        print("[WARNING] Some tests failed - check output above")
    print("="*80)


def main():
    """Run all standardization tests."""
    print("\n" + "="*80)
    print("TCP DATA STANDARDIZATION TEST SUITE")
    print("="*80 + "\n")

    test_date_standardization()
    test_vessel_name_standardization()
    test_currency_standardization()
    test_numeric_extraction()
    test_full_standardization()

    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)


if __name__ == "__main__":
    main()
