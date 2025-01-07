import json
import utils.prompts as prompts
from loguru import logger
from pydantic import BaseModel, Field
from openai import OpenAI
from config.envs import OPEN_AI_KEY
from models.ai_models import AIModel
from models.templates import ResumeTemplate, Template_Details
from .utils import generate_pdf_from_latex

client = OpenAI(api_key=OPEN_AI_KEY)  # we recommend using python-dotenv to add OPENAI_API_KEY="My API Key" to your .env file so that your API Key is not stored in source control.

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

def create_customized_resume(resume_text: str, job_description_text: str, model=AIModel.gpt_4o_mini):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": """You will be given a job description. Create a customized resume in LaTeX.
             Follow these instructions:
             - change the title in a way that matches the job title
             - Just focus on the contents. Do not change any settings, such as paper size, style, packages, and so on.
             - For each past job in the experience section do not change the company name. Keep a 1-2 sentence about that company description. This should be concise but specific enough to give a good understanding of the past company.
             - Make sure the skills in the job description are included in the resume.
             - For items (bullet points) of each job rephrase them in a way that matches the language of the job description.
             - Make technologies keywords bold. Bold syntax is \\textbf{text}.
             - Run through all LaTeX after creation and make sure you're following LaTeX syntax.
             - Make sure that each LaTeX instruction is in a single line. Don't put all the code in one line.
             Resume LaTeX:""" + resume_text},
            {"role": "user", "content": "Job description: "+job_description_text}
        ],
        response_format=CustomizedResume  # ensures the out put is a json with the given format. For unsupported models, we can use JSON mode. read here: https://platform.openai.com/docs/guides/structured-outputs/json-mode
    )

    ai_tailored_resume_response, = json.loads(completion.choices[0].message.content).values()  # create the json object and unpack
    return ai_tailored_resume_response


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

def consider_eligibility(job_description: str, legal_authorization: str, model: AIModel = AIModel.gpt_4o_mini):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompts.consider_eligibility.format(legal_authorization=legal_authorization, job_description=job_description)}
        ],
        response_format=Eligibility
    )
    eligibility = json.loads(completion.choices[0].message.content)["eligibility"]
    logger.debug(f"Is user eligible for this job: {eligibility}")
    reason = json.loads(completion.choices[0].message.content)["reason"]
    logger.debug(f"Reason of eligibility desicion: {reason}")
    return eligibility, reason

def consider_suitability(job_description: str, preferences: str, model: AIModel = AIModel.gpt_4o_mini):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompts.consider_suitability.format(preferences=preferences, job_description=job_description)}
        ],
        response_format=Suitability
    )
    suitability = json.loads(completion.choices[0].message.content)["suitability"]
    logger.debug(f"Is user eligible for this job: {suitability}")
    reason = json.loads(completion.choices[0].message.content)["reason"]
    logger.debug(f"Reason of eligibility desicion: {reason}")
    return suitability, reason

def create_tailored_plain_resume(resume: str, job_description: str, model=AIModel.gpt_4o_mini, template=ResumeTemplate.Blue_Modern_Resume) -> str:
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompts.create_tailored_resume.format(resume=resume, job_description=job_description, num_pages=Template_Details[template]['num_pages'])}
        ],
        response_format=TailoredResume
    )
    tailored_resume = json.loads(completion.choices[0].message.content)["tailored_resume"]
    logger.debug(f"The tailored resume plain text is: {tailored_resume}")
    return tailored_resume

def covert_plain_resume_to_latex(time: str, company_name: str, plain_resume: str, model=AIModel.gpt_4o_mini, template=ResumeTemplate.Blue_Modern_Resume):

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompts.convert_plain_resume_to_latex.format(num_pages=Template_Details[template]['num_pages'], resume=plain_resume, latex_template=Template_Details[template]['structure'])}
    ]
    i = 1
    while i < 5: # and error in the code 
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=TailoredResume
        )
        tailored_resume = json.loads(completion.choices[0].message.content)["tailored_resume"]
        logger.debug(f"The tailored resume Latex code in iteration {i} is: {tailored_resume}")
        trimed_tailored_resume = tailored_resume[tailored_resume.find(r"\documentclass"):tailored_resume.rfind(r"\end{document}")+len(r"\end{document}")]  # removes possible extra things that AI adds
        compiler = Template_Details[template]['compiler']
        latex_compiler_response = generate_pdf_from_latex(time, company_name, trimed_tailored_resume, compiler)
        logger.debug(f"Request url to the LaTeX compiler is: {latex_compiler_response.url}")
        if not b"error: " in latex_compiler_response.content:  # there is no error in the compiled code
            return latex_compiler_response, trimed_tailored_resume
        logger.debug(f"There is an error in the latex code: {latex_compiler_response.content}")
        messages.extend([{"role": "assistant", "content": tailored_resume},
                         {"role": "user", "content": prompts.fix_latex_error.format(error=latex_compiler_response.content)}])
        i += 1
    return latex_compiler_response, trimed_tailored_resume

def create_tailored_plain_coverletter(resume: str, job_description: str, model=AIModel.gpt_4o_mini) -> str:
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
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

def generate_answer_questions(resume: str, job_description: str, question: str, model=AIModel.gpt_4o_mini):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assisstant."},
            {"role": "user", "content": prompts.answer_application_question.format(resume=resume, job_description=job_description, question=question)}
        ],
        response_format=TailoredAnswer
    )
    return json.loads(completion.choices[0].message.content)["tailored_answer"]
