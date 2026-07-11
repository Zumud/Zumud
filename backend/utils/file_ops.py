import datetime
import io
import os
import re
import tarfile

import pypdf
import requests
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from backend.config.config import TAR_FOLDER_NAME, TEX_FILE_NAME
from backend.config.envs import LaTeX_COMPILER_URL_DATA
from backend.utils.log import logger


def escape_latex(data):
    """
    Recursively escape LaTeX special characters in a data structure (string, list, or dict).

    Args:
        data: The data to escape (string, list, or dict)

    Returns:
        The input data with all LaTeX special characters escaped
    """
    if isinstance(data, str):
        # Handle backslash first to avoid affecting other replacements
        text = data.replace("\\", r"\textbackslash{}")

        # Then handle other special characters
        text = text.replace("&", r"\&")
        text = text.replace("%", r"\%")
        text = text.replace("$", r"\$")
        text = text.replace("#", r"\#")
        text = text.replace("_", r"\_")
        text = text.replace("{", r"\{")
        text = text.replace("}", r"\}")
        text = text.replace("~", r"\textasciitilde{}")
        text = text.replace("^", r"\textasciicircum{}")
        text = text.replace("<", r"\textless{}")
        text = text.replace(">", r"\textgreater{}")

        return text
    elif isinstance(data, list):
        return [escape_latex(item) for item in data]
    elif isinstance(data, dict):
        return {k: escape_latex(v) for k, v in data.items()}
    else:
        return data


def generate_tex_and_tar(
    save_folder: str,
    latex_content: str,
    file_name: str = "resume",
    folder_name: str = "resume",
):
    """
    Creates a folder, generates a .tex file inside it, and compresses the folder into a .tar file.

    Parameters:
        file_name (str): The name of the .tex file to create.
        latex_content (str): The LaTeX content to write into the file.
        folder_name (str): The name of the folder to create.
    """
    try:
        # Path of a folder for saving .tex files
        resume_folder_path = save_folder

        # Path of .tar file
        tar_path = save_folder

        # Ensure the folder exists
        os.makedirs(save_folder, exist_ok=True)

        # Full path for the .tex file
        tex_file_path = os.path.join(resume_folder_path, file_name)

        # Ensure the file name ends with .tex
        if not tex_file_path.endswith(".tex"):
            tex_file_path += ".tex"

        # Strip ASCII control chars (keep \t \n \r) — pdflatex chokes on them and
        # LLMs occasionally emit stray ones (e.g. U+0016) when transcribing RTL text.
        latex_content = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", latex_content)

        # Write the LaTeX content into the file
        with open(tex_file_path, "w", encoding="utf-8") as tex_file:
            tex_file.write(latex_content)

        logger.debug(f"File '{tex_file_path}' created successfully.")

        # Compress the folder into a .tar file
        tar_file_name = f"{folder_name}.tar"
        # Full path of .tar folder
        tar_folder_path = os.path.join(tar_path, tar_file_name)
        with tarfile.open(tar_folder_path, "w") as tar:
            tar.add(resume_folder_path, arcname="resume")
        return os.path.relpath(tar_folder_path)
    except Exception as e:
        logger.debug(f"An error occurred: {e}")


def generate_pdf_from_latex(save_folder, latex_code, compiler):
    """
    generate pdf file from latex code
    """
    tar_file = generate_tex_and_tar(
        save_folder, latex_code, TEX_FILE_NAME, TAR_FOLDER_NAME
    )
    with open(tar_file, "rb") as tar_file:
        files = {
            "file": (os.path.basename(tar_file.name), tar_file, "application/x-tar")
        }
        latex_compiler_response = requests.post(
            url=LaTeX_COMPILER_URL_DATA.format(
                tex_folder_path=f"{TAR_FOLDER_NAME}/{TEX_FILE_NAME}.tex",
                compiler=compiler,
            ),
            files=files,
        )
    return latex_compiler_response


def save_pdf(pdf_path, pdf_file, username):
    """
    Save pdf file in pdf_path
    """
    os.makedirs(pdf_path, exist_ok=True)
    file_name = f"{username}_resume.pdf"
    pdf_file_path = os.path.join(pdf_path, file_name)
    with open(pdf_file_path, "wb") as f:
        f.write(pdf_file)
    logger.debug(f"Generated pdf saved at here: {pdf_file_path}")
    pdf_file_path = os.path.abspath(pdf_file_path)
    return pdf_file_path


class PDFGenerator:
    def __init__(self):
        self.pdf = FPDF(format="A4")
        self.margin = 25  # mm
        self.line_height = 6
        self.paragraph_spacing = 10
        self.font_size = 11

    def preprocess_text(self, text):
        """Clean and prepare text for PDF conversion."""
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Split text into paragraphs based on different patterns
        paragraphs = []
        current_paragraph = []

        lines = text.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()

            # Check if this line is a signature line
            is_signature = (line.endswith(",") and len(line.split()) <= 2) or (
                i == len(lines) - 1
            )

            if not line:  # Empty line indicates paragraph break
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []
            elif is_signature:  # Handle signature lines as separate paragraphs
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []
                paragraphs.append(line)
            else:
                current_paragraph.append(line)

        # Add the last paragraph if it exists
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))

        # Clean up each paragraph
        paragraphs = [re.sub(r"\s+", " ", p).strip() for p in paragraphs if p.strip()]

        return paragraphs

    def get_effective_page_width(self):
        """Calculate the effective page width in points."""
        # Convert margins from mm to points
        margin_points = self.margin * 72 / 25.4
        return self.pdf.w - (2 * margin_points)

    def generate_pdf(self, text, output_path):
        """Generate a PDF file from the input text."""
        # Initialize PDF
        self.pdf.add_page()
        self.pdf.set_margins(self.margin, self.margin, self.margin)
        # Add Unicode font
        self.pdf.add_font("Arial", "", fname="./backend/utils/Arial.ttf", uni=True)
        self.pdf.set_font("Arial", size=self.font_size)
        self.pdf.set_auto_page_break(auto=True, margin=self.margin)

        # Process text into paragraphs
        paragraphs = self.preprocess_text(text)

        # Add paragraphs to PDF
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                # For signature lines, use left alignment
                if (
                    i >= len(paragraphs) - 2
                ):  # Last two paragraphs (typically "Sincerely," and name)
                    self.pdf.multi_cell(
                        w=0,
                        h=self.line_height,
                        txt=paragraph,
                        align="L",
                        new_x=XPos.LMARGIN,
                        new_y=YPos.NEXT,
                    )
                else:
                    # For regular paragraphs, use justified alignment
                    self.pdf.multi_cell(
                        w=0,
                        h=self.line_height,
                        txt=paragraph,
                        align="J",
                        new_x=XPos.LMARGIN,
                        new_y=YPos.NEXT,
                    )

                # Add paragraph spacing except after the last paragraph
                if i < len(paragraphs) - 1:
                    self.pdf.ln(self.paragraph_spacing)

        # Save PDF
        self.pdf.output(output_path)
        return output_path

    def create_pdf_document(self, text, output_folder):
        """Create a PDF document from text input in Streamlit."""
        try:
            os.makedirs(output_folder, exist_ok=True)

            # Generate output path
            output_path = os.path.join(output_folder, "CoverLetter.pdf")

            # Generate PDF
            output_path = self.generate_pdf(text, output_path)

            return output_path

        except Exception as e:
            raise Exception(f"Error generating PDF: {str(e)}")


def save_application_qa(save_folder: str, question: str, answer: str) -> str:
    """
    Saves a single application question and answer to a text file.

    Parameters:
        save_folder (str): The folder to save the file in.
        question (str): The application question.
        answer (str): The answer to the question.

    Returns:
        str: Path to the saved file.
    """
    try:
        # Ensure the folder exists
        os.makedirs(save_folder, exist_ok=True)

        # Create a filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"application_question_{timestamp}.txt"
        filepath = os.path.join(save_folder, filename)

        # Format the content
        content = f"Question:\n{question}\n\n"
        content += f"Answer:\n{answer}\n"

        # Write the content to the file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.debug(f"Application Q&A saved to {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Error saving application Q&A: {str(e)}")
        raise e


async def extract_text_from_pdf(pdf_contents: bytes) -> str:
    """
    Extract text from a PDF file.

    Args:
        pdf_contents (bytes): The binary contents of the PDF file

    Returns:
        str: Extracted text from all pages
    """
    pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_contents))

    # Extract text from all pages
    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()

    return extracted_text
