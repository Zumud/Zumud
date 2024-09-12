import requests
from os import remove
from fastapi import FastAPI
from urllib import parse
from envs import OPEN_AI_KEY
from templates import latex_template
from mail import send_mail

app = FastAPI()

url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPEN_AI_KEY}"
}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/generator")
async def generator(resume_text: str, job_description_text: str, email_address: str):
    # Combine the two given URLs
    data = {
      "model": "gpt-4o-mini", #gpt-4o-mini, gpt-3.5-turbo-0125
      "messages": [{"role": "user", "content": f"""Generate a tailored resume using for the given job description in the LaTeX template I give you. Latex template: {latex_template}.
                    Resume text: {resume_text}.
                    Job Description text: {job_description_text}"""}],
      "temperature": 0.7
    }
    ai_tailored_cv_response = requests.post(url, json=data, headers=headers).json()["choices"][0]["message"]["content"]
    tailored_cv_latex = ai_tailored_cv_response[ai_tailored_cv_response.find(r"\documentclass"):ai_tailored_cv_response.find(r"\end{document}")+len(r"\end{document}")]

    print(f"Tailored CV latex code is:\n{tailored_cv_latex}")

    latex_compiler_url = "https://latexonline.cc/compile?command=xelatex&text="
    # git command example: https://texlive2020.latexonline.cc/compile?command=xelatex&git=https://github.com/mohammadi-com/resume&target=MohammadMohammadi2/MohammadMohammadi.tex

    latex_compiler_reponse = requests.get(url=latex_compiler_url+parse.quote(tailored_cv_latex))
    print(f"URL is: {latex_compiler_reponse.url}")
    print(f"CV pdf text is: {latex_compiler_reponse.content}")

    i = 1
    while b"error: " in latex_compiler_reponse.content:
        data = {
          "model": "gpt-4o-mini", #we can use better ai in here to get better faster reponse, we can use a thread also
          "messages": [{"role": "user", "content": f"""Fix the latex code given with it's error. LaTeX: {tailored_cv_latex}.
                         error: {latex_compiler_reponse.content}."""}],
          "temperature": 0.7
        }
        ai_tailored_cv_response = requests.post(url, json=data, headers=headers).json()["choices"][0]["message"]["content"]
        tailored_cv_latex = ai_tailored_cv_response[ai_tailored_cv_response.find(r"\documentclass"):ai_tailored_cv_response.find(r"\end{document}")+len(r"\end{document}")]
        print(f"{i} Corrected Tailored CV latex code is:\n{tailored_cv_latex}")
        latex_compiler_reponse = requests.get(url=latex_compiler_url+parse.quote(tailored_cv_latex))
        print(f"{i} Corrected URL is: {latex_compiler_reponse.url}")
        print(f"{i} Corrected CV pdf text is: {latex_compiler_reponse.content}")
        if i < 5:
            i = i+1
        else:
            break


    with open('./tailored_cv.pdf', 'wb') as f:
        f.write(latex_compiler_reponse.content)
    
    send_mail(send_to=[email_address], subject="Tailored CV", text="Hi there!\n\nPlease find your tailored CV attached to this email.\n\nWishing you all the best in your job search :)" ,files=["./tailored_cv.pdf"])

    remove("./tailored_cv.pdf")

    return "sucess"