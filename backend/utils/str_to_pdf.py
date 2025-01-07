from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

def save_string_to_pdf(text, filename):
    # Create a SimpleDocTemplate with letter size
    doc = SimpleDocTemplate(filename, pagesize=letter)

    # Define custom styles for headings and body text
    heading_style = ParagraphStyle(
        name="Heading",
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,  # Line spacing for heading
        alignment=TA_LEFT,
        spaceAfter=14,  # Space after heading
        textColor=colors.black
    )

    body_style = ParagraphStyle(
        name="Body",
        fontName='Times-Roman',
        fontSize=12,
        leading=14,  # Line spacing for body text
        alignment=TA_LEFT,
        textColor=colors.black
    )

    # Split the input text by newlines to create individual paragraphs
    lines = text.split('\n')

    # List to hold paragraphs
    story = []

    # Add a heading if necessary
    # story.append(Paragraph("Cover Letter", heading_style))
    # story.append(Spacer(1, 24))  # Add space after the heading

    # Create a Paragraph object for each line of the body text
    for line in lines:
        if line.strip():  # Only create a paragraph if the line is not empty
            paragraph = Paragraph(line, body_style)
            story.append(paragraph)
            story.append(Spacer(1, 12))  # Add space between paragraphs (12 points)

    # Build the PDF document
    doc.build(story)
