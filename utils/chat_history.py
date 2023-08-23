from flask import session
import json

HISTORY_KEY = 'profile_history'
CURRENT_KEY = 'current_profile'

def reset_all_history():    
    session[HISTORY_KEY]  = {}

def get_profile_history():
    current_profile = session[CURRENT_KEY]
    if HISTORY_KEY in session:
        profile_history = session[HISTORY_KEY]
    else:
        profile_history = {current_profile['name']:[]} # {name:[history]}
        session[HISTORY_KEY] = profile_history
    if current_profile['name'] not in profile_history:
        session[HISTORY_KEY][current_profile['name']] =  []
    return session[HISTORY_KEY][current_profile['name']]

def save_profile_history(history):
    current_profile = session[CURRENT_KEY]
    profile_history = session[HISTORY_KEY]
    profile_history[current_profile['name']] =  history
    session[HISTORY_KEY] = profile_history
    
def reset_profile_history():
    save_profile_history([])

def rebuild_history(history):
    new_history = []
    for item in history:
        content_string = item['content']
        try:
            json_object = json.loads(content_string)
            content_string = json_object['content']
        except json.JSONDecodeError:
            pass
        if item['role'] == 'user':
            new_history.append({"role":"user","content":content_string})
        else:
            new_history.append({"role":"assistant","content":content_string})
    return new_history