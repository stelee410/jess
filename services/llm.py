from utils.config import switch_to_ernie
import openai
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
        return openai.ChatCompletion.create(model=model, messages=messages,temperature=temperature)