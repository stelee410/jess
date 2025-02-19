from context import *
from .__inner__ import *
from utils import simple_login_required
from bot.load_bot import load_bot_by_profile
from utils.model_repos import PROFILE_SCOPE_PRIVATE
from bot.chat import InSufficientBalanceException

@api.route('chat-history/<profileName>') 
@simple_login_required
def chatHistory(profileName):
    username = session['username']
    chat_history = chat_history_repo.get_chat_history_by_name(username,profileName)
    return chat_history

@csrf.exempt
@api.route('chat/<profileName>', methods=['POST'], endpoint='v1_chat')
@simple_login_required
def chat(profileName):
    content = request.json.get("content")
    username = session['username']
    profile = profile_repo.get_profile_by_name(profileName)
    user = user_repo.get_user_by_username(username)
    if profile is None:
        return {
            'success': False,
            'message': f"Profile {profileName} not found"
        },404
    if profile.owned_by != username and profile.scope == PROFILE_SCOPE_PRIVATE:
        return {
            'success': False,
            'message': f"Profile {profileName} not owned by {username}"
        }, 500
        
    botContext = {"username":username,"displayName":user.displayName}

    bot = load_bot_by_profile(profile,user.id, botContext,username)

    history = chat_history_repo.get_chat_history_by_name(username, profileName)
    try:
        user_message, assist_message = bot.chat(content, history)
        chat_history_repo.insert_message_to_chat_history(username, profileName, user_message)
        chat_history_repo.insert_message_to_chat_history(username, profileName, assist_message)
        return assist_message
    except InSufficientBalanceException as e:
        return {
            'success': False,
            'message': "InSufficientBalanceException"
        },400