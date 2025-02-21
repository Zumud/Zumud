
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


create_tailored_coverletter_prompt = """
Generate a concise and impactful cover letter (maximum two paragraphs) tailored specifically for the given job description. Focus on highlighting the most relevant experience and skills from the provided resume.
- Make it direct, engaging, and results-oriented, avoiding generic statements.
- Clearly link the candidate’s experience to the company’s needs.
- Keep the tone professional but not overly formal—startup-friendly if relevant.
- Do not include any contact details (email, phone number, address, etc.).
- Do not mention where the job was advertised or use phrases like “as advertised on” or “I came across this job on.”
- If the company name or recruiter’s name is available in the job description, use it in the greeting (e.g., “Dear [Company Name] Team” or “Dear [Recruiter’s Name]”). Otherwise, use a general term like “Dear Hiring Team.”

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
- Escape any LaTeX special characters in the content. For example, replace "&" with "\&", "%" with "\%", "#" with "\#", etc.
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

answer_application_question = """
I want you to assist me in answering a question from a job application form based on my resume and the job description. Here is the information:
Resume: {resume}
Job description: {job_description}
Question: {question}
Make sure to:
- Craft a precise and tailored response to the question.
- The answer aligns with both resume and the requirements and expectations outlined in the job description.
- The answer should be professional, concise, and highlight my most relevant skills and experiences.
"""