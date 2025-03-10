from context import engine, user_repo,profile_repo,chat_history_repo,EMBEDDING_MODEL
from utils import  model_repos
from services.long_term_momory_service import *
import logging
import jinja2
import datetime
import openai

def render_string(str, **kwargs):
    environment = jinja2.Environment()
    template = environment.from_string(str)
    return template.render(**kwargs)

def _get_chat_history(from_, from_displayName, profile_name, profile_displayName):
    chat_history_repo = model_repos.ChatHistoryRepo(engine,from_)
    history = chat_history_repo.get_chat_history_by_name(profile_name,True)
    history = history if history is not None else []
    ret = []
    for chat in history:
        role_name = from_displayName
        if chat['role'] == 'assistant':
           role_name = profile_displayName
        ret.append({
            "role_name":role_name,
            "role": chat['role'],
            "content": chat['content'],
            "created_at": chat['created_at'].strftime("%Y-%m-%d %H:%M:%S")})
    return ret

def _get_chat_history_list(username, profilename):
    history = chat_history_repo.get_chat_history_by_name(username, profilename)
    return [{'role':x['role'],'content':x['content']} for x in history]


#from the username who was chatting with the profile, to_ is the owner of the profile
def format_out_chat_history(from_,to_,profile_name,check_owner=True):
    profile = profile_repo.get_profile_by_name(profile_name)
    if profile is None:
        logging.warn(f"Trying to get chat history, but profile {profile_name} not found")
        return "profile not found"
    if check_owner and profile.owned_by != to_:
        logging.warn(f"Profile {profile_name} is not owned by {to_}")
        return "profile not owned by you"
    user = user_repo.get_user_by_username(from_)
    chat_history = _get_chat_history(from_,user.displayName, profile_name, profile.displayName)
    msg = """Dear {{profile_display_name}}({{profile_name}}) user, {{user_display_name}}({{from_}}) wants to share the following chat history with you:
-----

{% for chat in chat_history %}
{{chat.role_name}}: {{chat.content}} ({{chat.created_at}})
{% endfor %}

"""
    return render_string(msg, profile_display_name=profile.displayName,\
                          profile_name=profile.name, \
                            user_display_name=user.displayName, \
                            from_=from_, \
                            chat_history=chat_history)

def save_and_format_out_chat_history(from_,to_,profile_name,check_owner=True):
    chat_history = _get_chat_history_list(from_,profile_name)
    save_longterm_memory(from_,profile_name,chat_history)
    return format_out_chat_history(from_,to_,profile_name,check_owner)

def get_msg_body(user, profile, chat_history=[]):
    msg = """亲爱的数字人 {{profile_display_name}}({{profile_name}}) 用户, 你的朋友想要和你分享TA与数字人的聊天, 以下是他们的聊天记录:

-----

{% for chat in chat_history %}
{{chat.role}}: {{chat.content}}
{% endfor %}

"""
    ret = []
    for chat in chat_history:
        role = "用户"
        if chat['role'] == 'assistant':
           role = profile.displayName
        ret.append({
            "role": role,
            "content": chat['content']})

    return render_string(msg, profile_display_name=profile.displayName,\
                          profile_name=profile.name, \
                            user_display_name=user.displayName, \
                            from_=user.username, \
                            chat_history=ret)