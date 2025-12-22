"""
Generate PDF versions of TCP contracts with different layouts
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from pathlib import Path


def read_contract(file_path):
    """Read contract text file and return content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_bulk_carrier_pdf(text_content, output_path):
    """
    Layout 1: Traditional formal layout
    - Letter size
    - Times Roman font
    - Justified text
    - Wide margins
    - Section headers in bold
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=1.25*inch,
        rightMargin=1.25*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles for this layout
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=30,
        spaceBefore=20
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName='Times-Bold',
        fontSize=12,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.black
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName='Times-Roman',
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leading=14
    )

    story = []
    lines = text_content.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.15*inch))
            continue

        # Title
        if line == "TIME CHARTER PARTY":
            story.append(Paragraph(line, title_style))
        # Main section headers (ALL CAPS with colons)
        elif line.isupper() and line.endswith(':'):
            story.append(Paragraph(line, heading_style))
        # Regular text
        else:
            # Escape special characters for XML
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(line, body_style))

    doc.build(story)
    print(f"Generated: {output_path}")


def generate_tanker_pdf(text_content, output_path):
    """
    Layout 2: Modern business layout
    - A4 size
    - Helvetica font
    - Left-aligned text
    - Moderate margins
    - Blue section headers
    - Two-column layout for some sections
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=0.8*inch,
        rightMargin=0.8*inch,
        topMargin=0.9*inch,
        bottomMargin=0.9*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles for modern look
    title_style = ParagraphStyle(
        'ModernTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        alignment=TA_LEFT,
        spaceAfter=20,
        spaceBefore=10,
        textColor=colors.HexColor('#1a5490')
    )

    heading_style = ParagraphStyle(
        'ModernHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.HexColor('#2e75b6'),
        borderPadding=5,
        backColor=colors.HexColor('#e8f2f9')
    )

    body_style = ParagraphStyle(
        'ModernBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        alignment=TA_LEFT,
        spaceAfter=5,
        leading=13
    )

    story = []
    lines = text_content.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.1*inch))
            continue

        # Title
        if line == "TIME CHARTER PARTY":
            story.append(Paragraph(line, title_style))
            story.append(Spacer(1, 0.2*inch))
        # Main section headers
        elif line.isupper() and line.endswith(':'):
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(line, heading_style))
        # Regular text
        else:
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(line, body_style))

    doc.build(story)
    print(f"Generated: {output_path}")


def generate_container_pdf(text_content, output_path):
    """
    Layout 3: Compact professional layout
    - Letter size
    - Courier font (monospace for technical feel)
    - Narrow margins
    - Small font
    - Gray shaded headers
    - Dense layout
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.6*inch,
        rightMargin=0.6*inch,
        topMargin=0.7*inch,
        bottomMargin=0.7*inch
    )

    styles = getSampleStyleSheet()

    # Compact technical style
    title_style = ParagraphStyle(
        'CompactTitle',
        parent=styles['Heading1'],
        fontName='Courier-Bold',
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=15,
        spaceBefore=10
    )

    heading_style = ParagraphStyle(
        'CompactHeading',
        parent=styles['Heading2'],
        fontName='Courier-Bold',
        fontSize=10,
        spaceAfter=6,
        spaceBefore=10,
        textColor=colors.black,
        backColor=colors.HexColor('#d9d9d9'),
        borderPadding=3
    )

    body_style = ParagraphStyle(
        'CompactBody',
        parent=styles['BodyText'],
        fontName='Courier',
        fontSize=8,
        alignment=TA_LEFT,
        spaceAfter=3,
        leading=10
    )

    story = []
    lines = text_content.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.08*inch))
            continue

        # Title
        if line == "TIME CHARTER PARTY":
            story.append(Paragraph(line, title_style))
        # Main section headers
        elif line.isupper() and line.endswith(':'):
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(line, heading_style))
        # Regular text
        else:
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(line, body_style))

    doc.build(story)
    print(f"Generated: {output_path}")


def main():
    """Generate all three PDF contracts with different layouts."""
    contracts_dir = Path("sample_contracts")

    # Contract 1: Bulk Carrier - Traditional formal layout
    print("Generating bulk carrier contract PDF (Traditional layout)...")
    text1 = read_contract(contracts_dir / "tcp_contract_001.txt")
    generate_bulk_carrier_pdf(text1, str(contracts_dir / "tcp_contract_001.pdf"))

    # Contract 2: Tanker - Modern business layout
    print("\nGenerating tanker contract PDF (Modern layout)...")
    text2 = read_contract(contracts_dir / "tcp_contract_002.txt")
    generate_tanker_pdf(text2, str(contracts_dir / "tcp_contract_002.pdf"))

    # Contract 3: Container - Compact professional layout
    print("\nGenerating container vessel contract PDF (Compact layout)...")
    text3 = read_contract(contracts_dir / "tcp_contract_003.txt")
    generate_container_pdf(text3, str(contracts_dir / "tcp_contract_003.pdf"))

    print("\n" + "="*60)
    print("All PDFs generated successfully!")
    print("="*60)
    print("\nLayout differences:")
    print("1. tcp_contract_001.pdf - Traditional formal layout:")
    print("   - Times Roman font, justified text, wide margins")
    print("2. tcp_contract_002.pdf - Modern business layout:")
    print("   - Helvetica font, blue headers, A4 size")
    print("3. tcp_contract_003.pdf - Compact professional layout:")
    print("   - Courier monospace font, gray headers, dense layout")


if __name__ == "__main__":
    main()
