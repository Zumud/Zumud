from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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


if __name__ == "__main__":

    test_text = """
    Lorem ipsum\n dolor sit amet, consectetur adipiscing elit. Curabitur dignissim ligula et nisi facilisis, 
    et consectetur neque pharetra. Quisque finibus justo vitae mauris sodales, sit amet gravida mi pellentesque. 
    Sed vulputate risus ut quam scelerisque convallis. \nNullam nec vehicula est. Duis in lectus id velit commodo sodales. 
    Maecenas varius mauris et libero pharetra, a facilisis ipsum interdum.
    """
    text = """Dear Hiring manager,\nThis is an example string. \n It contains multiple lines.gfnbjbjjjjjjgfnbjbjjjjjjgfnbjbjjjjjjgfnbjbjjjjjjgfnbjbjjjjjjgfnbjbjjjjjjgfnbjbjjjjjjgfnbjbjjjjjjgfnbjbjjjjjjgfnbjbjjjjjj
            Each new line will be processed properly."""
    
    text = """Dear Hiring Manager,

    I am writing to apply for the Data Engineer position at your esteemed company.
    My experience and technical expertise make me an ideal candidate for this role.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    I look forward to the opportunity to contribute to your team.

    Sincerely,
    Mohammad"""
    save_string_to_pdf(text, "output.pdf")

    # Call the function with the test case
    # write_string_to_pdf("test_output.pdf", test_text)