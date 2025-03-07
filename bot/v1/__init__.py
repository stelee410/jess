from .base import BaseBot
from .chat_gpt import ChatGPTBot
from .chat_gpt_ltm import ChatGPTLTM

BotsMapping = {
    'base': BaseBot,
    'chatgpt': ChatGPTBot,
    'chatgpt_ltm': ChatGPTLTM,
}

def get_bots_list():
    return [
        ('base', '基础'),
        ('chatgpt', 'ChatGPT'),
        ('chatgpt_ltm', 'ChatGPTLTM'),
    ]

def get_bot_klass(bot_name):
    if not bot_name in BotsMapping:
        bot_name = 'base'
    return BotsMapping[bot_name]

