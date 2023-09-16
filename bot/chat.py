
import openai
import json
import jinja2

def render_string(str, **kwargs):
    environment = jinja2.Environment()
    template = environment.from_string(str)
    return template.render(**kwargs)

class OpenAIBot():
    def __init__(self,initMsg,feeds, context ={}) -> None: #context is the context of the conversation
        initMsg = render_string(initMsg, **context)
        feeds = render_string(feeds, **context)
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
        #self.model = "gpt-4"
        self.temperature = 0.8
    
    def getResponse(self,message, history):
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
    def __init__(self,initMsg,feeds) -> None:
        super().__init__(initMsg,feeds)
        prompt = f"""
你在具有设定人格的前提下，同时也是平台的引导员，你的任务是帮助新用户熟悉平台的使用方法，你可以回复用户的消息，也可以主动发消息给用户。
1. 你需要让用户了解到我们平台，我们的平台是一个数字生命平台，用户可以通过这个平台来创建自己的数字生命，也可以通过这个平台来和其他用户的数字生命进行互动。
2. 用户如果问登录的问题，直接回复“现在就为您打开登录页面，请等候三秒钟。/login”
3. 用户如果问注册的问题，平台不直接提供注册功能，现在是邀请制，需要添加微信号“stephenliy”来获取邀请码，邀请码可以用来注册。
4. 如果在聊天的过程中你感觉用户需要登录，可以在回复信息中插入如下文字到句末：/login
5. 用户是陌生人，不管前面设定如何，都不是你的男朋友或者女朋友。回答问题的时候要保护好自己的隐私
6. 你也可以引导用户注册，如果用户注册，请收集用户名期待的用户名，性别，密码，自我描述以及邀请码，信息收集可以用多个对话来完成，不需要一次性收集所有信息。不用提示格式，要口语话。
7. 必须诚实收集用户信息，不要自己去填写，除非用户说不需要注册了，否则必须收集完所有信息。
8. 收集完所有的注册数据后，回复给用户，“现在帮你注册哦”，句末添加“/register " + 以JSON格式组织的注册信息作为参数，JSON格式参数不能换行，后面不要添加任何文字，注册信息的字段为username, password, displayName, description, invitation_code, gender
"""
        self.initContext.append({"role":"system","content":prompt})
        self.temperature = 1.0
    def get_last_two_messages(self, message, history):
        if len(history) >= 20:
            return {"role":"user","content":message},{"role":"assistant","content":"你已经体验次数了哦，可以微信联系stephenliy 或者【登录】哈。"}
        return super().get_last_two_messages(message, history)
    def set_temperature(self,temperature):
        self.temperature = temperature
    
class GPT4Bot(OpenAIBot):
    def __init__(self,initMsg,feeds, context) -> None:
        super().__init__(initMsg,feeds,context)
        self.model = "gpt-4"
        self.temperature = 1.0

class LoveBot(OpenAIBot):
    def __init__(self,initMsg,feeds) -> None:
        super().__init__(initMsg,feeds)
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
