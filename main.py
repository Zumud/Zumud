import requests
import prompts
from loguru import logger
from os import remove
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from urllib import parse

from envs import ADD_GDRIVE_ZAP_URL, LaTeX_COMPILER_URL
from openai_wrapper import create_customized_cv, create_customized_cl, ai_prompt, ai_messages, create_tailored_plain_resume, create_tailored_plain_coverletter, covert_plain_resume_to_latex
from mail import send_mail
from models import AIModel
from cover_letter import save_string_to_pdf

folder_num = 71  # maybe better to save it in a DB, so can keep it value when we restart the server
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/generate-tailored-plain-resume")
async def generate_tailored_plain_resume(resume: str, job_description: str, model: AIModel = AIModel.gpt_4o_mini) -> str:
    """
    Gets resume and job description in plain text and returns tailored resume as a string
    """
    return create_tailored_plain_resume(resume, job_description, model)

@app.get("/generate-tailored-plain-coverletter")
async def generate_tailored_plain_coverletter(resume: str, job_description: str, model: AIModel = AIModel.gpt_4o_mini) -> str:
    """
    Gets resume and job description in plain text and returns customized cover letter as a string
    """
    return create_tailored_plain_coverletter(resume, job_description, model)

@app.get("/generate-tailored-latex-resume")
async def generate_tailored_latex_resume(resume: str, job_description: str, model: AIModel = AIModel.gpt_4o_mini) -> str:
    """
    Gets resume and job description in plain text and returns tailored resume as a latex
    """
    tailored_plain_resume = create_tailored_plain_resume(resume, job_description, model)
    latex_compiler_reponse, tailored_latex_resume = covert_plain_resume_to_latex(tailored_plain_resume, model)
    company_name = ai_prompt(f"Give the name of the company that this job description is for. As the output just give the name, nothing else. Job description: {job_description}")  # Since this is a simple task we use the cheapest ai
    with open(f'./CVs/{company_name}_cv.pdf', 'wb') as f:
        f.write(latex_compiler_reponse.content)
    return tailored_latex_resume


@app.post("/generator")
async def generator(resume_text: str, job_description_text: str, email_address: str | None = None, cover_letter: bool = False, model: AIModel = AIModel.gpt_4o_mini):
    global folder_num
    ai_tailored_cv_response = create_customized_cv(resume_text, job_description_text, model)
    ai_tailored_cl_response = create_customized_cl(resume_text, job_description_text, model)
    company_name = ai_prompt(f"Give the name of the company that this job description is for. As the output just give the name, nothing else. Job description: {job_description_text}")  # Since this is a simple task we use the cheapest ai    
    
    print(f"The ai_tailored_cv_response is: {ai_tailored_cv_response}\nThe ai_tailored_cl_response is: {ai_tailored_cl_response}\nthe company_name is: {company_name}")
    tailored_cv_latex = ai_tailored_cv_response[ai_tailored_cv_response.find(r"\documentclass"):ai_tailored_cv_response.rfind(r"\end{document}")+len(r"\end{document}")]  # striming to the part we want
    print(f"Tailored CV latex code is:\n{tailored_cv_latex}")  # make these prints as logs
    latex_compiler_reponse = requests.get(url=LaTeX_COMPILER_URL+parse.quote(tailored_cv_latex))
    print(f"URL is: {latex_compiler_reponse.url}")
    print(f"CV pdf text is: {latex_compiler_reponse.content}")
    i = 1
    while b"error: " in latex_compiler_reponse.content and i < 5:  # if there is an error, provide whole previous response not the truncated
        ai_tailored_cv_response = ai_prompt(f"""You've generated the given LaTeX code, but it faces compilation error.
                                            Fix the code based on the error.
                                            LaTeX:\n{ai_tailored_cv_response}.\n\nError:\n{latex_compiler_reponse.content}.""", AIModel.gpt_4o_mini)  # since this is a simple request, we use gpt4o mini for it
        tailored_cv_latex = ai_tailored_cv_response[ai_tailored_cv_response.find(r"\documentclass"):ai_tailored_cv_response.find(r"\end{document}")+len(r"\end{document}")]
        print(f"{i} Corrected Tailored CV latex code is:\n{tailored_cv_latex}")
        latex_compiler_reponse = requests.get(url=LaTeX_COMPILER_URL+parse.quote(tailored_cv_latex))
        print(f"{i} Corrected URL is: {latex_compiler_reponse.url}")
        print(f"{i} Corrected CV pdf text is: {latex_compiler_reponse.content}")
        i += 1

    
    tailored_cl_path = './tailored_cl.pdf'
    save_string_to_pdf(filename=tailored_cl_path, text=ai_tailored_cl_response)

    with open('./tailored_cv.pdf', 'wb') as f:
        f.write(latex_compiler_reponse.content)
    
    # add the file to the GDRIVE
    tailored_cv_path = "./tailored_cv.pdf"

    with open(tailored_cv_path, 'rb') as tailored_cv, open(tailored_cl_path, 'rb') as tailored_cl:
        files = {'tailored_cv': tailored_cv, 'tailored_cl': tailored_cl}
        requests.post(url=ADD_GDRIVE_ZAP_URL, data={'name': f"{folder_num:04}_"+company_name}, files=files)
        folder_num += 1
    
    # we can use this line to send the cv to the email
    if email_address is not None:
        send_mail(send_to=[email_address], subject="Tailored CV", text="Hi there!\n\nPlease find your tailored CV attached to this email.\n\nWishing you all the best in your job search :)" ,files=["./tailored_cv.pdf"])

    remove(tailored_cv_path)
    remove(tailored_cl_path)

    return "sucess"