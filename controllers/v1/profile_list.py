from .__inner__ import api
from context import *
from utils.config import base_url

def build_profile(name,displayName,avatar,description):
    return {
        'name': name,
        'displayName': displayName,
        'avatar': avatar,
        'description': description
    }

#TODO: 最近聊天列表
@api.route('recent-chat') 
def recent_chat():
    username = session['username']
    if not username:
        return {
            'code':401,
            'message':'user is not login'
        }
    profiles_list = profile_repo.get_recent_profile_list(session.get('username'))
    return [{
        'name':profile.name,
        'displayName':profile.displayName,
        'avatar':f'{base_url}static/{profile.avatar}',
        'description':profile.short_description
    }for profile in profiles_list]

#TODO: 推荐聊天列表
@api.route('recommend-chat') 
def recommend_chat():
    profiles_list = profile_repo.get_profile_list()
    return [{
        'name':profile.name,
        'displayName':profile.displayName,
        'avatar':f'{base_url}static/{profile.avatar}',
        'description':profile.short_description
    }for profile in profiles_list]
