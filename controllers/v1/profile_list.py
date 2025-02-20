from .__inner__ import api
from context import *
from utils.config import base_url
from utils import simple_login_required


SCOPE_PUBLIC = 0
SCOPE_PRIVATE = 1

def build_profile(name,displayName,avatar,description):
    return {
        'name': name,
        'displayName': displayName,
        'avatar': avatar,
        'description': description
    }


@api.route('profile/<profileName>') 
@simple_login_required
def fetchProfile(profileName):
    profile = profile_repo.get_profile_by_name(profileName)
    if profile is None:
        return {
            'code':404,
            'message':'profile not found'
        }
    if profile.scope == SCOPE_PRIVATE and profile.owned_by != session.get('username'):
        return {
            'code':403,
            'message':'profile is private'
        }
    
    return {
        'name': profile.name,
        'displayName': profile.displayName,
        'avatar': f'{base_url}static/{profile.avatar}',
        'description': profile.short_description,
    }

@api.route('recent-chat') 
@simple_login_required
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
        'description':profile.short_description,
        'lastchatTimestamp':last_chat_at
    }for profile,last_chat_at in profiles_list]

@api.route('recommend-chat') 
@simple_login_required
def recommend_chat():
    profiles_list = profile_repo.get_profile_list()
    return [{
        'name':profile.name,
        'displayName':profile.displayName,
        'avatar':f'{base_url}static/{profile.avatar}',
        'description':profile.short_description
    }for profile in profiles_list]

@api.route('private-chat') 
@simple_login_required
def private_chat():
    profiles_list = profile_repo.get_profile_private_list(session.get('username'))
    return [{
        'name':profile.name,
        'displayName':profile.displayName,
        'avatar':f'{base_url}static/{profile.avatar}',
        'description':profile.short_description
    }for profile in profiles_list]
