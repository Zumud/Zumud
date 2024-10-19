create_tailored_resume_prompt = """Please help me tailor my resume to match the following job description, emphasizing relevant skills and experiences to maximize my chances of getting an interview.

**My Current Resume:**
{resume}

**Job Description:**
{job_description}

**Instructions:**
- Highlight and expand on experiences that align closely with the job requirements.
- Incorporate keywords and phrases from the job description into my resume.
- Remove or de-emphasize experiences that are not relevant to the job.
- Ensure the resume remains professional and well-organized.
- Keep the final resume within two pages.

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