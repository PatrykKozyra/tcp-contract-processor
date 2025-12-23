"""
TCP Contract Processing - Streamlit Web UI

Simple web interface for processing and managing TCP contracts.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import io
from datetime import datetime

# Import from existing modules
from src.main import (
    extract_text_from_pdf,
    extract_contract_data,
    OUTPUT_DIR
)
from src.data_standardization import standardize_and_validate, TCPDataStandardizer


# Page configuration
st.set_page_config(
    page_title="TCP Contract Processor",
    page_icon="📄",
    layout="wide"
)


# Initialize session state
if 'contracts' not in st.session_state:
    st.session_state.contracts = []


def process_pdf_file(pdf_file) -> dict:
    """
    Process an uploaded PDF file.

    Args:
        pdf_file: Streamlit UploadedFile object

    Returns:
        Standardized contract data dictionary
    """
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(pdf_file.read())
        tmp_path = tmp_file.name

    try:
        # Extract text from PDF
        text = extract_text_from_pdf(tmp_path)

        # Extract structured data using Claude
        raw_contract_data = extract_contract_data(text)

        # Standardize the data
        contract_data = standardize_and_validate(raw_contract_data)

        # Add metadata
        contract_data['_source_file'] = pdf_file.name
        contract_data['_processed_at'] = datetime.now().isoformat()

        return contract_data

    finally:
        # Clean up temporary file
        Path(tmp_path).unlink(missing_ok=True)


def create_excel_download(contracts: list) -> bytes:
    """
    Create Excel file from contracts list.

    Args:
        contracts: List of contract dictionaries

    Returns:
        Excel file as bytes
    """
    df = TCPDataStandardizer.create_columnar_dataframe(contracts)

    # Create Excel file in memory
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl', sheet_name='TCP Contracts')
    output.seek(0)

    return output.getvalue()


def filter_contracts_by_vessel(contracts: list, vessel_name: str) -> list:
    """
    Filter contracts by vessel name (case-insensitive partial match).

    Args:
        contracts: List of contract dictionaries
        vessel_name: Vessel name to search for

    Returns:
        Filtered list of contracts sorted by contract_date descending
    """
    if not vessel_name:
        return contracts

    vessel_name_upper = vessel_name.upper()

    filtered = [
        contract for contract in contracts
        if contract.get('VESSEL NAME') and
        vessel_name_upper in contract['VESSEL NAME'].upper()
    ]

    # Sort by TCP DATE descending
    filtered.sort(
        key=lambda x: x.get('TCP DATE') or '0000-00-00',
        reverse=True
    )

    return filtered


# Main UI
st.title("📄 TCP Contract Processor")
st.markdown("AI-powered extraction and management of Time Charter Party contracts")

# Sidebar
with st.sidebar:
    st.header("About")
    st.info(
        "Upload PDF contracts to extract structured data using Claude AI. "
        "Search, view, and export your contract data to Excel."
    )

    st.header("Statistics")
    st.metric("Total Contracts", len(st.session_state.contracts))

    if st.session_state.contracts:
        vessels = [c.get('vessel_name', 'N/A') for c in st.session_state.contracts]
        unique_vessels = len(set(vessels))
        st.metric("Unique Vessels", unique_vessels)

    if st.button("Clear All Contracts", type="secondary"):
        st.session_state.contracts = []
        st.rerun()

# Main content area
tab1, tab2 = st.tabs(["📤 Upload & Process", "🔍 View & Search"])

# Tab 1: Upload & Process
with tab1:
    st.header("Upload PDF Contracts")

    uploaded_files = st.file_uploader(
        "Choose PDF file(s)",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more TCP contract PDF files"
    )

    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} file(s)")

        col1, col2 = st.columns([1, 3])

        with col1:
            process_button = st.button(
                "🚀 Process Contracts",
                type="primary",
                use_container_width=True
            )

        if process_button:
            progress_bar = st.progress(0)
            status_text = st.empty()

            successful = 0
            failed = 0

            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name}...")

                try:
                    with st.spinner(f"Extracting data from {uploaded_file.name}..."):
                        contract_data = process_pdf_file(uploaded_file)
                        st.session_state.contracts.append(contract_data)
                        successful += 1

                        st.success(
                            f"✓ {uploaded_file.name} - "
                            f"Vessel: {contract_data.get('vessel_name', 'N/A')}"
                        )

                except Exception as e:
                    failed += 1
                    st.error(f"✗ {uploaded_file.name} - Error: {str(e)}")

                progress_bar.progress((i + 1) / len(uploaded_files))

            status_text.text("Processing complete!")

            st.info(
                f"**Summary:** {successful} successful, {failed} failed out of {len(uploaded_files)} total"
            )

            if successful > 0:
                st.balloons()

# Tab 2: View & Search
with tab2:
    st.header("Contract Database")

    if not st.session_state.contracts:
        st.info("No contracts processed yet. Upload and process PDF files in the 'Upload & Process' tab.")

    else:
        # Search bar
        col1, col2 = st.columns([3, 1])

        with col1:
            search_query = st.text_input(
                "🔍 Search by vessel name",
                placeholder="Enter vessel name (e.g., Pacific Star)",
                help="Case-insensitive partial match"
            )

        with col2:
            st.write("")  # Spacer
            st.write("")  # Spacer
            show_all = st.checkbox("Show all fields", value=False)

        # Filter contracts
        filtered_contracts = filter_contracts_by_vessel(
            st.session_state.contracts,
            search_query
        )

        st.markdown(f"**Showing {len(filtered_contracts)} contract(s)**")

        if filtered_contracts:
            # Create DataFrame
            df = TCPDataStandardizer.create_columnar_dataframe(filtered_contracts)

            # Select columns to display
            if show_all:
                display_df = df
            else:
                # Show most important columns (updated for 53-field structure)
                important_cols = [
                    'VESSEL NAME', 'TCP DATE', 'TRADE', 'TYPE AUTO.',
                    'CHARTERERS', 'CHARTER LENGTH', 'CURRENT TC RATE(CL 8)',
                    'DELIVERY DATE', 'REDELIVERY DATE', 'REDELIVERY LOCATION',
                    '_source_file'
                ]
                display_cols = [col for col in important_cols if col in df.columns]
                display_df = df[display_cols]

            # Display data table
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

            # Download section
            st.markdown("---")
            st.subheader("Export Data")

            col1, col2, col3 = st.columns([2, 2, 2])

            with col1:
                # Excel download
                excel_data = create_excel_download(filtered_contracts)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"tcp_contracts_{timestamp}.xlsx"

                st.download_button(
                    label="📥 Download as Excel",
                    data=excel_data,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            with col2:
                # CSV download
                csv_data = df.to_csv(index=False)

                st.download_button(
                    label="📥 Download as CSV",
                    data=csv_data,
                    file_name=f"tcp_contracts_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            # Detailed view
            st.markdown("---")
            st.subheader("Detailed Contract View")

            if len(filtered_contracts) > 0:
                # Select contract to view
                vessel_options = [
                    f"{c.get('VESSEL NAME', 'N/A')} - {c.get('TCP DATE', 'N/A')}"
                    for c in filtered_contracts
                ]

                selected_idx = st.selectbox(
                    "Select contract to view details:",
                    range(len(vessel_options)),
                    format_func=lambda i: vessel_options[i]
                )

                selected_contract = filtered_contracts[selected_idx]

                # Display in expandable sections - Updated for 53-field structure
                with st.expander("📋 Basic Information", expanded=True):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Contract Details**")
                        st.write(f"TCP Date: {selected_contract.get('TCP DATE', 'N/A')}")
                        st.write(f"Contract Type: {selected_contract.get('CONTRACT TYPE', 'N/A')}")
                        st.write(f"STTC/LTTC: {selected_contract.get('STTC/ LTTC', 'N/A')}")
                        st.write(f"Source File: {selected_contract.get('_source_file', 'N/A')}")

                    with col2:
                        st.write("**Vessel Information**")
                        st.write(f"Vessel Name: {selected_contract.get('VESSEL NAME', 'N/A')}")
                        st.write(f"IMO Number: {selected_contract.get('IMO NUMBER', 'N/A')}")
                        st.write(f"Type: {selected_contract.get('TYPE AUTO.', 'N/A')}")
                        st.write(f"Trade: {selected_contract.get('TRADE', 'N/A')}")
                        st.write(f"Built: {selected_contract.get('BUILT', 'N/A')}")
                        st.write(f"Flag: {selected_contract.get('FLAG', 'N/A')}")
                        st.write(f"DWT: {selected_contract.get('DWT', 'N/A')}")

                with st.expander("🤝 Parties & Contacts"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Owners**")
                        st.write(f"Name: {selected_contract.get('OWNERS.', 'N/A')}")
                        st.write(f"Beneficial Owner: {selected_contract.get('BENEFICIAL OWNER (FROM BANK DETAILS)', 'N/A')}")
                        st.write(f"Email: {selected_contract.get('OWNER EMAIL ADDRESS', 'N/A')}")
                        st.write(f"Technical Manager: {selected_contract.get('TECHNICAL MANAGER', 'N/A')}")
                        st.write(f"Tech Manager Email: {selected_contract.get('TECHNICAL MANAGER EMAIL ADDRESS', 'N/A')}")

                    with col2:
                        st.write("**Charterers**")
                        st.write(f"Name: {selected_contract.get('CHARTERERS', 'N/A')}")
                        st.write("")
                        st.write("**Other Contacts**")
                        st.write(f"Broker: {selected_contract.get('BROKER', 'N/A')}")
                        st.write(f"Broker Email: {selected_contract.get('BROKERS EMAIL', 'N/A')}")
                        st.write(f"Vessel Email: {selected_contract.get('VESSEL EMAIL', 'N/A')}")

                with st.expander("💰 Commercial Terms"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Charter Length:** {selected_contract.get('CHARTER LENGTH', 'N/A')}")
                        st.write(f"**Current TC Rate:** ${selected_contract.get('CURRENT TC RATE(CL 8)', 'N/A')}")
                        st.write(f"**Rate Type:** {selected_contract.get('FIXED/ MARKET RELATED', 'N/A')}")

                    with col2:
                        st.write(f"**Option Periods:** {selected_contract.get('OPTION PERIODS', 'N/A')}")
                        st.write(f"**Length of Next Option:** {selected_contract.get('LENGTH OF NEXT OPTION', 'N/A')}")
                        st.write(f"**Option Declaration Date:** {selected_contract.get('OPTION DECLARATION DATE.', 'N/A')}")

                with st.expander("🚢 Delivery & Redelivery"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Delivery**")
                        st.write(f"Date: {selected_contract.get('DELIVERY DATE', 'N/A')}")

                    with col2:
                        st.write("**Redelivery**")
                        st.write(f"Date: {selected_contract.get('REDELIVERY DATE', 'N/A')}")
                        st.write(f"Location: {selected_contract.get('REDELIVERY LOCATION', 'N/A')}")
                        st.write(f"Earliest Date: {selected_contract.get('EARLIEST REDELIVERY DATE.', 'N/A')}")
                        st.write(f"Latest Date: {selected_contract.get('LATEST REDELIVERY DATE.', 'N/A')}")

                with st.expander("📅 Redelivery Details"):
                    st.write(f"**Notice Schedule:** {selected_contract.get('ALL REDEL NOTICES', 'N/A')}")
                    st.write(f"**First Notice (days):** {selected_contract.get('FIRST REDEL NOTICE', 'N/A')}")
                    st.write(f"**Chop -/+ Days:** {selected_contract.get('REDEL CHOP minus DAYS', 'N/A')} / {selected_contract.get('REDEL CHOP plus DAYS', 'N/A')}")
                    st.write(f"**Last Cargoes:** {selected_contract.get('LAST CARGOES ON REDELIVERY', 'N/A')}")
                    st.write(f"**Bunkers on Redelivery:** {selected_contract.get('BUNKERS ON REDELIVERY(CL 15)', 'N/A')}")
                    st.write(f"**Can Offhire be Added:** {selected_contract.get('CAN OFFHIRE BE ADDED?(CL 4(B))', 'N/A')}")
                    st.write(f"**Other Terms:** {selected_contract.get('OTHER REDELIVERY TERMS (E#G BALLAST BONUS)', 'N/A')}")

                with st.expander("⚓ Technical & Classification"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Classification Society:** {selected_contract.get('CLASSIFICATION SOCIETY', 'N/A')}")
                        st.write(f"**P&I Club:** {selected_contract.get('P&I CLUB', 'N/A')}")
                        st.write(f"**H&M Value:** {selected_contract.get('H&M VALUE USDM', 'N/A')}")

                    with col2:
                        st.write(f"**IMO Type:** {selected_contract.get('IMO TYPE', 'N/A')}")
                        st.write(f"**Ice Class:** {selected_contract.get('ICE CLASS', 'N/A')}")
                        st.write(f"**Drydock Location:** {selected_contract.get('DRY-DOCK LOCATION', 'N/A')}")

        else:
            st.warning(f"No contracts found matching '{search_query}'")

# Footer
st.markdown("---")
st.caption("Powered by Claude AI | Built with Streamlit")
