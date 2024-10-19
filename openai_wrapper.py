import json
from pydantic import BaseModel
from openai import OpenAI
from envs import OPEN_AI_KEY
from models import AIModel

client = OpenAI(api_key=OPEN_AI_KEY)  # we recommend using python-dotenv to add OPENAI_API_KEY="My API Key" to your .env file so that your API Key is not stored in source control.

class TailoredCV(BaseModel):
    customized_resume: str

class TailoredCL(BaseModel):
    customized_cover_letter: str

class CompanyName(BaseModel):
    company_name: str

def create_customized_cv(resume_text: str, job_description_text: str, model=AIModel.gpt_4o_mini):
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
        response_format=TailoredCV  # ensures the out put is a json with the given format. For unsupported models, we can use JSON mode. read here: https://platform.openai.com/docs/guides/structured-outputs/json-mode
    )

    ai_tailored_cv_response, = json.loads(completion.choices[0].message.content).values()  # create the json object and unpack
    return ai_tailored_cv_response


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
        ]
    )
    return completion.choices[0].message.content

def ai_messages(messages: list[tuple[str, str]], model=AIModel.gpt_4o_mini) -> str:
    completion = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return completion.choices[0].message.content