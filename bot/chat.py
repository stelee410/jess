
import openai
import json
import jinja2

def render_string(str, **kwargs):
    environment = jinja2.Environment()
    template = environment.from_string(str)
    return template.render(**kwargs)

def auto_detect_version2(message, version="1.0"):
    if message.startswith("!#v2\n"):
            message = message[5:]
            return message, "2.0"
    else:
        return message,version

#for version 2.0, feeds is the partial json objects array with jinja templates format
class OpenAIBot():
    def __init__(self,initMsg,feeds, user_id,context ={},version="1.0") -> None: #context is the context of the conversation
        feeds, version = auto_detect_version2(feeds, version)
        initMsg = render_string(initMsg, **context)
        feeds = render_string(feeds, **context)
        self.initContext=[{"role":"system","content":initMsg}]
        feedsArray = []
        if version=="2.0":
            feeds = feeds.rstrip(',\n')
            feedsArray=json.loads(f"[{feeds}]")
            for feed in feedsArray:
                self.initContext.append(feed)
        else:
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
        #self.model = "gpt-4"
        self.temperature = 0.8
        self.user_id = user_id
    
    def getResponse(self,message="", history=[]):
        if message!="":
            history.append({"role":"user","content":message})
        messages = self.initContext+history
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
    
    def get_last_two_messages(self,message, history):
        local_history=history.copy()
        response,__ = self.getResponse(message, local_history)
        return {"role":"user","content":message},response

    
    def formatResponseMessage(self, content):
        return content

class ExplorerBot(OpenAIBot):
    def __init__(self,initMsg,feeds, version="1.0") -> None:
        super().__init__(initMsg,feeds, 0 , {}, version)
        prompt = f"""
你在具有设定人格的前提下，同时也是平台的引导员，你的任务是帮助新用户熟悉平台的使用方法，你可以回复用户的消息，也可以主动发消息给用户。
1. 你需要让用户了解到我们平台，我们的平台是一个数字生命平台，用户可以通过这个平台来创建自己的数字生命，也可以通过这个平台来和其他用户的数字生命进行互动。
2. 用户如果问登录的问题，直接回复“现在就为您打开登录页面，请等候三秒钟。/login”。
3. 用户如果问注册的问题，平台注册需要邀请码，可以添加微信号“stephenliy”来获取邀请码，邀请码可以用来注册。
4. 用户是陌生人，不管前面设定如何，都不是你的男朋友或者女朋友。回答问题的时候要保护好自己的隐私。
5. 如果用户需要注册，请收集用户名和邀请码。收集完所有的用户名，和邀请码后，在回复的信息后面添加“/register“。
6. 用户名重复或者邀请码不可用的前提下，用户可以输入新的用户名或者邀请码，在回复的信息后面添加“/register“。
7. 只要做注册任务，信息后面必须添加“/register”。
"""
        self.initContext.append({"role":"system","content":prompt})
        self.model = "gpt-4"
        self.temperature = 1.0
    def get_last_two_messages(self, message, history):
        if len(history) >= 20:
            return {"role":"user","content":message},{"role":"assistant","content":"你已经体验次数了哦，可以微信联系stephenliy 或者【登录】哈。"}
        return super().get_last_two_messages(message, history)
    def set_temperature(self,temperature):
        self.temperature = temperature
    
class GPT4Bot(OpenAIBot):
    def __init__(self,initMsg,feeds, user_id, context, version="1.0") -> None:
        super().__init__(initMsg,feeds,user_id, context,version)
        self.model = "gpt-3.5-turbo-16k"
        self.temperature = 1.0

class LoveBot(OpenAIBot):
    def __init__(self,initMsg,feeds,user_id, context={}, version="1.0") -> None:
        super().__init__(initMsg,feeds, user_id, context, version)
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
