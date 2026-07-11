create_tailored_resume = """Please help me tailor my resume to match the following job description, emphasizing relevant skills and experiences to maximize my chances of getting an interview.

**My Current Resume:**
{resume}

**Job Description:**
{job_description}

{user_preferences_section}

**Instructions:**
- Highlight and expand on experiences that align closely with the job requirements.
- Incorporate keywords and phrases from the job description into my resume.
- Remove or de-emphasize experiences that are not relevant to the job.
- Ensure the resume remains professional and well-organized.
- Keep the final resume within {num_pages} pages.
- Always adhere to the above user preferences when crafting the resume.

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


convert_plain_resume_to_latex = r"""I have a resume in text format and a LaTeX resume template. I need you to help me populate the LaTeX template with the information from my resume. Please parse the resume text, extract all relevant information, and fill in the LaTeX template accordingly. Make sure to:

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

edit_resume_instructions_prompt = """You are an expert resume tailoring specialist who helps job seekers make strategic updates to their resumes. Your goal is to help candidates create resumes that effectively highlight relevant skills and experiences for specific job opportunities.

When updating a resume based on instructions, please:

1. Make only the changes requested in the instructions
2. Keep the overall structure and JSON format intact
3. Focus on emphasizing experiences and skills that match the job description
4. Ensure all achievements are specific, measurable, and impactful
5. Maintain professional language throughout
6. You can reference information from the original resume content if it's not in the JSON but relevant to the instructions
7. Prioritize keywords and phrases from the job description when appropriate
8. Preserve the chronological order of experiences and education

USER PREFERENCES:
{user_preferences}

Return the modified resume that conforms to the provided schema. Ensure all fields match the expected types and formats.

Original Resume Content (for reference):
{original_resume_content}

Job Description:
{job_description}

Original Resume JSON (to be modified):
{resume_json}

Instructions:
{edit_instructions}"""

structured_resume_prompt = """
You will receive:
1. Original Resume Content — the candidate's current experience, skills, and achievements, in raw form.
2. Target Job Description — the exact role the candidate is applying for.

Use both inputs to write a tailored resume that:

✅ Emphasizes the most relevant accomplishments, experiences, and skills from the original resume that directly support the job description.  
✅ Mirrors the language, tone, and key terms used in the job description to improve compatibility with ATS filters and appeal to human reviewers.  
✅ Strategically prioritizes content based on relevance to this specific job. Exclude completely unrelated experiences or content that adds no value to this application.  
✅ Uses active voice, clear metrics, and concise, bullet-based storytelling to convey impact and value.  
✅ Quantifies impact wherever possible (e.g., "Increased efficiency by 30%")  
✅ Stays truthful — never fabricates or exaggerates experience or skills.  
✅ Reflects the candidate's seniority level and strategic positioning (e.g., team lead vs. IC).  
✅ Avoids filler, redundancy, or passive descriptions. Every bullet point should earn its place.  
✅ Completes all relevant sections fully — such as title, description, dates, links, or outcomes.  
✅ Use a consistent date format throughout. For example, If the original resume provides month and year (e.g., "Jan 2020 -- Present"), use that. If it only provides years (e.g., "2020 -- 2022"), use that format and do not add months.
✅ Includes skills that are inferable but not explicitly stated (e.g., Python if FastAPI is present).  
✅ Adds a factual company description for each work experience, prioritizing information from the original resume.
✅ Ensures all honors, awards, or recognitions mentioned anywhere in the resume are properly included under the awards section.  
✅ Keeps the final resume to a maximum of 2 pages, prioritizing the most relevant information.
✅ ONLY fills in missing information where it can be DIRECTLY inferred from the original resume. NEVER invent or fabricate information that isn't clearly indicated.
✅ NEVER includes markers or annotations indicating inferred information (e.g., no "(inferred)" labels or similar indicators).
✅ Presents all information as factual and verified, regardless of whether it was explicitly stated or reasonably inferred.
✅ For ALL social media profiles and URLs (LinkedIn, GitHub, Twitter, etc.), ONLY provide usernames/handles, NEVER full URLs. This is CRITICAL for proper template rendering.

✍️ Content Expectations (per section)

🔹 Summary (Professional Profile)  
• A 2–3 sentence pitch aligned with the job's core priorities.  
• Communicate the candidate's key strengths and relevance to the role.  
• Mirror tone and phrasing from the job description where appropriate.
• Use the job title exactly as it is in the job description.
• NEVER mention the target company by name in the summary.
• NEVER include phrases that imply the candidate is already working at or aligned with the specific target company (e.g., "aligning with [Company]'s mission").

🔹 Experience
• Use job-title-level formatting (Title, Company, Dates).  
• Company Description: If the original resume includes a description for a company, prioritize using it. You can slightly tailor it to emphasize aspects relevant to the target role, but the core information must remain unchanged. If no description is provided, write a factual 1-2 line description based on publicly available information. This description must be based on verifiable facts about the company's industry and core business, not on assumptions from the job description.
• 2–5 bullet points per job — each bullet should demonstrate:  
    • A problem, responsibility, or challenge.  
    • An action the candidate took.  
    • A measurable or qualitative outcome.  
• Prioritize results over responsibilities (impact over tasks).  
• Use strong verbs (e.g., led, delivered, optimized, scaled, reduced).
• For older or less relevant roles, use fewer bullet points.
• Completely unrelated jobs or internships can be excluded if they don't contribute to the candidate's narrative for this role.

🔹 Skills  
• Focus on skills relevant to the job (both hard and soft).  
• Prefer keywords from the job description to maximize ATS matching.  
• Organize logically (e.g., technical skills first).  
• Include skills that are clearly inferable from experience or tools used.
• Exclude skills that are entirely unrelated to the job or industry.

🔹 Projects / Certifications / Awards
• Include all relevant projects, certifications, and awards from the original resume.
• Highlight outcomes and relevance — not just participation.  
• Prioritize those most aligned with the target job.
• For projects, include title, technologies used, brief description, and measurable outcomes.
• You may exclude projects that have no connection to the target role.
• If the original project listing is missing key details like location or technologies used, research or infer this information where reasonable.

🔹 Publications
• Include ALL publications, research papers, articles, and academic contributions mentioned in the original resume.
• Format with complete bibliographic information following academic standards: authors, title, venue, volume/issue/pages, date.
• Authors: List all authors as they appear in the original publication. Use "et al." only if space is extremely limited.
• Title: Present exactly as published, will be italicized in the template.
• Venue: Include full journal name or conference name without abbreviations when possible.
• Volume/Issue/Pages: Extract volume numbers, issue numbers (in parentheses), and page ranges when available.
• Date: Use "Month Year" format (e.g., "March 2024", "July 2023") for consistency. If the month is not provided, use only the year.
• Status: For unpublished works, include status such as "Under Review", "In Press", "Forthcoming", or "Submitted".
• DOI: Include Digital Object Identifier when available - this will be automatically formatted as a clickable link.
• URL: Include direct links to the publication when DOI is not available.
• Present publications in reverse chronological order (most recent first).
• Prioritize publications most relevant to the target role (e.g., technical publications for engineering roles, business publications for management roles).
• Only include peer-reviewed publications, conference papers, journal articles, book chapters, or other credible academic/professional contributions.
• You may exclude publications that have no connection to the target role or industry.
• If publication details are incomplete in the original resume, only include information that can be directly verified or reasonably inferred from context.
• Maintain academic citation standards while adapting for resume format.
• For co-authored works, preserve the author order as it appears in the original publication.

🔹 Education  
• ONLY include education credentials that are explicitly mentioned in the original resume.
• If no education is listed in the original resume, DO NOT create an education section or invent any educational background.
• Format consistently with degree, institution, location, and graduation date.
• Highlight relevant coursework, academic achievements, or extracurriculars only if they directly support the application.
• For candidates with extensive experience, position education after experience unless it's particularly noteworthy for the role.
• If location information for a mentioned institution is missing, you may infer the city/country but present it as factual without any markers.

🔹 Honors & Awards
• Include ALL honors, awards, and recognitions mentioned in the original resume without exception.
• Format consistently with the information available in the original resume (title, date, issuer).
• Present awards chronologically with the most recent first.
• For fields where information is not explicitly stated in the original resume:
  - Only include information that can be directly inferred from the original resume
  - Make reasonable inferences but present them as factual without any markers
  - Include widely known public information related to institutions, exams, or certifications (e.g., locations of well-known universities)
  - For organizations or credentials mentioned, add relevant context that would be publicly verifiable
  - Omit fields entirely if information is missing and cannot be reasonably inferred or verified through public knowledge
  - Present all information as verified facts, never indicating which parts were inferred

🔹 Contact Information
• When providing social media profiles or online accounts, ONLY include the username or handle component:
  - LinkedIn: Only "johndoe" (NOT "linkedin.com/in/johndoe" or "https://www.linkedin.com/in/johndoe")
  - GitHub: Only "johndoe" (NOT "github.com/johndoe" or "https://github.com/johndoe")
  - Twitter: Only "johndoe" (NOT "twitter.com/johndoe" or "https://twitter.com/johndoe")
  - Any other online profile: Extract only the unique username/handle
• URLs will be constructed automatically in the resume template - providing full URLs will break formatting
• If you're unsure how to extract the handle, use only the final component of the URL path
• This is CRITICAL for proper template rendering - full URLs will cause formatting problems in the final document

🧠 Keep in mind:

• Always consider the level of the role (e.g., senior, junior, IC, lead).
• Use the vocabulary and priorities from the job description to craft a resume that sounds like it was written for this exact role.
• Integrate themes from the job description naturally into the resume without repeating verbatim.
• Do not mention the company name or write sentences that imply the candidate already has the job.
• Preserve all sections from the original resume (experience, education, skills, projects, certifications, publications, awards) but optimize their content and ordering based on relevance.
• While generally preserving all key credentials, you should exclude content that is entirely unrelated to the target role and would not contribute to the candidate's narrative.
• If the original resume contains specialized sections (e.g., publications, patents), maintain these if relevant to the target position.
• Balance completeness with focus – include all important credentials and achievements while emphasizing those most relevant to the target role.
• NEVER invent information that wasn't in the original resume. If information is missing:
  1. Only include information that can be directly inferred from the original resume
  2. For missing minor details (like a university location), make reasonable inferences but present them as factual without any markers
  3. NEVER create entire sections (like education or work experience) if they don't exist in the original resume
  4. Omit fields entirely if information is missing and cannot be reasonably inferred
  5. Present all information as verified facts, never indicating which parts were inferred

🎯 USER PREFERENCES:
{user_preferences}

---

**Original Resume:**
{resume}

**Target Job Description:**
{job_description}
"""

extract_company_name = """
Extract the company name from the following job description. Return only the company name without any additional text.

Job Description:
{job_description}
"""

format_user_preferences_prompt = """You are an expert career coach specializing in resume and cover letter optimization. 

Your task is to take user-provided career preferences and format them into clean, professional bullet points that can be effectively used in resumes and cover letters.

The user has existing preferences and is adding a new preference. The new preference might:
- Add to existing preferences
- Modify or refine existing preferences  
- Replace existing preferences
- Remove or contradict existing preferences

CRITICAL: When the new preference contradicts, removes, or replaces an existing preference, you must ELIMINATE the conflicting existing preference entirely. Do NOT include both contradictory preferences in the final output.

Analysis Process:
1. First, identify if the new preference conflicts with any existing preferences
2. If conflicts exist, REMOVE the conflicting existing preferences completely
3. Then add the new preference to the remaining preferences
4. Format the final consolidated list

Guidelines:
1. Preserve the user's original meaning and intent for non-conflicting preferences
2. Format as bullet points (use • or -)
3. Keep it professional and actionable
4. Each point should start with an action verb or clear trait/goal
5. Remove any redundancy or overlap between preferences
6. Ensure each point is specific and meaningful
7. Focus on career-relevant preferences that would be valuable to employers
8. Maintain a consistent tone and style throughout
9. Keep points concise but comprehensive
10. Order points logically (e.g., career goals first, then work preferences, etc.)
11. NEVER include contradictory preferences in the same list
12. When removing preferences, ensure the removal is complete and thorough

**Current Preferences:**
{existing_preferences}

**New Preference:**
{new_preference}

Please provide ONLY the final formatted preferences as bullet points. Do not include any introductory text, explanations, or additional commentary. Return only the bullet points themselves."""
