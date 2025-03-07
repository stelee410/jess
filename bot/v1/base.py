import jinja2
import json
from context import balance_repo
from utils import tokenizer
from services import llm
from services import long_term_momory_service

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

    
class BaseBot():
    __support_long_term_memory__ = False
    def __init__(self,initMsg,feeds, user_id, context ={}, username = None, profilename = None) -> None: #context is the context of the conversation
        feeds, version = auto_detect_version2(feeds)
        initMsg = render_string(initMsg, **context)
        feeds = render_string(feeds, **context)
        if self._get_pre_context() != "":
            initMsg = self._get_pre_context()+"\n"+initMsg
        self.initContext=[{"role":"system","content":initMsg}]
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
        self.username = username
        self.profilename = profilename
        self.support_long_term_memory = self.__class__.__support_long_term_memory__

    def disabled_longterm_memory(self):
        self.support_long_term_memory = False

    def _get_model(self):
        return "gpt-3.5-turbo-16k"
    
    def _get_temperature(self):
        return 0.8
    
    def _get_pre_context(self):
        return ""
    
    def buildMemory(self, message):
        if message=="":
            return self.initContext
        if self.username is not None and self.profilename is not None:
            long_term_memory = long_term_momory_service.get_longterm_memory(self.username, self.profilename,message)
            return self.initContext+long_term_memory

    def get_max_token_num_hard(self):
        return 4096
    def get_max_token_num_soft(self):
        return 1500

    def getResponse(self,message="", history=[]):
        raw_history = [c for c in history if c['saved_flag']==0]
        history = [ {'role':c['role'], 'content':c['content']} for c in raw_history]
        if self.support_long_term_memory:
            input_message = ""
            for n in history[-3:]:
                input_message += n["content"]+"\n"
            input_message += message
            initContext = self.buildMemory(input_message)
        else:
            initContext = self.initContext
        if message!="":
            history.append({"role":"user","content":message})

        messages = initContext+history
        
        if self.support_long_term_memory:
            token_num = tokenizer.num_tokens_from_messages(messages)
            if token_num > self.get_max_token_num_hard():
                print("token number too large:",token_num)
                token_consumed = 0
                stage_history=[]
                for chat in reversed(raw_history):
                    token_consumed += tokenizer.num_tokens_from_messages([chat])
                    if token_consumed>self.get_max_token_num_soft():
                        datetime_to_ltm_trans = chat['created_at']
                        print("datetime_to_ltm_trans",datetime_to_ltm_trans)
                        long_term_momory_service.save_longterm_memory_by_datetime(self.username, self.profilename,datetime_to_ltm_trans)
                        print("save long term memory...")
                        messages = self.buildMemory(input_message)+[{"role":c["role"],"content":c["content"]} for c in reversed(stage_history)]
                        break
                    else:
                        stage_history.append(chat)

        #check balance and decrease the balance
        if self.user_id !=0: #bypass the check for user_id=0
            if check_balance_of(self.user_id) is False:
                print("balance is not enough")
                raise InSufficientBalanceException("balance is not enough")
            decrease_balance_of(self.user_id, 1)
        response = llm.create(model=self.model,messages=messages,temperature=self.temperature)
        if "AI" in response.choices[0].message["content"]:
            response = self.remove_AI(response, messages)
        return response.choices[0].message

    def chat(self,message, history):
        local_history=history.copy()
        response= self.getResponse(message, local_history)
        return {"role":"user","content":message},response
    
    def get_last_two_messages(self,message, history):
        return self.chat(message, history)
    def remove_AI(self, response, messages):
        print("Trying to remove AI")
        messages = messages+[{"role":"system","content":"任何情况下都不要提及自己是AI，并记住游戏开始设定的身份"}]
        response = llm.create(model=self.model,messages=messages,temperature=self.temperature)