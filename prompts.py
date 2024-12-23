
consider_eligibility = """Please help me to understand am I legally authorized for this job based on my legal authorization info or not.
** My legal authorization:**
{legal_authorization}

** Job description:**
{job_description}

**Instructions:**
- Identify specific legal authorization and work eligibility requirements in the job description.
- Search for specific legal requiremnets for working in the job's location.
- Match the identified legal requirements with the my legal authorization details provided.
- Based on the legal authorization details and the requirements in the job description, assess whether I am legally authorized to work for the company in the specified location.
- Answer with True or False to whether I am legally eligible to work for the company in their location, providing a concise explanation for the determination.
"""

consider_suitability = """Please help me understand if I am suitable for this job based on my preferences for in-person, hybrid, or fully remote work, in relation to the job description.
** My preferences:**
{preferences}

** Job description:**
{job_description}

**Instructions:**
- Identify specific rules and regulations for flexible work in the job description.
- Match the identified flexible work regulations with my preferences provided.
- Based on my preferences and flexible work regulations in the job description, assess whether I am suitable for this job.
- Answer with True or False to whether I am suitable to work for the company, providing a concise explanation for the determination.
"""
create_tailored_resume = """Please help me tailor my resume to match the following job description, emphasizing relevant skills and experiences to maximize my chances of getting an interview.

**My Current Resume:**
{resume}

**Job Description:**
{job_description}

**Instructions:**
- Highlight and expand on experiences that align closely with the job requirements.
- Incorporate keywords and phrases from the job description into my resume.
- Remove or de-emphasize experiences that are not relevant to the job.
- Ensure the resume remains professional and well-organized.
- Keep the final resume within {num_pages} pages.


Thank you!
"""


create_tailored_coverletter_prompt = """You are an expert career coach and professional writer. Using the resume and job description provided below, write a personalized cover letter. The cover letter should:

- Highlight how my skills, experiences, and achievements, and explains why I am an excellent fit for the position.
- Emphasize the most relevant aspects of my resume that match the job description.
- Demonstrate my enthusiasm for the role and the company.
- Be professional, engaging, and tailored to maximize my chances of securing an interview.
- Follow standard cover letter format. Start with "Dear", there is no need for contact details, date, and so on. No place holders.

**Resume:**
{resume}

**Job Description:**
{job_description}
"""


convert_plain_resume_to_latex = """I have a resume in text format and a LaTeX resume template. I need you to help me populate the LaTeX template with the information from my resume. Please parse the resume text, extract all relevant information, and fill in the LaTeX template accordingly. Make sure to:

- Add or remove sections in the LaTeX template based on the content of the resume.
- Populate all fields such as personal information, summary, experience, skills, education, projects, certifications.
- Add necessary bullet points for each part instead of very long sentences.
- Format the bullet points and lists appropriately in LaTeX.
- Escape any LaTeX special characters in the content.
- Ensure the final output is valid LaTeX code ready for compilation.
- Ensure the final output is {num_pages} pages.

Here is my resume text:

{resume}

---

And here is my LaTeX template:

{latex_template}

---

Please provide the complete populated LaTeX code."""


fix_latex_error = """I tried compiling the LaTeX resume code you provided earlier, but I encountered an error during compilation. The error message is:

```
{error}
```

Could you please help me fix the LaTeX code so it compiles successfully? 
Please provide the corrected LaTeX code with the issue resolved."""