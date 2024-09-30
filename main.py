import requests
from os import remove
from fastapi import FastAPI
from urllib import parse

from envs import ADD_GDRIVE_ZAP_URL, LaTeX_COMPILER_URL
from openai_wrapper import ai_prompt
from mail import send_mail
from models import AIModel

folder_num = 0  # maybe better to save it in a DB, so can keep it value when we restart the server
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/generator")
async def generator(resume_text: str, job_description_text: str, email_address: str | None = None, cover_letter: bool = False, model: AIModel | None = AIModel.gpt_3_5_turbo_cheap):
    global folder_num
    ai_tailored_cv_response = ai_prompt(f"""Generate a tailored resume using for the given job description. Resume: {resume_text}. Job Description text: {job_description_text}""", model)
    job_name = ai_prompt(f"Give the name of the company that this job post is for. As the output hust give the name, nothing else. Job post: {job_description_text}")
    tailored_cv_latex = ai_tailored_cv_response[ai_tailored_cv_response.find(r"\documentclass"):ai_tailored_cv_response.find(r"\end{document}")+len(r"\end{document}")]

    print(f"Tailored CV latex code is:\n{tailored_cv_latex}")  # make these prints as logs

    latex_compiler_reponse = requests.get(url=LaTeX_COMPILER_URL+parse.quote(tailored_cv_latex))
    print(f"URL is: {latex_compiler_reponse.url}")
    print(f"CV pdf text is: {latex_compiler_reponse.content}")

    i = 1
    while b"error: " in latex_compiler_reponse.content and i < 5:
        ai_tailored_cv_response = ai_prompt(f"""Fix the latex code given with it's error. LaTeX: {tailored_cv_latex}. error: {latex_compiler_reponse.content}.""", model)
        tailored_cv_latex = ai_tailored_cv_response[ai_tailored_cv_response.find(r"\documentclass"):ai_tailored_cv_response.find(r"\end{document}")+len(r"\end{document}")]
        print(f"{i} Corrected Tailored CV latex code is:\n{tailored_cv_latex}")
        latex_compiler_reponse = requests.get(url=LaTeX_COMPILER_URL+parse.quote(tailored_cv_latex))
        print(f"{i} Corrected URL is: {latex_compiler_reponse.url}")
        print(f"{i} Corrected CV pdf text is: {latex_compiler_reponse.content}")
        i = i+1


    with open('./tailored_cv.pdf', 'wb') as f:
        f.write(latex_compiler_reponse.content)
    
    # add the file to the GDRIVE
    file_path = "./tailored_cv.pdf"

    with open(file_path, 'rb') as file:
        files = {'file': file}
        requests.post(url=ADD_GDRIVE_ZAP_URL, data={'name': f"{folder_num:04}_"+job_name}, files=files)
        folder_num += 1
    
    # we can use this line to send the cv to the email
    if email_address is not None:
        send_mail(send_to=[email_address], subject="Tailored CV", text="Hi there!\n\nPlease find your tailored CV attached to this email.\n\nWishing you all the best in your job search :)" ,files=["./tailored_cv.pdf"])

    remove("./tailored_cv.pdf")

    return "sucess"