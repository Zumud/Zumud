import json

from loguru import logger
from openai import OpenAI
from jinja2 import Template

import backend.utils.prompts as prompts
from backend.config.envs import OPEN_AI_KEY
from backend.models.ai_models import AIModel
from backend.models.templates import ResumeTemplate, Template_Details
from backend.utils.file_ops import generate_pdf_from_latex, save_application_qa, escape_latex
from backend.utils.log import logger
from backend.models.resume_models import TailoredResume, TailoredCoverLetter, TailoredAnswer, StructuredResume

client = OpenAI(api_key=OPEN_AI_KEY)

def ai_prompt(prompt: str, model=AIModel.gpt_4_1_nano) -> str:
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
    )
    return completion.choices[0].message.content

def get_company_name(job_description):
    """
    Identifying the name of the company based on the job description
    """
    company_name = ai_prompt(
        f"Give the name of the company that this job description is for. As the output just give the name, nothing else. Job description: {job_description}"
    )  # Since this is a simple task we use the cheapest ai
    return company_name

def generate_tailored_resume_text(resume: str, job_description: str, model=AIModel.gpt_4_1_nano, template=ResumeTemplate.MTeck_resume) -> str:
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert in resume writing."},
            {"role": "user", "content": prompts.create_tailored_resume.format(resume=resume, job_description=job_description, num_pages=Template_Details[template]['num_pages'])}
        ],
        response_format=TailoredResume
    )
    tailored_resume = json.loads(completion.choices[0].message.content)["tailored_resume"]
    logger.debug(f"The tailored resume plain text is: {tailored_resume}")
    return tailored_resume

def generate_structured_latex_resume(save_folder: str, resume: str, job_description: str, model=AIModel.gpt_4_1_nano, template=ResumeTemplate.MTeck_resume):
    """
    Convert a plain resume to LaTeX using structured output and Jinja2 templating.
    
    Returns:
        tuple: (latex_compiler_response, rendered_latex, structured_resume_json)
    """
    # First, get structured resume data from GPT
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": """You are a world-class resume writer, career strategist, and ATS optimization expert. You specialize in transforming general resumes into sharply focused, high-impact documents tailored for specific job applications — increasing interview rates significantly. Your sole goal is to maximize the candidate's chances of getting an interview by rewriting their resume content to match a specific job description. Your output will be structured as JSON for formatting later, but you should focus purely on crafting the best possible content."""},
            {"role": "user", "content": prompts.structured_resume_prompt.format(
                resume=resume,
                job_description=job_description,
                schema=json.dumps(StructuredResume.model_json_schema(), indent=2)
            )}
        ],
        response_format=StructuredResume
    )
    
    structured_resume_json = completion.choices[0].message.content
    structured_resume = json.loads(structured_resume_json)
    
    logger.debug(f"Structured resume: {structured_resume}")
    
    # Escape LaTeX special characters in the resume data
    escaped_resume = escape_latex(structured_resume)
    logger.debug(f"Escaped resume: {escaped_resume}")
    
    # Get the LaTeX template
    latex_template = Template_Details[template]['structure']
    logger.debug(f"LaTeX template: {latex_template}")
    
    # Create Jinja2 template and render
    jinjatex_template = Template(latex_template)
    logger.debug(f"Jinjatex Template: {jinjatex_template}")
    rendered_latex = jinjatex_template.render(escaped_resume)
    logger.debug(f"Rendered LaTeX: {rendered_latex}")
    
    # Try to compile
    compiler = Template_Details[template]['compiler']
    latex_compiler_response = generate_pdf_from_latex(save_folder, rendered_latex, compiler)
    
    if b"error: " in latex_compiler_response.content:
        error_msg = latex_compiler_response.content.decode('utf-8')
        logger.error(f"LaTeX compilation error: {error_msg}")
        raise ValueError(f"Failed to compile LaTeX document: {error_msg}")
    
    logger.debug("Successfully compiled LaTeX document")
    return latex_compiler_response, rendered_latex, structured_resume_json

def generate_tailored_coverletter_text(resume: str, job_description: str, model=AIModel.gpt_4_1_nano) -> str:
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert career coach and professional writer."},
            {"role": "user", "content": prompts.create_tailored_coverletter_prompt.format(resume=resume, job_description=job_description)}
        ],
        response_format=TailoredCoverLetter
    )
    return json.loads(completion.choices[0].message.content)["tailored_coverletter"]

def ai_messages(messages: list[tuple[str, str]], model=AIModel.gpt_4_1_nano) -> str:
    completion = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return completion.choices[0].message.content

def generate_answer_questions(resume: str, job_description: str, question: str, save_folder: str = None, model=AIModel.gpt_4_1_nano):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assisstant."},
            {"role": "user", "content": prompts.answer_application_question.format(resume=resume, job_description=job_description, question=question)}
        ],
        response_format=TailoredAnswer
    )
    
    answer = json.loads(completion.choices[0].message.content)["tailored_answer"]
    
    # Save the question and answer if save_folder is provided
    if save_folder:
        try:
            file_path = save_application_qa(save_folder, question, answer)
            logger.debug(f"Application Q&A saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving application Q&A: {str(e)}")
    
    return answer

def update_resume_with_instructions(resume_json: str, original_resume_content: str, job_description: str, instructions: str, model=AIModel.gpt_4_1_nano) -> str:
    """
    Update a JSON resume based on free-form text instructions.
    
    Args:
        resume_json (str): The original resume JSON
        original_resume_content (str): The user's full resume content from their profile
        job_description (str): The job description to tailor the resume for
        instructions (str): Free-form text instructions describing changes to make
        model: The AI model to use
        
    Returns:
        str: The updated resume JSON
    """
    prompt = (
        f"You are an expert resume tailoring specialist who helps job seekers make strategic updates to their resumes. "
        f"Your goal is to help candidates create resumes that effectively highlight relevant skills and experiences for specific job opportunities.\n\n"
        f"When updating a resume based on instructions, please:\n\n"
        f"1. Make only the changes requested in the instructions\n"
        f"2. Keep the overall structure and JSON format intact\n"
        f"3. Focus on emphasizing experiences and skills that match the job description\n"
        f"4. Ensure all achievements are specific, measurable, and impactful\n"
        f"5. Maintain professional language throughout\n"
        f"6. You can reference information from the original resume content if it's not in the JSON but relevant to the instructions\n"
        f"7. Prioritize keywords and phrases from the job description when appropriate\n"
        f"8. Preserve the chronological order of experiences and education\n\n"
        f"Return the modified resume that conforms to the provided schema. "
        f"Ensure all fields match the expected types and formats.\n\n"
        f"Original Resume Content (for reference):\n{original_resume_content}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Original Resume JSON (to be modified):\n{resume_json}\n\n"
        f"Instructions:\n{instructions}"
    )
    
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a resume editor assistant. Provide the updated resume in the specified format."},
            {"role": "user", "content": prompt}
        ],
        response_format=StructuredResume
    )
    
    updated_resume = completion.choices[0].message.content
    return updated_resume

def edit_resume_and_generate_pdf(save_path: str, resume_json: str, original_resume_content: str, job_description: str, edit_instructions: str, model=AIModel.gpt_4_1_nano, template=ResumeTemplate.MTeck_resume):
    """
    Process edit instructions on a resume JSON and generate a PDF.
    
    Args:
        save_path (str): Path to save the updated resume files
        resume_json (str): Original resume JSON
        original_resume_content (str): The user's full resume content from their profile
        job_description (str): The job description to tailor the resume for
        edit_instructions (str): Free-form text instructions for editing
        model: AI model to use
        template: LaTeX template to use
        
    Returns:
        tuple: (pdf_compiler_response, updated_resume_json)
    """
    # Update the resume JSON using AI
    updated_resume_json = update_resume_with_instructions(
        resume_json,
        original_resume_content,
        job_description,
        edit_instructions,
        model
    )
    
    # Parse the updated JSON to get the structured resume
    structured_resume = json.loads(updated_resume_json)
    
    # Escape LaTeX special characters
    escaped_resume = escape_latex(structured_resume)
    
    # Get the LaTeX template
    latex_template = Template_Details[template]['structure']
    
    # Create Jinja2 template and render
    jinjatex_template = Template(latex_template)
    rendered_latex = jinjatex_template.render(escaped_resume)
    
    # Compile LaTeX to PDF
    compiler = Template_Details[template]['compiler']
    latex_compiler_response = generate_pdf_from_latex(save_path, rendered_latex, compiler)
    
    if b"error: " in latex_compiler_response.content:
        error_msg = latex_compiler_response.content.decode('utf-8')
        raise ValueError(f"Failed to compile LaTeX document: {error_msg}")
    
    return latex_compiler_response, updated_resume_json

def update_cover_letter_with_instructions(cover_letter: str, resume_content: str, job_description: str, instructions: str, model=AIModel.gpt_4_1_nano) -> str:
    """
    Update a cover letter based on free-form text instructions.
    
    Args:
        cover_letter (str): The original cover letter text
        resume_content (str): The user's resume content for reference
        job_description (str): The job description for context
        instructions (str): Free-form text instructions describing changes to make
        model: The AI model to use
        
    Returns:
        str: The updated cover letter text
    """
    prompt = (
        f"You are an expert career coach specializing in cover letters that win interviews. You help job seekers refine their cover letters to make them compelling, relevant, and tailored to specific positions.\n\n"
        f"I have a cover letter that needs improvement based on specific instructions. I'll provide you with the candidate's resume, job description, current cover letter, and editing instructions.\n\n"
        f"When editing the cover letter, please:\n\n"
        f"1. Make only the changes requested in the instructions\n"
        f"2. Keep the overall structure and flow unless specified otherwise\n"
        f"3. Ensure the letter maintains a clear introduction, body paragraphs that demonstrate value, and strong closing\n"
        f"4. Highlight relevant qualifications and experiences from the resume that align with the job description\n"
        f"5. Maintain a professional yet conversational tone appropriate for the industry\n"
        f"6. Use concrete examples of achievements from the resume when applicable\n"
        f"7. Keep paragraphs focused and concise (3-5 sentences per paragraph)\n"
        f"8. Ensure the letter expresses enthusiasm for the role and organization\n"
        f"9. Ensure the letter references skills and experiences that actually appear in the resume\n"
        f"10. Tailor the content to address specific requirements mentioned in the job description\n"
        f"11. Avoid clichés and generic language in favor of specific, compelling content\n\n"
        f"Return only the improved cover letter text, maintaining appropriate professional language and formatting.\n\n"
        f"Candidate's Resume:\n{resume_content}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Original Cover Letter:\n{cover_letter}\n\n"
        f"Instructions:\n{instructions}"
    )
    
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional cover letter editor. Provide the updated cover letter with the requested changes."},
            {"role": "user", "content": prompt}
        ],
        response_format=TailoredCoverLetter
    )
    
    updated_cover_letter = json.loads(completion.choices[0].message.content)["tailored_coverletter"]
    return updated_cover_letter

def update_answer_with_instructions(original_answer: str, question: str, job_description: str, resume_content: str, instructions: str, model=AIModel.gpt_4_1_nano) -> str:
    """
    Update an application question answer based on free-form text instructions.
    
    Args:
        original_answer (str): The original answer text
        question (str): The application question being answered
        job_description (str): The job description for context
        resume_content (str): The user's resume content for reference
        instructions (str): Free-form text instructions describing changes to make
        model: The AI model to use
        
    Returns:
        str: The updated answer text
    """
    prompt = (
        f"You are an expert job application coach specializing in interview questions. You help candidates refine their answers to make them more impactful, relevant, and tailored to specific positions.\n\n"
        f"I have an answer to a job application question that needs refinement based on specific instructions. I'll provide you with the candidate's resume, job description, question, original answer, and edit instructions.\n\n"
        f"When updating the answer, please:\n"
        f"1. Make only the changes requested in the instructions\n"
        f"2. Keep the overall structure and flow unless specified otherwise\n"
        f"3. Ensure the answer directly addresses the question asked\n"
        f"4. Highlight relevant skills/experiences from the resume that match the job description\n"
        f"5. Maintain a professional, confident tone\n"
        f"6. Use concrete examples and quantifiable achievements from the resume when possible\n"
        f"7. Keep the answer concise and impactful (typically 3-5 sentences for brief answers, 2-3 paragraphs for detailed ones)\n"
        f"8. Ensure all information is truthful and accurately reflects what's in the resume\n\n"
        f"Return only the improved answer text, maintaining appropriate professional language and formatting.\n\n"
        f"Candidate's Resume:\n{resume_content}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Question:\n{question}\n\n"
        f"Original Answer:\n{original_answer}\n\n"
        f"Instructions:\n{instructions}"
    )
    
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional job application answer editor. Provide the updated answer with the requested changes."},
            {"role": "user", "content": prompt}
        ],
        response_format=TailoredAnswer
    )
    
    updated_answer = json.loads(completion.choices[0].message.content)["tailored_answer"]
    return updated_answer
