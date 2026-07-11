from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def save_string_to_pdf(text, filename):
    # Create a SimpleDocTemplate with letter size
    doc = SimpleDocTemplate(filename, pagesize=letter)

    body_style = ParagraphStyle(
        name="Body",
        fontName="Times-Roman",
        fontSize=12,
        leading=14,  # Line spacing for body text
        alignment=TA_LEFT,
        textColor=colors.black,
    )

    # Split the input text by newlines to create individual paragraphs
    lines = text.split("\n")

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
