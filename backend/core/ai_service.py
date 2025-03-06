import json

from loguru import logger
from openai import OpenAI
from pydantic import BaseModel, Field, HttpUrl
from jinja2 import Template
from typing import List, Optional

import backend.utils.prompts as prompts
from backend.config.envs import OPEN_AI_KEY
from backend.models.ai_models import AIModel
from backend.models.templates import ResumeTemplate, Template_Details
from backend.utils.file_ops import generate_pdf_from_latex, save_application_qa
from backend.utils.log import logger
from backend.models.legal_authorization_models import LegalAuthorization


client = OpenAI(api_key=OPEN_AI_KEY)

class Eligibility(BaseModel):
    eligibility: bool = Field(..., description="Indicates eligibility: 'True' or 'False'.")
    reason: str = Field(..., description="Explanation of eligibility")

class Suitability(BaseModel):
    suitability: bool = Field(..., description="Indicates suitability: 'True' or 'False.")
    reason: str = Field(..., description="Explanation of suitability")
class TailoredResume(BaseModel):
    tailored_resume: str

class TailoredCoverLetter(BaseModel):
    tailored_coverletter: str

class CustomizedResume(BaseModel):
    customized_resume: str

class TailoredCL(BaseModel):
    customized_cover_letter: str

class CompanyName(BaseModel):
    company_name: str

class TailoredAnswer(BaseModel):
    tailored_answer: str

class ResumeSection(BaseModel):
    category: str
    items: List[str]

class Experience(BaseModel):
    company: str
    role: str
    location: str
    date_range: str
    achievements: List[str]

class Education(BaseModel):
    institution: str
    degree: str
    location: str
    date_range: str
    minors: Optional[List[str]] = None

class Certification(BaseModel):
    name: str
    issuer: str

class Project(BaseModel):
    name: str
    date_range: str
    achievements: List[str]

class PersonalInfo(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    linkedin: str
    github: str

class StructuredResume(BaseModel):
    personal_info: PersonalInfo
    summary: str
    skills: List[ResumeSection]
    experience: List[Experience]
    education: List[Education]
    certifications: Optional[List[Certification]] = None
    projects: Optional[List[Project]] = None

def create_customized_cl(resume_text: str, job_description_text: str, model=AIModel.gpt_4o_mini):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": """You will be given a job description. Create a customized cover letter based on the resume is given.
             Follow these instructions:
             - The body of it should be at most two paragraphs.
             - Focus on my experiences and skills that align with the job description.
             - Not overly formal.
             Resume:""" + resume_text},
            {"role": "user", "content": "Job description: "+job_description_text}
        ],
        response_format=TailoredCL
    )

    ai_tailored_cl_response, = json.loads(completion.choices[0].message.content).values()  # create the json object and unpack
    return ai_tailored_cl_response


def ai_prompt(prompt: str, model=AIModel.gpt_4o_mini) -> str:
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
    )
    return completion.choices[0].message.content

def get_company_name(job_description):
    """
    Identifying the name of the company based on the job description
    """
    company_name = ai_prompt(
        f"Give the name of the company that this job description is for. As the output just give the name, nothing else. Job description: {job_description}"
    )  # Since this is a simple task we use the cheapest ai
    return company_name

def consider_eligibility(job_description: str, legal_authorization: LegalAuthorization, model: AIModel = AIModel.gpt_4o_mini):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompts.consider_eligibility.format(legal_authorization=legal_authorization.work_authorization, job_description=job_description)}
        ],
        response_format=Eligibility
    )
    eligibility = json.loads(completion.choices[0].message.content)["eligibility"]
    logger.debug(f"Is user eligible for this job: {eligibility}")
    reason = json.loads(completion.choices[0].message.content)["reason"]
    logger.debug(f"Reason of eligibility decision: {reason}")
    return eligibility, reason

def consider_suitability(job_description: str, model: AIModel = AIModel.gpt_4o_mini):
    messages = [
        {"role": "system", "content": prompts.consider_suitability_system},
        {"role": "user", "content": prompts.consider_suitability.format(job_description=job_description)}
    ]
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=Suitability
    )
    suitability = json.loads(completion.choices[0].message.content)["suitability"]
    logger.debug(f"Is user eligible for this job: {suitability}")
    reason = json.loads(completion.choices[0].message.content)["reason"]
    logger.debug(f"Reason of eligibility desicion: {reason}")
    return suitability, reason

def create_tailored_plain_resume(resume: str, job_description: str, model=AIModel.gpt_4o_mini, template=ResumeTemplate.MTeck_resume) -> str:
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert in resume writing."},
            {"role": "user", "content": prompts.create_tailored_resume.format(resume=resume, job_description=job_description, num_pages=Template_Details[template]['num_pages'])}
        ],
        response_format=TailoredResume
    )
    tailored_resume = json.loads(completion.choices[0].message.content)["tailored_resume"]
    logger.debug(f"The tailored resume plain text is: {tailored_resume}")
    return tailored_resume

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
        text = data.replace('\\', r'\textbackslash{}')
        
        # Then handle other special characters
        text = text.replace('&', r'\&')
        text = text.replace('%', r'\%')
        text = text.replace('$', r'\$')
        text = text.replace('#', r'\#')
        text = text.replace('_', r'\_')
        text = text.replace('{', r'\{')
        text = text.replace('}', r'\}')
        text = text.replace('~', r'\textasciitilde{}')
        text = text.replace('^', r'\textasciicircum{}')
        text = text.replace('<', r'\textless{}')
        text = text.replace('>', r'\textgreater{}')
        
        return text
    elif isinstance(data, list):
        return [escape_latex(item) for item in data]
    elif isinstance(data, dict):
        return {k: escape_latex(v) for k, v in data.items()}
    else:
        return data

def covert_plain_resume_to_latex(save_folder: str, resume: str, job_description: str, model=AIModel.gpt_4o_mini, template=ResumeTemplate.MTeck_resume):
    """
    Convert a plain resume to LaTeX using structured output and Jinja2 templating.
    """
    # First, get structured resume data from GPT
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": """You are an expert resume parser and formatter.
            Your task is to analyze the resume and job description, and output a structured JSON object
            that follows the exact schema provided. The output should be tailored to the job description
            while preserving all relevant information from the resume."""},
            {"role": "user", "content": f"""Resume:
            {resume}
            
            Job Description:
            {job_description}
            
            Please analyze this resume and job description, and output a structured JSON object
            that follows this exact schema:
            {json.dumps(StructuredResume.model_json_schema(), indent=2)}
            
            Important:
            1. Tailor the content to the job description while preserving factual information
            2. Ensure all dates are in a consistent format (e.g., "Jan 2020 -- Present")
            3. Keep achievements concise and impactful
            4. Include only relevant skills and experiences
            5. Format all text properly for LaTeX (escape special characters)"""}
        ],
        response_format=StructuredResume
    )
    
    structured_resume = json.loads(completion.choices[0].message.content)
    
    logger.debug(f"Structured resume: {structured_resume}")
    
    # Escape LaTeX special characters in the resume data
    escaped_resume = escape_latex(structured_resume)
    logger.debug(f"Escaped resume: {escaped_resume}")
    
    # Get the LaTeX template
    latex_template = Template_Details[template]['structure']
    logger.debug(f"LaTeX template: {latex_template}")
    
    # Create Jinja2 template and render
    jinjatex_template = Template(latex_template)
    logger.debug(f"Jinjatex Template: {jinjatex_template}")
    rendered_latex = jinjatex_template.render(escaped_resume)
    logger.debug(f"Rendered LaTeX: {rendered_latex}")
    
    # Try to compile
    compiler = Template_Details[template]['compiler']
    latex_compiler_response = generate_pdf_from_latex(save_folder, rendered_latex, compiler)
    
    if b"error: " in latex_compiler_response.content:
        error_msg = latex_compiler_response.content.decode('utf-8')
        logger.error(f"LaTeX compilation error: {error_msg}")
        raise ValueError(f"Failed to compile LaTeX document: {error_msg}")
    
    logger.debug("Successfully compiled LaTeX document")
    return latex_compiler_response, rendered_latex

def create_tailored_plain_coverletter(resume: str, job_description: str, model=AIModel.gpt_4o_mini) -> str:
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert career coach and professional writer."},
            {"role": "user", "content": prompts.create_tailored_coverletter_prompt.format(resume=resume, job_description=job_description)}
        ],
        response_format=TailoredCoverLetter
    )
    return json.loads(completion.choices[0].message.content)["tailored_coverletter"]

def ai_messages(messages: list[tuple[str, str]], model=AIModel.gpt_4o_mini) -> str:
    completion = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return completion.choices[0].message.content

def generate_answer_questions(resume: str, job_description: str, question: str, save_folder: str = None, model=AIModel.gpt_4o_mini):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assisstant."},
            {"role": "user", "content": prompts.answer_application_question.format(resume=resume, job_description=job_description, question=question)}
        ],
        response_format=TailoredAnswer
    )
    
    answer = json.loads(completion.choices[0].message.content)["tailored_answer"]
    
    # Save the question and answer if save_folder is provided
    if save_folder:
        try:
            file_path = save_application_qa(save_folder, question, answer)
            logger.debug(f"Application Q&A saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving application Q&A: {str(e)}")
    
    return answer
