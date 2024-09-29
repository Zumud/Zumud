import requests
from os import remove
from fastapi import FastAPI
from urllib import parse
from envs import OPEN_AI_KEY, ADD_GDRIVE_ZAP_URL
# from templates import latex_template
from mail import send_mail

folder_num = 0

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
async def generator(resume_text: str, job_description_text: str, email_address: str = None):
    global folder_num
    # Combine the two given URLs
    data = {
      "model": "gpt-3.5-turbo-0125", #gpt-4o-mini, gpt-3.5-turbo-0125, gpt-4o
      #in the LaTeX template I give you. Latex template: {latex_template}.
      "messages": [{"role": "user", "content": f"""Generate a tailored resume using for the given job description.
                    Resume: {resume_text}.
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
        if i > 4:
            break
        i = i+1
            

    with open('./tailored_cv.pdf', 'wb') as f:
        f.write(latex_compiler_reponse.content)
    
    # add the file to the GDRIVE
    file_path = "./tailored_cv.pdf"

    with open(file_path, 'rb') as file:
        files = {'file': file}
    # response = requests.post(url, )
        requests.post(url=ADD_GDRIVE_ZAP_URL, data={'name': folder_num},  #, 'latex_compiler_url': latex_compiler_url[:-6], 'tailored_cv_latex': parse.quote(tailored_cv_latex)},
                       files=files)
        folder_num += 1
    

    
    
    # we can use this line to send the cv to the email
    if email_address is not None:
        send_mail(send_to=[email_address], subject="Tailored CV", text="Hi there!\n\nPlease find your tailored CV attached to this email.\n\nWishing you all the best in your job search :)" ,files=["./tailored_cv.pdf"])

    remove("./tailored_cv.pdf")

    return "sucess"