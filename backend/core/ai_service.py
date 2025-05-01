import json

from loguru import logger
from openai import OpenAI
from jinja2 import Template

import backend.utils.prompts as prompts
from backend.config.envs import OPEN_AI_KEY
from backend.models.ai_models import AIModel
from backend.models.templates import ResumeTemplate, Template_Details
from backend.utils.file_ops import generate_pdf_from_latex, save_application_qa, escape_latex
from backend.utils.log import logger
from backend.models.resume_models import TailoredResume, TailoredCoverLetter, TailoredAnswer, StructuredResume

client = OpenAI(api_key=OPEN_AI_KEY)

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

def generate_tailored_resume_text(resume: str, job_description: str, model=AIModel.gpt_4o_mini, template=ResumeTemplate.MTeck_resume) -> str:
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

def generate_structured_latex_resume(save_folder: str, resume: str, job_description: str, model=AIModel.gpt_4o_mini, template=ResumeTemplate.MTeck_resume):
    """
    Convert a plain resume to LaTeX using structured output and Jinja2 templating.
    """
    # First, get structured resume data from GPT
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": """You are a world-class resume writer, career strategist, and ATS optimization expert. You specialize in transforming general resumes into sharply focused, high-impact documents tailored for specific job applications — increasing interview rates significantly. Your sole goal is to maximize the candidate’s chances of getting an interview by rewriting their resume content to match a specific job description. Your output will be structured as JSON for formatting later, but you should focus purely on crafting the best possible content."""},
            {"role": "user", "content": prompts.structured_resume_prompt.format(
                resume=resume,
                job_description=job_description,
                schema=json.dumps(StructuredResume.model_json_schema(), indent=2)
            )}
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

def generate_tailored_coverletter_text(resume: str, job_description: str, model=AIModel.gpt_4o_mini) -> str:
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
