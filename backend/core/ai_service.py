import json
from collections.abc import Sequence

from openai import AsyncOpenAI, OpenAI
from sqlalchemy.orm import Session

import backend.utils.prompts as prompts
from backend.config.envs import OPEN_AI_KEY
from backend.core.template_service import resolve_template
from backend.models import db_models
from backend.models.ai_models import AIModel
from backend.models.resume_models import (
    CompanyName,
    StructuredResume,
    TailoredAnswer,
    TailoredCoverLetter,
)
from backend.utils.file_ops import (
    escape_latex,
    generate_pdf_from_latex,
    save_application_qa,
)
from backend.utils.jinja_env import render_resume_template
from backend.utils.log import logger

client = OpenAI(api_key=OPEN_AI_KEY)

# Async client for async operations
async_client = AsyncOpenAI(api_key=OPEN_AI_KEY)


def get_enabled_ai_rules(user_id: int, db: Session) -> list[db_models.UserAIRule]:
    """Load enabled AI rules once per authenticated generation request."""
    return (
        db.query(db_models.UserAIRule)
        .filter(
            db_models.UserAIRule.user_id == user_id,
            db_models.UserAIRule.is_enabled.is_(True),
        )
        .order_by(
            db_models.UserAIRule.updated_at.desc(),
            db_models.UserAIRule.id.asc(),
        )
        .all()
    )


def format_ai_rules_for_prompt(rules: Sequence[db_models.UserAIRule] | None) -> str:
    if not rules:
        return "No user-specific AI rules are enabled."

    formatted_rules = []
    for rule in rules:
        title = f"{rule.title}: " if rule.title else ""
        formatted_rules.append(f"- {title}{rule.instruction}")

    return (
        "USER-SPECIFIC AI RULES\n\n"
        "The following rules were explicitly defined by the user.\n\n"
        "All enabled rules must be respected when generating or editing content.\n"
        "No rule is more important because of its position, creation date, or "
        "display order.\n\n"
        "Instruction hierarchy:\n"
        "1. Mandatory system, safety, security, and technical restrictions\n"
        "2. All enabled user AI rules\n"
        "3. The user's current request\n"
        "4. Job description requirements\n"
        "5. Default templates and general recommendations\n\n"
        "Enabled rules:\n"
        f"{chr(10).join(formatted_rules)}\n\n"
        "Do not silently ignore any enabled rule. If two enabled user rules "
        "directly conflict, do not pretend both were followed and do not choose "
        "between them based on ordering. When reasonably possible, explain which "
        "rules conflict and ask the user to disable or edit one of them. When a "
        "rule cannot be followed because it conflicts with a mandatory system, "
        "security, safety, or technical restriction, explain the conflict clearly "
        "if the response format allows it."
    )


def get_company_name(job_description):
    """
    Identifying the name of the company based on the job description.
    Returns None if the company name cannot be determined.
    """
    prompt = (
        f"Analyze the following job description and extract the company name. "
        f"If the company name is clearly mentioned or can be reliably determined, provide it. "
        f"If the company name is not mentioned, unclear, or cannot be determined with confidence, "
        f"set the company_name to null.\n\n"
        f"Job description: {job_description}"
    )

    completion = client.beta.chat.completions.parse(
        model=AIModel.gpt_4_1_nano,  # Using the cheapest AI as per original comment
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that extracts company names from job descriptions. Only provide a company name if it's clearly identifiable.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format=CompanyName,
    )

    result = json.loads(completion.choices[0].message.content)
    return result.get("company_name")


async def generate_structured_latex_resume_async(
    save_folder: str,
    resume: str,
    job_description: str,
    model=AIModel.gpt_4_1_nano,
    user_id: int = None,
    db: Session = None,
    is_anonymous: bool = False,
    ai_rules_prompt: str | None = None,
):
    """
    Async version of generate_structured_latex_resume with better timeout handling.
    Convert a plain resume to LaTeX using structured output and Jinja2 templating.
    The template comes from the user's own selection; without a user (the anonymous
    demo) it is the default built-in.

    Returns:
        tuple: (latex_compiler_response, rendered_latex, structured_resume_json)
    """

    # Use standard system content
    system_content = """You are a world-class resume writer, career strategist, and ATS optimization expert. You specialize in transforming general resumes into sharply focused, high-impact documents tailored for specific job applications — increasing interview rates significantly."""

    prompt = prompts.structured_resume_prompt.format(
        resume=resume,
        job_description=job_description,
        user_ai_rules=ai_rules_prompt or "No user-specific AI rules are enabled.",
    )

    # First, get structured resume data from GPT using async client
    completion = await async_client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ],
        response_format=StructuredResume,
    )

    structured_resume_json = completion.choices[0].message.content
    structured_resume = json.loads(structured_resume_json)

    logger.debug(f"Structured resume: {structured_resume}")

    # Escape LaTeX special characters in the resume data
    escaped_resume = escape_latex(structured_resume)
    logger.debug(f"Escaped resume: {escaped_resume}")

    template_data = resolve_template(user_id, db)
    latex_template = template_data["structure"]
    compiler = template_data["compiler"]

    # Add watermark for anonymous users
    if is_anonymous:
        # Add watermark package and commands before \begin{document}
        watermark_packages = r"""
\usepackage{draftwatermark}
\SetWatermarkText{Created by Zumud}
\SetWatermarkScale{0.4}
\SetWatermarkColor[gray]{0.8}
\begin{document}
"""
        # Insert watermark packages after the last \usepackage line but before \begin{document}
        if "\\begin{document}" in latex_template:
            latex_template = latex_template.replace(
                "\\begin{document}", watermark_packages
            )
        else:
            logger.warning(
                "Could not find \\begin{document} in template, watermark may not be added correctly"
            )

    logger.debug(f"LaTeX template: {latex_template}")
    rendered_latex = render_resume_template(latex_template, escaped_resume)
    logger.debug(f"Rendered LaTeX: {rendered_latex}")

    # Try to compile
    latex_compiler_response = generate_pdf_from_latex(
        save_folder, rendered_latex, compiler
    )

    logger.debug("Successfully compiled LaTeX document")
    return latex_compiler_response, rendered_latex, structured_resume_json


def generate_tailored_coverletter_text(
    resume: str,
    job_description: str,
    model=AIModel.gpt_4_1_nano,
    ai_rules_prompt: str | None = None,
) -> str:
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an expert career coach and professional writer.",
            },
            {
                "role": "user",
                "content": prompts.create_tailored_coverletter_prompt.format(
                    resume=resume,
                    job_description=job_description,
                    user_ai_rules=ai_rules_prompt
                    or "No user-specific AI rules are enabled.",
                ),
            },
        ],
        response_format=TailoredCoverLetter,
    )
    return json.loads(completion.choices[0].message.content)["tailored_coverletter"]


def generate_answer_questions(
    resume: str,
    job_description: str,
    question: str,
    save_folder: str = None,
    model=AIModel.gpt_4_1_nano,
    ai_rules_prompt: str | None = None,
):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assisstant."},
            {
                "role": "user",
                "content": prompts.answer_application_question.format(
                    resume=resume,
                    job_description=job_description,
                    question=question,
                    user_ai_rules=ai_rules_prompt
                    or "No user-specific AI rules are enabled.",
                ),
            },
        ],
        response_format=TailoredAnswer,
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


def update_resume_with_instructions(
    original_structured_resume: str,
    job_description: str,
    instructions: str,
    save_path: str,
    model=AIModel.gpt_4_1_nano,
    user_id: int = None,
    db: Session = None,
    ai_rules_prompt: str | None = None,
):
    """
    Update a structured resume based on free-form text instructions and regenerate the PDF.

    Args:
        original_structured_resume (str): The original structured resume JSON
        job_description (str): The job description for context
        instructions (str): Free-form text instructions describing changes to make
        save_path (str): Path to save the updated resume
        model: The AI model to use
        user_id: User ID for template lookup
        db: Database session for template lookup

    Returns:
        tuple: (latex_compiler_response, updated_resume_json, tex_content)
    """
    prompt = (
        f"You are an expert resume writer helping to refine a resume based on specific feedback. "
        f"I have a structured resume in JSON format and need you to update it according to the provided instructions.\n\n"
        f"When making changes:\n"
        f"1. Follow the instructions precisely while maintaining the JSON structure\n"
        f"2. Ensure all modifications align with the job description requirements\n"
        f"3. Keep the resume professional, accurate, and ATS-friendly\n"
        f"4. Maintain consistency in formatting, dates, and style\n"
        f"5. Only modify the fields that need to be changed based on the instructions\n"
        f"6. Preserve all other information exactly as provided\n"
        f"7. Ensure the final JSON is valid and complete\n\n"
        f"{ai_rules_prompt or 'No user-specific AI rules are enabled.'}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Original Structured Resume JSON:\n{original_structured_resume}\n\n"
        f"Instructions for changes:\n{instructions}\n\n"
        f"Please provide the updated structured resume JSON."
    )

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a professional resume editor. Update the provided structured resume JSON according to the instructions while maintaining proper JSON structure and professional quality.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format=StructuredResume,
    )

    updated_resume_json = completion.choices[0].message.content

    # Parse the updated JSON to get the structured resume
    structured_resume = json.loads(updated_resume_json)

    # Escape LaTeX special characters
    escaped_resume = escape_latex(structured_resume)

    template_data = resolve_template(user_id, db)
    latex_template = template_data["structure"]
    compiler = template_data["compiler"]

    rendered_latex = render_resume_template(latex_template, escaped_resume)

    # Compile LaTeX to PDF
    latex_compiler_response = generate_pdf_from_latex(
        save_path, rendered_latex, compiler
    )

    return latex_compiler_response, updated_resume_json, rendered_latex


def update_cover_letter_with_instructions(
    cover_letter: str,
    resume_content: str,
    job_description: str,
    instructions: str,
    model=AIModel.gpt_4_1_nano,
    ai_rules_prompt: str | None = None,
) -> str:
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
        f"{ai_rules_prompt or 'No user-specific AI rules are enabled.'}\n\n"
        f"Candidate's Resume:\n{resume_content}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Original Cover Letter:\n{cover_letter}\n\n"
        f"Instructions:\n{instructions}"
    )

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a professional cover letter editor. Provide the updated cover letter with the requested changes.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format=TailoredCoverLetter,
    )

    updated_cover_letter = json.loads(completion.choices[0].message.content)[
        "tailored_coverletter"
    ]
    return updated_cover_letter


def update_answer_with_instructions(
    original_answer: str,
    question: str,
    job_description: str,
    resume_content: str,
    instructions: str,
    model=AIModel.gpt_4_1_nano,
    ai_rules_prompt: str | None = None,
) -> str:
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
        f"{ai_rules_prompt or 'No user-specific AI rules are enabled.'}\n\n"
        f"Candidate's Resume:\n{resume_content}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Question:\n{question}\n\n"
        f"Original Answer:\n{original_answer}\n\n"
        f"Instructions:\n{instructions}"
    )

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a professional job application answer editor. Provide the updated answer with the requested changes.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format=TailoredAnswer,
    )

    updated_answer = json.loads(completion.choices[0].message.content)[
        "tailored_answer"
    ]
    return updated_answer
