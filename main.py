import os

from loguru import logger
from fastapi import FastAPI

import openai_wrapper
from models import AIModel
from templates import john_doe_resume

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/generate-tailored-plain-resume")
def generate_tailored_plain_resume(resume: str, job_description: str, model: AIModel = AIModel.gpt_4o_mini) -> str:
    """
    Gets resume and job description in plain text and returns tailored resume as a string
    """
    return openai_wrapper.create_tailored_plain_resume(resume, job_description, model)

@app.get("/generate-tailored-plain-coverletter")
def generate_tailored_plain_coverletter(resume: str, job_description: str, model: AIModel = AIModel.gpt_4o_mini) -> str:
    """
    Gets resume and job description in plain text and returns customized cover letter as a string
    """
    return openai_wrapper.create_tailored_plain_coverletter(resume, job_description, model)

@app.get("/generate-tailored-latex-resume")
def generate_tailored_latex_resume(resume: str, job_description: str, model: AIModel = AIModel.gpt_4o_mini) -> str:
    """
    Gets resume and job description in plain text and returns tailored resume as a latex
    """
    tailored_plain_resume = generate_tailored_plain_resume(resume, job_description, model)
    _, trimed_tailored_resume = openai_wrapper.covert_plain_resume_to_latex(tailored_plain_resume, model)
    return trimed_tailored_resume

@app.get("/generate-latex-resume-save")
def generate_tailored_latex_resume_save(job_description: str, resume: str = john_doe_resume, model: AIModel = AIModel.gpt_4o_mini):
    """
    Gets resume and job description in plain text and saves tailored resume
    """
    tailored_plain_resume = generate_tailored_plain_resume(resume, job_description, model)
    latex_compiler_reponse, _ = openai_wrapper.covert_plain_resume_to_latex(tailored_plain_resume, model)
    company_name = openai_wrapper.ai_prompt(f"Give the name of the company that this job description is for. As the output just give the name, nothing else. Job description: {job_description}")  # Since this is a simple task we use the cheapest ai
    with open(f'./CVs/{company_name}_cv.pdf', 'wb') as f:
        f.write(latex_compiler_reponse.content)
    logger.debug(f"Generated resume saved at here: ./CVs/{company_name}_cv.pdf")
    return {"success": f"Generated resume saved at here: ./CVs/{company_name}_cv.pdf",
    "path": os.path.abspath(f"./CVs/{company_name}_cv.pdf")
    }
