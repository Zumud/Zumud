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
- Clearly link the candidate's experience to the company's needs.
- Keep the tone professional but not overly formal—startup-friendly if relevant.
- Do not include any contact details (email, phone number, address, etc.), but ensure the letter has a proper valediction (e.g., 'Best regards' or 'Sincerely').
- Do not mention where the job was advertised or use phrases like "as advertised on" or "I came across this job on."
- If the company name or recruiter's name is available in the job description, use it in the greeting (e.g., "Dear [Company Name] Team" or "Dear [Recruiter's Name]"). Otherwise, use a general term like "Dear Hiring Team."

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

structured_resume_prompt = """Resume:
{resume}

Job Description:
{job_description}

Please analyze this resume and job description, and output a structured JSON object
that follows this exact schema:
{schema}

Important:
1. Tailor the content to the job description while preserving factual information
2. Ensure all dates are in a consistent format (e.g., "Jan 2020 -- Present")
3. Keep achievements concise and impactful
4. Include only relevant skills and experiences
5. For each company in the experience section, add a brief description that highlights the company's relevance to the target position
6. If there are honors, awards, or recognitions in the resume, include them in the awards section
7. Format all text properly for LaTeX (escape special characters)
8. Never use 'None' as a value - leave optional fields as empty strings or omit them entirely if the information is not available
9. Do not include placeholder values like "N/A" or "None" in the data - use empty strings instead"""