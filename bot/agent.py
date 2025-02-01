from openai import OpenAI

client = OpenAI()

class Agent():
    def __init__(self, method_name, args_list) -> None:
        self.model = "gpt-3.5-turbo"
        self.temperature = 1.0
        self.method_name = method_name
        self.args_list = args_list
        prompt ="""
你是一个参数翻译程序，你可以将人类自然语言描述的指令翻译成对应的JSON格式参数。字段包括：
"""
        prompt += ','.join(args_list)
        self.system_prompt = prompt

    def getResponse(self, messages):
        new_messages = messages.copy()
        initMsg = [{"role":"system","content":self.system_prompt}]
        new_messages.append({"role":"user","content":"输出参数"})
        response = client.chat.completions.create(model=self.model,messages= initMsg + new_messages,temperature=self.temperature)
        return response.choices[0].message.content
    def get_method_name(self):
        return self.method_name