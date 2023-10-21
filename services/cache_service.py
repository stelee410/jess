from utils.config import cache_uri
from context import cache
import os
import json


#so far the cache is used to serve the chat memory
#the format will be JSONP

def reset_cache():
    cache = {}

def reset_blob(key, on_fly = True):
    if on_fly is False:
        blob_path = os.path.join(cache_uri, key)
        if os.path.exists(blob_path):
            os.remove(blob_path)
    if key in  cache:
        del cache[key]

def get_blob_by_key(key):
    ret = cache.get(key)
    if ret is None:
        #try to load from blob
        blob_path = os.path.join(cache_uri, key)
        if os.path.exists(blob_path):
            with open(blob_path, 'rb') as f:
                ret = f.read()
                cache[key] = ret
        return ret
    else:
        return None


def get_chat_memory(username, profilename):
    key = generate_key_for_chat_memory(username, profilename)
    ret = cache.get(key)
    if ret is None:
        #try to load from blob
        blob_path = os.path.join(cache_uri, key)
        if os.path.exists(blob_path):
            with open(blob_path, 'rb') as f:
                ret =[json.loads(line) for line in f.readlines()]
                cache[key] = ret
 
    return ret
    
def set_chat_memory(username, profilename, json_list):
    key = generate_key_for_chat_memory(username, profilename)
    blob_path = os.path.join(cache_uri, key)
    if os.path.exists(blob_path):
        mode = 'a'
    else:
        mode = 'w'
    with open(blob_path, mode) as f:
        for item in json_list:
            f.write(json.dumps(item))
            f.write("\n")
    reset_blob(key)
    return get_chat_memory(username, profilename)

def generate_key_for_chat_memory(username, profilename):
    return f"{username}-{profilename}--chat_history.jsonp"