from .v1 import *
from .v1 import get_bots_list as v1_get_bots_list

def if_support_memory(botname):
    bot_klass = get_bot_klass(botname)
    return bot_klass.__support_long_term_memory__

def get_bots_list():
    return v1_get_bots_list()

def load_bot(bot_name, description, messages, caller_id, context, username=None, profilename=None):
    bot_klass = get_bot_klass(bot_name)
    return bot_klass(description, messages, caller_id,context, username, profilename)

def load_bot_by_profile(profile, caller_id, context={}, username=None):
    context = {**context,**{"profile":profile}}
    bot_klass = get_bot_klass(profile.bot)
    return bot_klass(profile.description, profile.message, caller_id, context, username, profile.name)
