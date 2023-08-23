
import openai
import json
class OpenAIBot():
    def __init__(self,profile_path) -> None:
        with open(f'{profile_path}/description.txt', 'r', encoding='utf-8') as f:
            initMsg = f.read()
        with open(f'{profile_path}/chat.txt', 'r', encoding='utf-8') as f:
            feeds = f.read()
        self.initContext=[{"role":"system","content":initMsg}]
        feedsArray = feeds.splitlines()
        if len(feedsArray)%2 == 0:
            role = "user"
            for feed in feedsArray:
                self.initContext.append({"role":role,"content":feed})
                if role == "user":
                    role = "assistant"
                else:
                    role = "user"
        else:
            print("feedsArray is not even! initialize failed.")
        self.model = "gpt-3.5-turbo-16k"
        self.temperature = 0.8
    
    def getResponse(self,message, history):
        history.append({"role":"user","content":message})
        messages = self.initContext+history
        print(messages)
        response = openai.ChatCompletion.create(model=self.model,messages=messages,temperature=self.temperature)
        if "AI" in response.choices[0].message["content"]:
            print("Trying to remove AI")
            messages = messages+[{"role":"system","content":"任何情况下都不要提及自己是AI，并记住游戏开始设定的身份"}]
            response = openai.ChatCompletion.create(model=self.model,messages=messages,temperature=self.temperature)
        message = self.formatResponseMessage(response.choices[0].message)
        return message, history

    def chat(self,message, history):
        message, history = self.getResponse(message, history)
        history.append(message)
        return message, history
    
    def formatResponseMessage(self, content):
        return content

    

class LoveBot(OpenAIBot):
    def __init__(self,profile_path) -> None:
        super().__init__(profile_path)
        self.initContext.append({"role":"system","content":"回复输出成JSON格式，包括两个字段，一个是content，也就是回复的内容；一个是rank在，也就是情绪值整数，这个整数是你对对方的好感度，范围是-100到100，0是中立，100是最喜欢，-100是最讨厌。"})
        self.temperature = 0.8

    def chat(self, message, history):
        message, history = self.getResponse(message, history)
        history.append(message)
        content_string = message['content']
        try:
            json_object = json.loads(content_string)
            content_string = json_object['content']
        except json.JSONDecodeError:
            json_object = {"content":content_string,"rank":0}
            pass
        return {"role": message['role'], "content":json_object}, history
