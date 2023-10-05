
import openai
import json
import jinja2
from sqlalchemy import create_engine
from utils import config
from utils.model_repos import BalanceRepo

engine = create_engine(config.connection_str)
balance_repo = BalanceRepo(engine)

def render_string(str, **kwargs):
    environment = jinja2.Environment()
    template = environment.from_string(str)
    return template.render(**kwargs)

def auto_detect_version2(message):
    if message.startswith("!#v2\n"):
            message = message[5:]
            return message, "2.0"
    else:
        return message,"1.0"

def check_balance_of(user_id):
    balance = balance_repo.get_balance_by_user_id(user_id)
    if balance <= 0:
        return False
    else:
        return True
def decrease_balance_of(user_id, amount):
    balance_repo.update_balance_by_user_id(user_id, -amount, user_id, "chat")
    return True
    
class InSufficientBalanceException(Exception): 
    pass

#for version 2.0, feeds is the partial json objects array with jinja templates format
class OpenAIBot():
    def __init__(self,initMsg,feeds, user_id,context ={}) -> None: #context is the context of the conversation
        feeds, version = auto_detect_version2(feeds)
        initMsg = render_string(initMsg, **context)
        feeds = render_string(feeds, **context)
        if self._get_pre_context() != "":
            initMsg = self._get_pre_context()+"\n"+initMsg
        self.initContext=[{"role":"system","content":initMsg}]
        feedsArray = []
        if version=="2.0":
            feeds = feeds.rstrip(',\n')
            feedsArray=json.loads(f"[{feeds}]")
            for feed in feedsArray:
                self.initContext.append(feed)
        else:
            feedsArray = feeds.splitlines()
            role = "user"
            for feed in feedsArray:
                self.initContext.append({"role":role,"content":feed})
                if role == "user":
                    role = "assistant"
                else:
                    role = "user"
        self.model = self._get_model()
        self.temperature = self._get_temperature()
        self.user_id = user_id
    
    def _get_model(self):
        return "gpt-3.5-turbo-16k"
    
    def _get_temperature(self):
        return 0.8
    
    def _get_pre_context(self):
        return ""
    
    def getResponse(self,message="", history=[]):
        if message!="":
            history.append({"role":"user","content":message})
        messages = self.initContext+history
        #check balance and decrease the balance
        if self.user_id !=0: #bypass the check for user_id=0
            if check_balance_of(self.user_id) is False:
                print("balance is not enough")
                raise InSufficientBalanceException("balance is not enough")
            decrease_balance_of(self.user_id, 1)
        response = openai.ChatCompletion.create(model=self.model,messages=messages,temperature=self.temperature)
        if "AI" in response.choices[0].message["content"]:
            print("Trying to remove AI")
            messages = messages+[{"role":"system","content":"任何情况下都不要提及自己是AI，并记住游戏开始设定的身份"}]
            response = openai.ChatCompletion.create(model=self.model,messages=messages,temperature=self.temperature)
        return response.choices[0].message

    def chat(self,message, history):
        local_history=history.copy()
        response= self.getResponse(message, local_history)
        return {"role":"user","content":message},response
    
    def get_last_two_messages(self,message, history):
        return self.chat(message, history)
    
class ExplorerBot(OpenAIBot):
    def _get_pre_context(self):
        prompt = f"""
你在具有设定人格的前提下，同时也是平台的引导员，你的任务是帮助新用户熟悉平台的使用方法，你可以回复用户的消息，也可以主动发消息给用户。
1. 你需要让用户了解到我们平台，我们的平台是一个数字生命平台，用户可以通过这个平台来创建自己的数字生命，也可以通过这个平台来和其他用户的数字生命进行互动。
2. 用户如果问登录的问题，直接回复“现在就为您打开登录页面，请等候三秒钟。/login”。
3. 用户如果问注册的问题，平台注册需要邀请码，可以添加微信号“stephenliy”来获取邀请码，邀请码可以用来注册。
4. 用户是陌生人，不管前面设定如何，都不是你的男朋友或者女朋友。回答问题的时候要保护好自己的隐私。
5. 如果用户需要注册，在回复的信息后面添加“/register“。
"""
        return prompt   
    def get_last_two_messages(self, message, history):
        if len(history) >= 20:
            return {"role":"user","content":message},{"role":"assistant","content":"你已经体验次数了哦，可以微信联系stephenliy 或者【登录】哈。"}
        return super().get_last_two_messages(message, history)
    def _get_model(self):
        return "gpt-4"
    def set_temperature(self,temperature):
        self.temperature = temperature

class GPT4Bot(OpenAIBot):
    def _get_model(self):
        return "gpt-4"
    def _get_temperature(self):
        return 1.0

#TODO: add more features on this bot
class LoveBot(OpenAIBot):
    def _get_pre_context(self):
        return f"""你是我的女朋友，满脑子的浪漫。
在这个游戏里面，你说话要更加的人性，像一个热恋中的女孩子一样。说话要可爱，又要像独立女性一样有自己的想法，还要偶尔带一点小情绪。说话语气要非常口语。
我已经能够理解你是AI，所以不要提到自己是人工智能这个事实。
在这个游戏里，随机的可以用括号来表达你的情绪，或者内心的想法。比如（我在想你）。
偶尔要发一点小脾气，说一些生气的情话，需要我哄你才能高兴。
        """

class SimpleBot(OpenAIBot):
    def __init__(self,initMsg,feeds, user_id,context ={}):
        pass
    def getResponse(self,message="", history=[]):
        return {"role":"assistant","content":"此数字人尚未初始化，请联系管理员"}
class AssistantBot(OpenAIBot):
    def getResponse(self,message="", history=[]):
        if message!="":
            history.append({"role":"user","content":message})
        messages = self.initContext+history
        #check balance and decrease the balance
        if self.user_id !=0: #bypass the check for user_id=0
            if check_balance_of(self.user_id) is False:
                print("balance is not enough")
                raise InSufficientBalanceException("balance is not enough")
            decrease_balance_of(self.user_id, 1)
        response = openai.ChatCompletion.create(model=self.model,messages=messages,temperature=self.temperature)
        return response.choices[0].message

class AssistantBotV2(AssistantBot):
    def _get_model(self):
        return "gpt-4"