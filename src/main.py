"""
Time Charter Party (TCP) Document Processing Agent

This module provides functionality to extract and process time charter party
contract data from PDF documents using Claude AI and export to Excel format.
"""

import os
from pathlib import Path
import pdfplumber
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv
from src.data_standardization import standardize_and_validate, TCPDataStandardizer

# Load environment variables
load_dotenv()

# Initialize paths
PROJECT_ROOT = Path(__file__).parent.parent
CONTRACTS_DIR = PROJECT_ROOT / "sample_contracts"
OUTPUT_DIR = PROJECT_ROOT / "output"


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        str: Extracted text content from the PDF
    """
    try:
        # Open the PDF file with pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from all pages
            text_content = []

            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text from current page
                page_text = page.extract_text()

                if page_text:
                    # Add page separator for multi-page PDFs
                    if page_num > 1:
                        text_content.append(f"\n--- Page {page_num} ---\n")
                    text_content.append(page_text)
                else:
                    print(f"Warning: No text found on page {page_num}")

            # Combine all text
            full_text = "\n".join(text_content)

            # Clean up excessive whitespace while preserving structure
            # Replace multiple consecutive blank lines with max 2 blank lines
            import re
            full_text = re.sub(r'\n{3,}', '\n\n', full_text)

            return full_text.strip()

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def extract_contract_data(text: str, max_retries: int = 3) -> dict:
    """
    Extract structured contract data from text using Claude AI.

    Args:
        text (str): Raw text extracted from PDF
        max_retries (int): Maximum number of retry attempts (default: 3)

    Returns:
        dict: Structured contract data including:
            - vessel_name
            - charter_period
            - hire_rate
            - delivery_port
            - redelivery_port
            - other relevant TCP fields

    Raises:
        ValueError: If API key is not found
        Exception: If extraction fails after all retries
    """
    # Initialize Anthropic client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

    client = Anthropic(api_key=api_key)

    # Estimate token usage for cost tracking
    input_tokens_estimate = len(text.split()) * 1.3  # Rough estimate
    print(f"  - Estimated input tokens: ~{int(input_tokens_estimate)}")

    # Create prompt for contract data extraction
    prompt = f"""Please analyze this Time Charter Party (TCP) contract and extract the following information into a structured format.

CONTRACT TEXT:
{text}

Please extract and return ONLY the following fields in valid JSON format. If a field is not found, use null:

{{
    "contract_number": "Contract reference number",
    "contract_date": "Date of contract",
    "vessel_name": "Name of the vessel",
    "imo_number": "IMO number",
    "vessel_flag": "Flag/nationality",
    "year_built": "Year vessel was built",
    "vessel_type": "Type of vessel (bulk carrier, tanker, container, etc.)",
    "deadweight": "Deadweight tonnage",
    "gross_tonnage": "Gross tonnage",
    "speed_about": "Speed in knots",
    "consumption_per_day": "Fuel consumption per day",
    "owner_name": "Owner's company name",
    "owner_location": "Owner's location/country",
    "charterer_name": "Charterer's company name",
    "charterer_location": "Charterer's location/country",
    "charter_period_months": "Charter period in months (numeric)",
    "charter_period_description": "Full charter period description",
    "daily_hire_rate_usd": "Daily hire rate in USD (numeric only)",
    "delivery_date": "Delivery date or period",
    "delivery_port": "Delivery port/place",
    "redelivery_port": "Redelivery port/place or range",
    "bunkers_delivery_ifo": "IFO/VLSFO quantity on delivery (metric tons)",
    "bunkers_delivery_mgo": "MGO/MDO quantity on delivery (metric tons)",
    "bunkers_redelivery_ifo": "IFO/VLSFO quantity on redelivery (metric tons)",
    "bunkers_redelivery_mgo": "MGO/MDO quantity on redelivery (metric tons)",
    "last_special_survey": "Date of last special survey",
    "next_special_survey": "Date when next special survey is due",
    "drydocking_policy": "Summary of drydocking provisions",
    "off_hire_threshold_hours": "Minimum hours before off-hire applies (numeric)",
    "trading_limits": "Geographic trading limits",
    "law_and_arbitration": "Governing law and arbitration location",
    "commission_rate": "Commission rate percentage",
    "additional_notes": "Any other significant terms or special conditions"
}}

Return ONLY valid JSON, no other text or explanation."""

    import json
    import re
    import time

    # Retry loop with exponential backoff
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait_time = 2 ** (attempt - 1)  # Exponential backoff: 2, 4, 8 seconds
                print(f"  - Retrying in {wait_time} seconds... (attempt {attempt}/{max_retries})")
                time.sleep(wait_time)

            # Send request to Claude API
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,  # Reduced from 4000 to save costs
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Display actual token usage
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            estimated_cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.015 / 1000)

            print(f"  - Actual tokens: {input_tokens} input, {output_tokens} output")
            print(f"  - Estimated cost: ${estimated_cost:.4f}")

            # Extract the response text
            response_text = message.content[0].text.strip()

            # Remove markdown code blocks if present
            # Strip markdown code fences (```json and ```)
            if response_text.startswith('```'):
                # Remove opening ```json or ```
                response_text = re.sub(r'^```(?:json)?\s*\n', '', response_text)
                # Remove closing ```
                response_text = re.sub(r'\n```\s*$', '', response_text)
                response_text = response_text.strip()

            # Parse JSON response
            contract_data = json.loads(response_text)

            # Validate that we got a dictionary with data
            if not isinstance(contract_data, dict) or len(contract_data) == 0:
                raise ValueError("Received empty or invalid data structure from Claude")

            print(f"  - Successfully extracted {len(contract_data)} fields")
            return contract_data

        except json.JSONDecodeError as e:
            last_error = f"JSON parsing error: {e}"
            print(f"  - Error: Failed to parse JSON response from Claude: {e}")
            if attempt == max_retries:
                print(f"  - Response was: {response_text[:500] if 'response_text' in locals() else 'No response'}")

        except Exception as e:
            last_error = str(e)
            print(f"  - Error during Claude API call (attempt {attempt}/{max_retries}): {e}")

        # If this was the last attempt, raise the error
        if attempt == max_retries:
            error_msg = f"Failed to extract contract data after {max_retries} attempts. Last error: {last_error}"
            print(f"  - {error_msg}")
            raise Exception(error_msg)


def export_to_excel(contract_data: dict, output_filename: str) -> None:
    """
    Export contract data to Excel file in simple tabular format.

    Args:
        contract_data (dict): Structured contract data
        output_filename (str): Name of the output Excel file
    """
    # Convert dictionary to simple two-column format: Field | Value
    # This makes it easy to convert to CSV later
    data_rows = []

    for field_name, field_value in contract_data.items():
        # Convert field name from snake_case to Title Case
        display_name = field_name.replace('_', ' ').title()
        data_rows.append({
            'Field': display_name,
            'Value': field_value
        })

    # Create DataFrame with simple two-column structure
    df = pd.DataFrame(data_rows)

    # Construct full output path
    output_path = OUTPUT_DIR / output_filename

    # Export to Excel without any formatting (raw table)
    # This makes it easy to convert to CSV
    df.to_excel(
        output_path,
        index=False,
        engine='openpyxl',
        sheet_name='Contract Data'
    )

    print(f"Exported to: {output_path}")


def process_contract(pdf_path: str, output_filename: str = None) -> None:
    """
    Main function to process a TCP contract from PDF to Excel.

    Args:
        pdf_path (str): Path to the PDF contract file
        output_filename (str): Optional custom output filename
    """
    print(f"Processing contract: {pdf_path}")

    # Extract text from PDF
    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)

    # Extract structured data using Claude
    print("Extracting contract data using Claude AI...")
    raw_contract_data = extract_contract_data(text)

    # Standardize the data
    contract_data = standardize_and_validate(raw_contract_data)

    # Generate output filename if not provided
    if output_filename is None:
        pdf_name = Path(pdf_path).stem
        output_filename = f"{pdf_name}_extracted.xlsx"

    # Export to Excel
    print(f"Exporting to Excel: {output_filename}")
    export_to_excel(contract_data, output_filename)

    print("Processing complete!")


def main():
    """
    Main entry point for the TCP processing agent.
    """
    # Check if API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key.")
        return

    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Example usage: process all PDFs in sample_contracts folder
    pdf_files = list(CONTRACTS_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {CONTRACTS_DIR}")
        print("Please add TCP contract PDFs to the sample_contracts folder.")
        return

    print(f"Found {len(pdf_files)} PDF file(s) to process.")

    for pdf_file in pdf_files:
        try:
            process_contract(str(pdf_file))
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")


if __name__ == "__main__":
    main()
