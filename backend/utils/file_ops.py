import os
import requests
import tarfile
from .log import logger
from config.config import APPLICANT_NAME, TEX_FILE_NAME, TAR_FOLDER_NAME
from config.envs import LaTeX_COMPILER_URL_DATA

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
        resume_folder_path = f'./Resumes/{time}_{company_name}'

        # Path of .tar file
        tar_path = f'./Resumes/{time}_{company_name}'

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
    return pdf_file_path
