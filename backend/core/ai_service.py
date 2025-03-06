import json

from loguru import logger
from openai import OpenAI
from pydantic import BaseModel, Field

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

def covert_plain_resume_to_latex(save_folder: str, plain_resume: str, model=AIModel.gpt_4o_mini, template=ResumeTemplate.MTeck_resume):
    # Store the original content sections
    original_sections = {}
    current_section = None
    section_content = []
    
    for line in plain_resume.split('\n'):
        if line.strip().startswith('\\section{') or line.strip().startswith('\\subsection{'):
            if current_section:
                original_sections[current_section] = '\n'.join(section_content)
            current_section = line.strip()
            section_content = []
        elif current_section:
            section_content.append(line)
    
    if current_section:
        original_sections[current_section] = '\n'.join(section_content)

    messages = [
        {"role": "system", "content": """You are an expert in LaTeX document processing and resume formatting.
        Your task is to format the resume content while:
        1. Preserving ALL content from the original resume
        2. Only fixing LaTeX syntax issues
        3. Maintaining the document structure
        4. Not removing or modifying any sections
        5. If you encounter LaTeX errors, fix the syntax while keeping the content intact"""},
        {"role": "user", "content": prompts.convert_plain_resume_to_latex.format(
            num_pages=Template_Details[template]['num_pages'],
            resume=plain_resume,
            latex_template=Template_Details[template]['structure']
        )}
    ]

    max_attempts = 5
    attempt = 1
    last_error = None
    
    while attempt <= max_attempts:
        try:
            completion = client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=TailoredResume
            )
            
            tailored_resume = json.loads(completion.choices[0].message.content)["tailored_resume"]
            logger.debug(f"Attempt {attempt}: Generated LaTeX code")
            
            # Extract the document content between \begin{document} and \end{document}
            doc_start = tailored_resume.find(r"\begin{document}")
            doc_end = tailored_resume.rfind(r"\end{document}")
            if doc_start == -1 or doc_end == -1:
                raise ValueError("Missing document environment markers")
                
            document_content = tailored_resume[doc_start:doc_end + len(r"\end{document}")]
            
            # Verify all original sections are present
            for section in original_sections:
                if section not in document_content:
                    raise ValueError(f"Missing section: {section}")
            
            # Try to compile
            compiler = Template_Details[template]['compiler']
            latex_compiler_response = generate_pdf_from_latex(save_folder, tailored_resume, compiler)
            
            if not b"error: " in latex_compiler_response.content:
                logger.debug("Successfully compiled LaTeX document")
                return latex_compiler_response, tailored_resume
                
            error_msg = latex_compiler_response.content.decode('utf-8')
            logger.debug(f"LaTeX compilation error: {error_msg}")
            
            # Add error context to messages
            messages.extend([
                {"role": "assistant", "content": tailored_resume},
                {"role": "user", "content": f"""Fix the following LaTeX error while preserving ALL content:
                Error: {error_msg}
                
                Important:
                1. Do not remove or modify any sections
                2. Only fix the LaTeX syntax issues
                3. Keep all content intact
                4. If the error is about missing packages, add them to the preamble
                5. If the error is about syntax, fix only the problematic part
                
                Current document structure:
                {list(original_sections.keys())}"""}
            ])
            
            last_error = error_msg
            attempt += 1
            
        except Exception as e:
            logger.error(f"Error in attempt {attempt}: {str(e)}")
            attempt += 1
    
    # If we get here, we failed to generate a valid document
    error_summary = f"Failed to generate valid LaTeX after {max_attempts} attempts. Last error: {last_error}"
    logger.error(error_summary)
    raise ValueError(error_summary)

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
