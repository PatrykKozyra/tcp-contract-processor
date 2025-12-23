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

    # Create prompt for contract data extraction - Updated to match Excel template (53 fields)
    prompt = f"""Please analyze this Time Charter Party (TCP) contract and extract the following information into a structured format.

CONTRACT TEXT:
{text}

Please extract and return ONLY the following fields in valid JSON format. If a field is not found or not applicable, use null or "-" for text fields:

{{
    "VESSEL NAME": "Full name of the vessel (e.g., M/T ADVANTAGE ATOM)",
    "TRADE": "Type of trade/cargo (e.g., CRUDE, CLEAN, LNG, PRODUCTS)",
    "TYPE AUTO.": "Vessel size/type category (e.g., Aframax, VLCC, Suezmax, Panamax)",
    "TCP DATE": "Date of the charter party contract",
    "CONTRACT TYPE": "Contract type classification (e.g., EXTERNAL, INTERNAL)",
    "OWNERS.": "Owner's company name",
    "CHARTERERS": "Charterer's company name",
    "CHARTER LENGTH": "Charter period description (e.g., '3 YEARS +/- 30 DAYS')",
    "OPTION PERIODS": "Description of option periods, if any (use 'N/A.' if none)",
    "LENGTH OF NEXT OPTION": "Duration of next option period (use null if N/A)",
    "NUMBER OF DAYS PRIOR REDELIVERY DATE TO DECLARE THE OPTION": "Days before redelivery to declare option (numeric)",
    "OPTION DECLARATION DATE.": "Date by which option must be declared",
    "STTC/ LTTC": "Charter duration type: STTC (Short Term) or LTTC (Long Term)",
    "DELIVERY DATE": "Delivery date",
    "REDELIVERY DATE": "Redelivery date",
    "REDEL CHOP minus DAYS": "Days before redelivery date (charterer's option - numeric)",
    "REDEL CHOP plus DAYS": "Days after redelivery date (charterer's option - numeric)",
    "REDELIVERY LOCATION": "Detailed redelivery location description",
    "FIRST REDEL NOTICE": "First redelivery notice in days (numeric)",
    "EARLIEST REDELIVERY DATE.": "Earliest possible redelivery date",
    "LATEST REDELIVERY DATE.": "Latest possible redelivery date",
    "EARLIEST REDELIVERY NOTICE DATE.": "Earliest date for redelivery notice",
    "LATEST REDELIVERY NOTICE DATE": "Latest date for redelivery notice",
    "ALL REDEL NOTICES": "Complete redelivery notice schedule - extract exact text (e.g., 'Approx.: 20,15,10,7 days approximate and 5,3,2,1 definite days prior notice of redelivery')",
    "LAST CARGOES ON REDELIVERY": "Allowed last cargoes before redelivery (e.g., 'CRUDE OIL OR DIRTY PETROLEUM PRODUCTS')",
    "SLOPS ON REDELIVERY": "Slops requirements on redelivery (use '-' if not specified)",
    "CLEANING REQUIREMENTS ON REDELIVERY": "Cleaning requirements on redelivery (use '-' if not specified)",
    "CAN OFFHIRE BE ADDED?(CL 4(B))": "Can charterers add offhire time before redelivery? (Yes/No)",
    "NUMBER OF DAYS PRIOR REDELIVERY DATE TO DECLARE THIS": "Days before redelivery to declare offhire addition (numeric)",
    "OFFHIRE DECLARATION DATE(CL 4(B))": "Deadline date to declare offhire addition",
    "OTHER REDELIVERY TERMS (E#G BALLAST BONUS)": "Other redelivery terms like ballast bonus (use '-' if none)",
    "BUNKERS ON REDELIVERY(CL 15)": "Bunkers description on redelivery (e.g., 'FIFO BASIS / VESSEL TO BE DELIVERED AND REDELIVERED...')",
    "CURRENT TC RATE(CL 8)": "Current time charter rate per day (e.g., '35,000' for USD 35,000)",
    "FIXED/ MARKET RELATED": "Rate type: FIXED or MARKET RELATED",
    "BENEFICIAL OWNER (FROM BANK DETAILS)": "Beneficial owner name from bank details",
    "DRY-DOCK LOCATION": "Location of drydock (use '-' if not specified)",
    "BROKER": "Broker name (use '-' if not specified)",
    "BROKERS EMAIL": "Broker email address (use '-' if not specified)",
    "Original Annual Anniversary Date": "Original annual anniversary date (use '-' if not specified)",
    "Revised Annual Anniversary Date": "Revised annual anniversary date (use '-' if not specified)",
    "IMO NUMBER": "IMO number (numeric)",
    "BUILT": "Year vessel was built (numeric year)",
    "FLAG": "Vessel flag/registry (e.g., 'MARSHALL ISLANDS')",
    "VESSEL EMAIL": "Vessel email address",
    "OWNER EMAIL ADDRESS": "Owner's email address",
    "TECHNICAL MANAGER": "Technical manager company name",
    "TECHNICAL MANAGER EMAIL ADDRESS": "Technical manager email address",
    "P&I CLUB": "Protection and Indemnity Club name (e.g., 'WEST OF ENGLAND')",
    "H&M VALUE USDM": "Hull & Machinery insurance value in USD millions (e.g., '$55M (FOR 2018)')",
    "CLASSIFICATION SOCIETY": "Classification society name (e.g., 'DET NORSKE VERITAS', 'LLOYD'S REGISTER')",
    "IMO TYPE": "IMO ship type classification (use '-' if not specified)",
    "ICE CLASS": "Ice class rating (use '-' if not specified)",
    "DWT": "Deadweight tonnage (numeric)"
}}

IMPORTANT NOTES:
- Return ONLY valid JSON with these exact field names (case-sensitive, including punctuation)
- Use null for dates/numbers that are not found
- Use "-" for text fields that are not specified or not applicable
- For dates, use YYYY-MM-DD format if possible
- For ALL REDEL NOTICES, extract the complete notice schedule text exactly as written
- Extract numeric values without currency symbols or units where specified
- If contract uses different terminology, infer the equivalent field value

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
                max_tokens=3000,  # Increased for 53 fields (was 2000 for 33 fields)
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
