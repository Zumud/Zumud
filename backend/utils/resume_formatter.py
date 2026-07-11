from openai import AsyncOpenAI

from backend.config.envs import OPEN_AI_KEY
from backend.models.ai_models import AIModel

# Create an async client for OpenAI API calls
client = AsyncOpenAI(api_key=OPEN_AI_KEY)


async def format_resume_text(raw_text: str, model=AIModel.gpt_4_1_nano) -> str:
    """
    Asynchronously format extracted resume text into a clean, structured format suitable for AI processing.

    Args:
        raw_text (str): The raw text extracted from a resume PDF
        model (AIModel): The AI model to use for formatting

    Returns:
        str: Formatted resume text optimized for AI processing
    """
    if not raw_text or not raw_text.strip():
        return ""

    # Create a prompt for the AI to format the resume
    system_prompt = """You are an expert in resume formatting and parsing. 
Your task is to take raw text extracted from a resume PDF and format it into a clean, well-structured plain text resume.

Guidelines:
1. Preserve all important information from the original text
2. Standardize and properly label all sections (EXPERIENCE, EDUCATION, SKILLS, etc.)
3. Ensure consistent spacing and formatting (use blank lines between sections)
4. Remove any extraction artifacts or encoding issues
5. Place contact information (name, email, phone) at the top
6. Organize content into clearly defined sections with proper headings
7. Maintain chronological order within experience and education sections
8. Keep bullet points for achievements and responsibilities
9. Remove any irrelevant or duplicate information
10. Format the text to be easily readable for both humans and AI systems

Your output should ONLY include the formatted plain text resume without any explanations or comments."""

    user_prompt = f"Here is the raw text extracted from a resume PDF. Please format it into a clean, structured plain text resume:\n\n{raw_text}"

    # Call the OpenAI API asynchronously
    response = await client.chat.completions.create(
        model=model,  # Using the AI model from parameter
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,  # Low temperature for more consistent formatting
        max_tokens=4000,  # Allow enough tokens for the formatted resume
    )

    # Extract and return the formatted text
    formatted_text = response.choices[0].message.content.strip()
    return formatted_text
