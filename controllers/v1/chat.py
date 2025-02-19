from context import *
from .__inner__ import *
from utils import simple_login_required
from utils.model_repos import ChatHistoryRepo

@api.route('chat-history/<profileName>') 
@simple_login_required
def chatHistory(profileName):
    username = session['username']
    chat_history_repo = ChatHistoryRepo(engine,username)
    chat_history = chat_history_repo.get_chat_history_by_name(profileName)
    return chat_history
