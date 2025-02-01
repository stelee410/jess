from utils.config import switch_to_ernie
from openai import OpenAI

client = OpenAI()
import ernie

model_mapping={
    "gpt-3.5-turbo-16k":"ernie-bot",
    "gpt-4":"ernie-bot-4"
}

def create(model, messages, temperature):
    if switch_to_ernie:
        model = model_mapping[model]
        return ernie.ChatCompletion.create(model=model, messages=messages,temperature=temperature)
    else:
        response = client.chat.completions.create(model=model, messages=messages,temperature=temperature)
        # 确保 choices[0].message 是字典格式
        response.choices[0].message = response.choices[0].message.model_dump()
        return response