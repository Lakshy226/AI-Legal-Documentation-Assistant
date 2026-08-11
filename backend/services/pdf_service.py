# Import regular expressions for detecting document sections.
import re

# Import ReportLab's PDF document builder.
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

# Import A4 page size.
from reportlab.lib.pagesizes import A4

# Import ReportLab styles.
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

# Import text alignment constants.
from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT,
    TA_JUSTIFY
)

# Import measurement units.
from reportlab.lib.units import mm

# Import colors.
from reportlab.lib import colors

# Import HTML escaping.
from xml.sax.saxutils import escape


# ---------------------------------------------------------
# PAGE HEADER / FOOTER
# ---------------------------------------------------------

def draw_page(canvas, document):

    # Save the current canvas state.
    canvas.saveState()

    # Get the current page number.
    page_number = canvas.getPageNumber()

    # Set header/footer color.
    canvas.setFillColor(
        colors.HexColor("#4B5563")
    )

    # Draw application name.
    canvas.setFont(
        "Helvetica-Bold",
        8
    )

    canvas.drawString(
        22 * mm,
        287 * mm,
        "LegalEase AI"
    )

    # Draw page number.
    canvas.setFont(
        "Helvetica",
        8
    )

    canvas.drawRightString(
        188 * mm,
        10 * mm,
        f"Page {page_number}"
    )

    # Draw footer disclaimer.
    canvas.drawString(
        22 * mm,
        10 * mm,
        "AI-generated draft • Review with a qualified legal professional"
    )

    # Draw header line.
    canvas.setStrokeColor(
        colors.HexColor("#D1D5DB")
    )

    canvas.line(
        22 * mm,
        283 * mm,
        188 * mm,
        283 * mm
    )

    # Draw footer line.
    canvas.line(
        22 * mm,
        14 * mm,
        188 * mm,
        14 * mm
    )

    # Restore canvas.
    canvas.restoreState()


# ---------------------------------------------------------
# PDF GENERATOR
# ---------------------------------------------------------

def create_pdf(
    title,
    content,
    output_path
):

    # Create the PDF using A4 paper.
    pdf = SimpleDocTemplate(
        output_path,
        pagesize=A4,

        # Left margin.
        leftMargin=22 * mm,

        # Right margin.
        rightMargin=22 * mm,

        # Top margin.
        topMargin=30 * mm,

        # Bottom margin.
        bottomMargin=22 * mm,

        # PDF metadata.
        title=title,
        author="LegalEase AI"
    )

    # Load ReportLab's default styles.
    styles = getSampleStyleSheet()

    # -----------------------------------------------------
    # CUSTOM STYLES
    # -----------------------------------------------------

    # Main title.
    title_style = ParagraphStyle(
        "LegalTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827"),
        spaceAfter=6 * mm
    )

    # Section heading such as "1. PARTIES".
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#111827"),
        spaceBefore=7 * mm,
        spaceAfter=3 * mm,
        keepWithNext=True
    )

    # Subsection heading such as "1.1 Landlord".
    subsection_style = ParagraphStyle(
        "Subsection",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#374151"),
        spaceBefore=3 * mm,
        spaceAfter=2 * mm,
        keepWithNext=True
    )

    # Normal legal clause.
    clause_style = ParagraphStyle(
        "Clause",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#1F2937"),
        spaceAfter=3 * mm
    )

    # Field label.
    label_style = ParagraphStyle(
        "Label",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#111827"),
        spaceAfter=1 * mm
    )

    # Signature text.
    signature_style = ParagraphStyle(
        "Signature",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#111827")
    )

    # Disclaimer.
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["BodyText"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#6B7280"),
        spaceBefore=6 * mm
    )

    # -----------------------------------------------------
    # DOCUMENT ELEMENTS
    # -----------------------------------------------------

    # Store PDF components.
    elements = []

    # Add application name.
    elements.append(
        Paragraph(
            "LEGALEASE AI",
            ParagraphStyle(
                "AppName",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#6B7280"),
                spaceAfter=2 * mm
            )
        )
    )

    # Add document title.
    elements.append(
        Paragraph(
            escape(title.upper()),
            title_style
        )
    )

    # Add title divider.
    divider = Table(
        [[""]],
        colWidths=[166 * mm],
        rowHeights=[0.7 * mm]
    )

    # Style divider.
    divider.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor("#374151")
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                0
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                0
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                0
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                0
            )
        ])
    )

    # Add divider.
    elements.append(divider)

    # Add spacing.
    elements.append(
        Spacer(
            1,
            6 * mm
        )
    )

    # Normalize line endings.
    content = content.replace(
        "\r\n",
        "\n"
    ).replace(
        "\r",
        "\n"
    )

    # Split document into lines.
    lines = content.split("\n")

    # Track whether we are inside the signature section.
    in_signatures = False

    # -----------------------------------------------------
    # PARSE GENERATED DOCUMENT
    # -----------------------------------------------------

    for raw_line in lines:

        # Remove surrounding whitespace.
        line = raw_line.strip()

        # Ignore empty lines.
        if not line:

            elements.append(
                Spacer(
                    1,
                    2 * mm
                )
            )

            continue

        # Remove Markdown heading symbols if the AI accidentally uses them.
        line = re.sub(
            r"^#{1,3}\s+",
            "",
            line
        ).strip()

        # -------------------------------------------------
        # MAJOR SECTION
        # -------------------------------------------------

        # Detect:
        # 1. PARTIES
        # 2. PROPERTY
        # 3. RENT AND PAYMENT
        section_match = re.match(
            r"^(\d+)\.\s+(.+)$",
            line
        )

        if section_match:

            # Extract section number.
            section_number = section_match.group(1)

            # Extract section title.
            section_title = section_match.group(2).strip()

            # Check for signature section.
            if (
                "SIGNATURE" in
                section_title.upper()
            ):
                in_signatures = True

            # Create section heading.
            elements.append(
                Paragraph(
                    (
                        f"<b>{escape(section_number)}. "
                        f"{escape(section_title.upper())}</b>"
                    ),
                    section_style
                )
            )

            # Add a small divider below section heading.
            section_line = Table(
                [[""]],
                colWidths=[166 * mm],
                rowHeights=[0.4 * mm]
            )

            section_line.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor("#D1D5DB")
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        0
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        0
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        0
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        0
                    )
                ])
            )

            elements.append(section_line)

            continue

        # -------------------------------------------------
        # SUBSECTION
        # -------------------------------------------------

        # Detect:
        # 1.1 Landlord
        # 1.2 Tenant
        # 2.1 Property Address
        subsection_match = re.match(
            r"^(\d+\.\d+)\s+(.+)$",
            line
        )

        if subsection_match:

            # Extract subsection number.
            subsection_number = subsection_match.group(1)

            # Extract subsection title.
            subsection_title = subsection_match.group(2)

            # Add subsection heading.
            elements.append(
                Paragraph(
                    (
                        f"<b>{escape(subsection_number)} "
                        f"{escape(subsection_title)}</b>"
                    ),
                    subsection_style
                )
            )

            continue

        # -------------------------------------------------
        # LABEL
        # -------------------------------------------------

        # Detect:
        # Name:
        # Address:
        # Monthly Rent:
        # Signature:
        label_match = re.match(
            r"^([^:]{1,60}):\s*(.*)$",
            line
        )

        if label_match:

            # Extract label.
            label = label_match.group(1).strip()

            # Extract value.
            value = label_match.group(2).strip()

            # If this is a label with a value,
            # display it as a structured field.
            if value:

                # Create a two-column field table.
                field_table = Table(
                    [[
                        Paragraph(
                            escape(label),
                            label_style
                        ),
                        Paragraph(
                            escape(value),
                            clause_style
                        )
                    ]],
                    colWidths=[
                        42 * mm,
                        124 * mm
                    ]
                )

                # Remove table borders.
                field_table.setStyle(
                    TableStyle([
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP"
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            2
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            2
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            2
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            2
                        )
                    ])
                )

                elements.append(field_table)

                continue

            # Label without value.
            elements.append(
                Paragraph(
                    escape(label),
                    label_style
                )
            )

            continue

        # -------------------------------------------------
        # SIGNATURES
        # -------------------------------------------------

        if in_signatures:

            # Create normal signature content.
            elements.append(
                Paragraph(
                    escape(line),
                    signature_style
                )
            )

            continue

        # -------------------------------------------------
        # NORMAL CLAUSE
        # -------------------------------------------------

        # Everything else becomes an individual clause.
        elements.append(
            Paragraph(
                escape(line),
                clause_style
            )
        )

    # -----------------------------------------------------
    # DISCLAIMER
    # -----------------------------------------------------

    # Add spacing before disclaimer.
    elements.append(
        Spacer(
            1,
            8 * mm
        )
    )

    # Add disclaimer.
    elements.append(
        Paragraph(
            "<b>DISCLAIMER:</b> This document is an "
            "AI-generated first draft and does not "
            "constitute legal advice. Review it with "
            "a qualified legal professional before "
            "signing or relying upon it.",
            disclaimer_style
        )
    )

    # Build PDF.
    pdf.build(
        elements,
        onFirstPage=draw_page,
        onLaterPages=draw_page
    )

    # Return generated PDF path.
    return output_path
