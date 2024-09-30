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


