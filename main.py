import os

from fastapi import FastAPI
import openai_wrapper
from models.templates import john_doe_resume, john_doe_legal_authorization, john_doe_preferences
from models.tailoring_options import TailoringOptions
from models.job import Job
from models.profile import Profile, Resume

from log import logger
from config import APPLICANT_NAME

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/determine_eligibility")
def determine_eligibility(job: Job, profile: Profile = Profile(resume=Resume(john_doe_resume),legal_authorization=john_doe_legal_authorization), tailoring_options: TailoringOptions = TailoringOptions()):
    """
    Gets profile and job description and determines eligibility for applying to the job
    """
    eligibility, reason = openai_wrapper.consider_eligibility(job.description, profile.legal_authorization, tailoring_options.ai_model)
    return {
        "eligibility": eligibility,
        "reason": reason
    }
@app.post("/determine_suitability")
def determine_suitability(job: Job, profile: Profile = Profile(resume=Resume(john_doe_resume), preferences=john_doe_preferences), tailoring_options: TailoringOptions = TailoringOptions()):
    """
    Gets profile and job description and determines suitability for applying to the job 
    """
    suitability, reason = openai_wrapper.consider_suitability(job.description, profile.preferences, tailoring_options.ai_model)
    return {
        "suitability": suitability,
        "reason": reason
    }

@app.post("/generate-tailored-plain-resume")
def generate_tailored_plain_resume(job: Job, profile: Profile = Profile(resume=Resume(john_doe_resume)), tailoring_options: TailoringOptions = TailoringOptions()) -> str:
    """
    Gets resume and job description in plain text and returns tailored resume as a string
    """
    return openai_wrapper.create_tailored_plain_resume(profile.resume.text, job.description, tailoring_options.ai_model, tailoring_options.resume_template)

@app.post("/generate-tailored-plain-coverletter")
def generate_tailored_plain_coverletter(job: Job, profile: Profile = Profile(Resume(john_doe_resume)), tailoring_options: TailoringOptions = TailoringOptions()) -> str:  # We should not pass tailoring options everytime, should be a config for each user. It could be kept with a session for example.
    """
    Gets resume and job description in plain text and returns customized cover letter as a string
    """
    return openai_wrapper.create_tailored_plain_coverletter(profile.resume.text, job.description, tailoring_options.ai_model)

@app.post("/generate-tailored-latex-resume")
def generate_tailored_latex_resume(job: Job, profile: Profile = Profile(Resume(john_doe_resume)), tailoring_options: TailoringOptions = TailoringOptions()) -> str:
    """
    Gets resume and job description in plain text and returns tailored resume as a latex
    """
    tailored_plain_resume = generate_tailored_plain_resume(job, profile, tailoring_options)
    _, trimed_tailored_resume = openai_wrapper.covert_plain_resume_to_latex(tailored_plain_resume, tailoring_options.ai_model, tailoring_options.resume_template)
    return trimed_tailored_resume

@app.post("/generate-latex-resume-save")
def generate_tailored_latex_resume_save(job: Job, profile: Profile = Profile(Resume(john_doe_resume)), tailoring_options: TailoringOptions = TailoringOptions()):
    """
    Gets resume and job description in plain text and saves tailored resume
    """
    tailored_plain_resume = generate_tailored_plain_resume(job, profile, tailoring_options)
    company_name = openai_wrapper.ai_prompt(
        f"Give the name of the company that this job description is for. As the output just give the name, nothing else. Job description: {job.description}"
    )  # Since this is a simple task we use the cheapest ai
    # Make a folder for each job description to save PDF, .tex, and .tar files of tailored resume.
    os.makedirs(f'./CVs/{company_name}', exist_ok=True)
    latex_compiler_response, _ = openai_wrapper.covert_plain_resume_to_latex(
        tailored_plain_resume, tailoring_options.ai_model, tailoring_options.resume_template
    )
    # Path to save pdf file of tailored resume
    pdf_path = f'./CVs/{company_name}/{APPLICANT_NAME}_cv.pdf'
    with open(pdf_path, 'wb') as f:
        f.write(latex_compiler_response.content)
    logger.debug(f"Generated resume saved at here: {pdf_path}")
    return {
        "success": f"Generated resume saved at here: {pdf_path}",
        "path": os.path.abspath(pdf_path)
    }
