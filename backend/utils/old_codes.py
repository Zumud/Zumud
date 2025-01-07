## Set your OpenAI API key globally, which is not advised
# openai.api_key = OPEN_AI_KEY


## How to call openai rest api
# url = "https://api.openai.com/v1/chat/completions"
# headers = {
#     "Content-Type": "application/json",
#     "Authorization": f"Bearer {OPEN_AI_KEY}"
# }
# Combine the two given URLs
    # data = {
    #   "model": model, #gpt-4o-mini, gpt-3.5-turbo-0125, gpt-4o
    #   #in the LaTeX template I give you. Latex template: {latex_template}.
    #   "messages": [{"role": "user", "content": f"""Generate a tailored resume using for the given job description.
    #                 Resume: {resume_text}.
    #                 Job Description text: {job_description_text}"""}],
    #   "temperature": 0.7ß
    # }
    # ai_tailored_cv_response = requests.post(url, json=data, headers=headers).json()["choices"][0]["message"]["content"]


## git command example: https://texlive2020.latexonline.cc/compile?command=xelatex&git=https://github.com/mohammadi-com/resume&target=MohammadMohammadi2/MohammadMohammadi.tex
## git command example: https://latexonline.cc/compile?git=https://github.com/mohammadi-com/resume&target=MohammadMohammadi2/MohammadMohammadi.tex&force=true
## .tar command example: https://latexonline.cc/data?target=resume/MohammadMohammadi2/MohammadMohammadi.tex&force=true&command=xelatex

    # tailored_cl_path = './tailored_cl.pdf'
    # save_string_to_pdf(filename=tailored_cl_path, text=ai_tailored_cl_response)

    # with open('./tailored_cv.pdf', 'wb') as f:
    #     f.write(latex_compiler_reponse.content)
    
    # # add the file to the GDRIVE
    # tailored_cv_path = "./tailored_cv.pdf"

    # with open(tailored_cv_path, 'rb') as tailored_cv, open(tailored_cl_path, 'rb') as tailored_cl:
    #     files = {'tailored_cv': tailored_cv, 'tailored_cl': tailored_cl}
    #     requests.post(url=ADD_GDRIVE_ZAP_URL, data={'name': f"{folder_num:04}_"+company_name}, files= )
    #     folder_num += 1
    
    # # we can use this line to send the cv to the email
    # if email_address is not None:
    #     send_mail(send_to=[email_address], subject="Tailored CV", text="Hi there!\n\nPlease find your tailored CV attached to this email.\n\nWishing you all the best in your job search :)" ,files=["./tailored_cv.pdf"])
