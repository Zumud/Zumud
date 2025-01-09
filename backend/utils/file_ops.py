import os
import requests
import tarfile
from backend.utils.log import logger
from backend.config.config import APPLICANT_NAME, TEX_FILE_NAME, TAR_FOLDER_NAME
from backend.config.envs import LaTeX_COMPILER_URL_DATA
from fpdf import FPDF
import re
from fpdf.enums import XPos, YPos


def generate_tex_and_tar(time: str, company_name: str, latex_content: str, file_name: str= "resume", folder_name: str="resume"):
    """
    Creates a folder, generates a .tex file inside it, and compresses the folder into a .tar file.

    Parameters:
        file_name (str): The name of the .tex file to create.
        latex_content (str): The LaTeX content to write into the file.
        folder_name (str): The name of the folder to create.
    """
    try:
        # Path of a folder for saving .tex files
        resume_folder_path = f'Application/Resumes/{time}_{company_name}'

        # Path of .tar file
        tar_path = f'Application/Resumes/{time}_{company_name}'

        # Ensure the folder exists
        os.makedirs(resume_folder_path, exist_ok=True)

        # Full path for the .tex file
        tex_file_path = os.path.join(resume_folder_path, file_name)

        # Ensure the file name ends with .tex
        if not tex_file_path.endswith(".tex"):
            tex_file_path += ".tex"

        # Write the LaTeX content into the file
        with open(tex_file_path, "w", encoding="utf-8") as tex_file:
            tex_file.write(latex_content)

        logger.debug(f"File '{tex_file_path}' created successfully.")

        # Compress the folder into a .tar file
        tar_file_name = f"{folder_name}.tar"
        # Full path of .tar folder
        tar_folder_path = os.path.join(tar_path, tar_file_name)
        with tarfile.open(tar_folder_path, "w") as tar:
            tar.add(resume_folder_path, arcname='resume')
        return (os.path.relpath(tar_folder_path))
    except Exception as e:
        logger.debug(f"An error occurred: {e}")

def generate_pdf_from_latex(time, company_name, latex_code, compiler):
    """ 
    generate pdf file from latex code
    """
    tar_file = generate_tex_and_tar(time, company_name, latex_code, TEX_FILE_NAME, TAR_FOLDER_NAME)
    with open(tar_file, 'rb') as tar_file:
        files = {'file':(os.path.basename(tar_file.name), tar_file, "application/x-tar")}
        latex_compiler_response = requests.post(url=LaTeX_COMPILER_URL_DATA.format(tex_folder_path=f"{TAR_FOLDER_NAME}/{TEX_FILE_NAME}.tex", compiler=compiler), files= files)
    return latex_compiler_response

def save_pdf(pdf_path, pdf_file):
    """
    Save pdf file in pdf_path
    """
    os.makedirs(pdf_path,exist_ok=True)
    file_name = f"{APPLICANT_NAME}_cv.pdf"
    pdf_file_path = os.path.join(pdf_path,file_name)
    with open(pdf_file_path,'wb') as f:
        f.write(pdf_file)
    logger.debug(f"Generated pdf saved at here: {pdf_file_path}")
    pdf_file_path = os.path.abspath(pdf_file_path)
    return pdf_file_path


class PDFGenerator:
    def __init__(self):
        self.pdf = FPDF(format='A4')
        self.margin = 25  # mm
        self.line_height = 6
        self.paragraph_spacing = 10
        self.font_size = 11
        
    def preprocess_text(self, text):
        """Clean and prepare text for PDF conversion."""
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Split text into paragraphs based on different patterns
        paragraphs = []
        current_paragraph = []
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check if this line is a signature line
            is_signature = (line.endswith(',') and len(line.split()) <= 2) or (i == len(lines) - 1)
            
            if not line:  # Empty line indicates paragraph break
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
            elif is_signature:  # Handle signature lines as separate paragraphs
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                paragraphs.append(line)
            else:
                current_paragraph.append(line)
        
        # Add the last paragraph if it exists
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        # Clean up each paragraph
        paragraphs = [re.sub(r'\s+', ' ', p).strip() for p in paragraphs if p.strip()]
        
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
        self.pdf.add_font('DejaVu', '', fname='backend/utils/DejaVuSans.ttf', uni=True)
        self.pdf.set_font('DejaVu', size=self.font_size)
        self.pdf.set_auto_page_break(auto=True, margin=self.margin)
        
        # Process text into paragraphs
        paragraphs = self.preprocess_text(text)
        
        # Add paragraphs to PDF
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                # For signature lines, use left alignment
                if i >= len(paragraphs) - 2:  # Last two paragraphs (typically "Sincerely," and name)
                    self.pdf.multi_cell(
                        w=0,
                        h=self.line_height,
                        txt=paragraph,
                        align='L',
                        new_x=XPos.LMARGIN,
                        new_y=YPos.NEXT
                    )
                else:
                    # For regular paragraphs, use justified alignment
                    self.pdf.multi_cell(
                        w=0,
                        h=self.line_height,
                        txt=paragraph,
                        align='J',
                        new_x=XPos.LMARGIN,
                        new_y=YPos.NEXT
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

