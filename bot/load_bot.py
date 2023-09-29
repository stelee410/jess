from bot.chat import OpenAIBot,ExplorerBot,GPT4Bot,LoveBot,SimpleBot

BotsMapping = {
    'OpenAIBot': OpenAIBot,
    'ExplorerBot': ExplorerBot,
    'GPT4Bot': GPT4Bot,
    'LoveBot': LoveBot,
    'SimpleBot':SimpleBot
}

def get_bots_list():
    return [
        ('OpenAIBot', '基础'),
         ('GPT4Bot', 'GPT4'),
        ('ExplorerBot', '首页引导员'),
        ('LoveBot', '爱情脑'),
        ('SimpleBot','测试')
    ]

def load_bot(bot_name, description, messages, caller_id, context):
    return BotsMapping[bot_name](description, messages, caller_id, context)

def load_bot_by_profile(profile, caller_id, context={}):
    context = {**context,**{"profile":profile}}
    return BotsMapping[profile.bot](profile.description, profile.message, caller_id, context)
