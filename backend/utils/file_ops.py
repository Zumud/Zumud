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

# (connect, read) seconds. Without a read timeout, a template that sends TeX into an
# infinite loop pins a uvicorn worker forever, and production runs only two of them.
LATEX_COMPILE_TIMEOUT = (5, 60)

# How much of the compiler log to surface; the full log runs to hundreds of lines.
LATEX_ERROR_EXCERPT = 2000

# latexrun prefixes every log with its own Python SyntaxWarnings, so the head of the
# log says nothing about the document. These pick out the lines that do.
LATEX_ERROR_LINE = re.compile(r"^.*?:(?:\d+:)? *error: ", re.MULTILINE)


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
    Writes the .tex file and packs it into the .tar the compiler expects.

    Parameters:
        file_name (str): The name of the .tex file to create.
        latex_content (str): The LaTeX content to write into the file.
        folder_name (str): The name of the folder inside the archive.
    """
    os.makedirs(save_folder, exist_ok=True)

    tex_file_path = os.path.join(save_folder, file_name)
    if not tex_file_path.endswith(".tex"):
        tex_file_path += ".tex"

    # Strip ASCII control chars (keep \t \n \r) — pdflatex chokes on them and
    # LLMs occasionally emit stray ones (e.g. U+0016) when transcribing RTL text.
    latex_content = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", latex_content)

    with open(tex_file_path, "w", encoding="utf-8") as tex_file:
        tex_file.write(latex_content)

    # Only the .tex goes in. Archiving the whole folder swept up whatever the
    # previous generation left behind — an earlier resume.tar, resume.json and
    # the PDF — and handed it all to the compiler.
    tar_folder_path = os.path.join(save_folder, f"{folder_name}.tar")
    with tarfile.open(tar_folder_path, "w") as tar:
        tar.add(
            tex_file_path, arcname=f"{folder_name}/{os.path.basename(tex_file_path)}"
        )

    return os.path.relpath(tar_folder_path)


def summarise_latex_errors(log: str) -> str:
    """Pull the document's own errors out of a compiler log.

    The log opens with latexrun's Python SyntaxWarnings and the pdflatex command
    line, so quoting the first N characters reports a problem in the compiler's
    source rather than in the user's document — useless to whoever has to fix it,
    and worse than useless as feedback to a model rewriting the template.
    """
    lines = log.splitlines()
    kept = []
    for index, line in enumerate(lines):
        if LATEX_ERROR_LINE.match(line):
            # The two lines after an error quote the offending source and point at
            # the column, which is the part that identifies what to change.
            kept.extend(lines[index : index + 3])

    excerpt = "\n".join(kept) if kept else "\n".join(lines[-20:])
    return excerpt[:LATEX_ERROR_EXCERPT].strip()


def generate_pdf_from_latex(save_folder, latex_code, compiler):
    """
    Compile LaTeX into a PDF, raising ValueError if the compiler did not produce one.
    """
    tar_file = generate_tex_and_tar(
        save_folder, latex_code, TEX_FILE_NAME, TAR_FOLDER_NAME
    )
    with open(tar_file, "rb") as tar_file:
        files = {
            "file": (os.path.basename(tar_file.name), tar_file, "application/x-tar")
        }
        try:
            latex_compiler_response = requests.post(
                url=LaTeX_COMPILER_URL_DATA.format(
                    tex_folder_path=f"{TAR_FOLDER_NAME}/{TEX_FILE_NAME}.tex",
                    compiler=compiler,
                ),
                files=files,
                timeout=LATEX_COMPILE_TIMEOUT,
            )
        except requests.Timeout:
            raise ValueError(
                f"LaTeX compilation timed out after {LATEX_COMPILE_TIMEOUT[1]}s"
            )

    # A PDF starts with %PDF; anything else is the compiler log. The previous
    # check searched the whole body for b"error: ", which a valid PDF's binary
    # streams could match by chance.
    if latex_compiler_response.status_code != 200 or not (
        latex_compiler_response.content.startswith(b"%PDF")
    ):
        log = latex_compiler_response.content.decode("utf-8", errors="replace")
        detail = summarise_latex_errors(log)
        logger.error(f"LaTeX compilation error: {detail}")
        raise ValueError(f"Failed to compile LaTeX document: {detail}")

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
