"""
Data Standardization Layer for TCP Contract Data

Handles:
- Date parsing and ISO format conversion
- Vessel name normalization
- Currency value standardization
- Numeric value extraction
- DataFrame creation with standardized columns
"""

import re
from datetime import datetime
from typing import Any, Optional
import pandas as pd


class TCPDataStandardizer:
    """Standardizes TCP contract data for consistent output."""

    # Common date formats found in TCPs
    DATE_FORMATS = [
        "%B %d, %Y",           # January 15, 2024
        "%d %B %Y",            # 15 January 2024
        "%b %d, %Y",           # Jan 15, 2024
        "%d %b %Y",            # 15 Jan 2024
        "%Y-%m-%d",            # 2024-01-15 (ISO)
        "%d/%m/%Y",            # 15/01/2024
        "%m/%d/%Y",            # 01/15/2024
        "%d.%m.%Y",            # 15.01.2024
        "%Y/%m/%d",            # 2024/01/15
        "%B %Y",               # January 2024 (month only)
        "%b %Y",               # Jan 2024
    ]

    @staticmethod
    def standardize_date(date_value: Any) -> Optional[str]:
        """
        Convert various date formats to ISO format (YYYY-MM-DD).

        Args:
            date_value: Date string in various formats

        Returns:
            ISO format date string (YYYY-MM-DD) or None if parsing fails
        """
        if not date_value or date_value == "null" or pd.isna(date_value):
            return None

        date_str = str(date_value).strip()

        # Already in ISO format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str

        # Try each date format
        for fmt in TCPDataStandardizer.DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # Try to extract year-month pattern for partial dates
        # Example: "January 2024" -> "2024-01-01"
        month_year_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', date_str, re.IGNORECASE)
        if month_year_match:
            month_name = month_year_match.group(1)
            year = month_year_match.group(2)
            try:
                parsed_date = datetime.strptime(f"{month_name} {year}", "%B %Y")
                return parsed_date.strftime("%Y-%m-01")  # First day of month
            except ValueError:
                pass

        # Try to extract just year
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            return f"{year_match.group(0)}-01-01"

        # If all parsing fails, return None
        return None

    @staticmethod
    def standardize_vessel_name(vessel_name: Any) -> Optional[str]:
        """
        Standardize vessel name: uppercase, trimmed, common prefixes.

        Args:
            vessel_name: Vessel name in various formats

        Returns:
            Standardized vessel name or None
        """
        if not vessel_name or vessel_name == "null" or pd.isna(vessel_name):
            return None

        name = str(vessel_name).strip()

        # Convert to uppercase
        name = name.upper()

        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name)

        # Ensure common prefixes are present
        # Add M/V or MT if missing and looks like a vessel name
        if not re.match(r'^(M/V|MT|MV|M\.V\.|S\.S\.|SS)', name):
            # Check if it's likely a vessel name (starts with capital letter, not a company name)
            if not any(keyword in name for keyword in ['LTD', 'INC', 'CORP', 'COMPANY', 'HOLDINGS', 'AS', 'SA', 'LLC']):
                name = f"M/V {name}"

        # Standardize prefix formats
        name = re.sub(r'^M\.V\.\s*', 'M/V ', name)
        name = re.sub(r'^MV\s+', 'M/V ', name)
        name = re.sub(r'^M\.T\.\s*', 'MT ', name)
        name = re.sub(r'^MT\s+', 'MT ', name)

        # Clean up any double spaces
        name = re.sub(r'\s+', ' ', name)

        return name.strip()

    @staticmethod
    def extract_numeric_value(value: Any) -> Optional[float]:
        """
        Extract numeric value from string, handling various formats.

        Args:
            value: Value that may contain numbers

        Returns:
            Extracted numeric value or None
        """
        if not value or value == "null" or pd.isna(value):
            return None

        # If already a number
        if isinstance(value, (int, float)):
            return float(value)

        value_str = str(value).strip()

        # Remove common currency symbols and formatting
        value_str = re.sub(r'[,$€£¥\s]', '', value_str)

        # Extract first number found
        number_match = re.search(r'-?\d+\.?\d*', value_str)
        if number_match:
            try:
                return float(number_match.group(0))
            except ValueError:
                return None

        return None

    @staticmethod
    def standardize_currency(value: Any, decimal_places: int = 2) -> Optional[float]:
        """
        Standardize currency value to float with specified decimal places.

        Args:
            value: Currency value in various formats
            decimal_places: Number of decimal places (default: 2)

        Returns:
            Standardized currency value or None
        """
        numeric = TCPDataStandardizer.extract_numeric_value(value)
        if numeric is not None:
            return round(numeric, decimal_places)
        return None

    @staticmethod
    def standardize_text(value: Any) -> Optional[str]:
        """
        Standardize text field: trim, remove extra whitespace.

        Args:
            value: Text value

        Returns:
            Cleaned text or None
        """
        if not value or value == "null" or pd.isna(value):
            return None

        text = str(value).strip()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove "null" strings
        if text.lower() == "null":
            return None

        return text if text else None

    @staticmethod
    def standardize_contract_data(raw_data: dict) -> dict:
        """
        Apply standardization to all fields in contract data.

        Args:
            raw_data: Raw contract data dictionary from Claude

        Returns:
            Standardized contract data dictionary
        """
        standardized = {}

        # Date fields
        date_fields = [
            'contract_date', 'delivery_date',
            'last_special_survey', 'next_special_survey'
        ]
        for field in date_fields:
            if field in raw_data:
                standardized[field] = TCPDataStandardizer.standardize_date(raw_data[field])

        # Vessel name
        if 'vessel_name' in raw_data:
            standardized['vessel_name'] = TCPDataStandardizer.standardize_vessel_name(raw_data['vessel_name'])

        # Numeric fields (integers)
        numeric_fields = [
            'charter_period_months', 'off_hire_threshold_hours'
        ]
        for field in numeric_fields:
            if field in raw_data:
                numeric = TCPDataStandardizer.extract_numeric_value(raw_data[field])
                standardized[field] = int(numeric) if numeric is not None else None

        # Currency/numeric fields (with decimals)
        currency_fields = [
            'daily_hire_rate_usd'
        ]
        for field in currency_fields:
            if field in raw_data:
                standardized[field] = TCPDataStandardizer.standardize_currency(raw_data[field])

        # Year field (extract and convert to int)
        if 'year_built' in raw_data:
            year = TCPDataStandardizer.extract_numeric_value(raw_data['year_built'])
            standardized['year_built'] = int(year) if year is not None else None

        # IMO number (remove any non-numeric characters)
        if 'imo_number' in raw_data:
            imo = TCPDataStandardizer.extract_numeric_value(raw_data['imo_number'])
            standardized['imo_number'] = str(int(imo)) if imo is not None else None

        # Text fields (just clean them)
        text_fields = [
            'contract_number', 'vessel_flag', 'vessel_type',
            'deadweight', 'gross_tonnage', 'speed_about', 'consumption_per_day',
            'owner_name', 'owner_location', 'charterer_name', 'charterer_location',
            'charter_period_description', 'delivery_port', 'redelivery_port',
            'bunkers_delivery_ifo', 'bunkers_delivery_mgo',
            'bunkers_redelivery_ifo', 'bunkers_redelivery_mgo',
            'drydocking_policy', 'trading_limits', 'law_and_arbitration',
            'commission_rate', 'additional_notes'
        ]
        for field in text_fields:
            if field in raw_data:
                standardized[field] = TCPDataStandardizer.standardize_text(raw_data[field])

        return standardized

    @staticmethod
    def create_standardized_dataframe(contract_data: dict) -> pd.DataFrame:
        """
        Create a pandas DataFrame with standardized data.

        Args:
            contract_data: Standardized contract data dictionary

        Returns:
            pandas DataFrame with two columns: Field and Value
        """
        # Convert to list of dicts for DataFrame
        rows = []
        for field, value in contract_data.items():
            display_name = field.replace('_', ' ').title()
            rows.append({
                'Field': display_name,
                'Value': value
            })

        df = pd.DataFrame(rows)
        return df

    @staticmethod
    def create_columnar_dataframe(contracts: list) -> pd.DataFrame:
        """
        Create a pandas DataFrame with each contract as a row and fields as columns.
        Better for CSV export and data analysis.

        Args:
            contracts: List of standardized contract data dictionaries

        Returns:
            pandas DataFrame with contracts as rows
        """
        if not contracts:
            return pd.DataFrame()

        # Define column order for better readability
        column_order = [
            'contract_number', 'contract_date', 'vessel_name', 'imo_number',
            'vessel_flag', 'year_built', 'vessel_type', 'deadweight', 'gross_tonnage',
            'owner_name', 'owner_location', 'charterer_name', 'charterer_location',
            'charter_period_months', 'daily_hire_rate_usd', 'delivery_date',
            'delivery_port', 'redelivery_port', 'speed_about', 'consumption_per_day',
            'bunkers_delivery_ifo', 'bunkers_delivery_mgo',
            'bunkers_redelivery_ifo', 'bunkers_redelivery_mgo',
            'last_special_survey', 'next_special_survey', 'drydocking_policy',
            'off_hire_threshold_hours', 'trading_limits', 'law_and_arbitration',
            'commission_rate', 'charter_period_description', 'additional_notes'
        ]

        df = pd.DataFrame(contracts)

        # Reorder columns (only include those that exist)
        existing_cols = [col for col in column_order if col in df.columns]
        other_cols = [col for col in df.columns if col not in column_order]
        final_cols = existing_cols + other_cols

        df = df[final_cols]

        return df


def standardize_and_validate(raw_data: dict) -> dict:
    """
    Main function to standardize and validate contract data.

    Args:
        raw_data: Raw contract data from Claude API

    Returns:
        Standardized and validated contract data
    """
    print("  - Standardizing data...")

    # Apply standardization
    standardized = TCPDataStandardizer.standardize_contract_data(raw_data)

    # Count standardized fields
    non_null_count = sum(1 for v in standardized.values() if v is not None)
    print(f"  - Standardized {non_null_count}/{len(standardized)} fields")

    return standardized
