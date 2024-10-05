from pydantic import BaseModel
from openai import OpenAI
from envs import OPEN_AI_KEY
from models import AIModel

client = OpenAI(api_key=OPEN_AI_KEY)  # we recommend using python-dotenv to add OPENAI_API_KEY="My API Key" to your .env file so that your API Key is not stored in source control.

class TailoredApplication(BaseModel):
    customized_resume: str
    customized_cover_letter: str
    company_name: str

def ai_prompt(prompt: list, model=AIModel.gpt_3_5_turbo_cheap):
    completion = client.chat.completions.create(
        model=model,
        messages=prompt,
        response_format=TailoredApplication  # ensures the out put is a json with the given format
        # [
        #     {"role": "system", "content": "You are a helpful assistant."},
        #     {"role": "user", 
        #      "content": prompt}
        # ]
    )
    return completion.choices[0].message.content


def ai_prompt_str(prompt: str, model=AIModel.gpt_3_5_turbo_cheap):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", 
             "content": prompt}
        ]
    )
    return completion.choices[0].message.content