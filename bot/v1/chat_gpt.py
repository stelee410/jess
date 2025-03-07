from .base import BaseBot

class ChatGPTBot(BaseBot):
    def __get_model(self):
        return "gpt-4o-mini"
        
