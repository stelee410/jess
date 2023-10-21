from .base import Base
from utils.model_repos import UserRepo,ProfileRepo,UserProfileRelRepo,PROFILE_SCOPE_PRIVATE,ChatHistoryRepo
from bot.load_bot import load_bot, load_bot_by_profile
from bot.chat import InSufficientBalanceException
import logging
from context import *
from utils import simple_login_required
import json

@app.route('/api/chat', methods=['POST'])
@csrf.exempt
@simple_login_required
def chat2():
    return NewChat().execute()

@app.route('/api/chatdev', methods=['POST'])
@csrf.exempt
@simple_login_required
def chatdev():
    return NewChat().chatdev()

@app.route('/api/savechatdev', methods=['POST'])
@csrf.exempt
@simple_login_required
def save_chatdev():
    return NewChat().save_chatdev()


class NewChat(Base):
    def save_chatdev(self):
        description = request.form.get('description')
        bot = request.form.get('bot')
        chat_data = request.form.get('chat_data')
        profile_name = request.form.get('profile_name')
        try:
            profile = profile_repo.get_profile_by_name(profile_name)
            if profile is None:
                return self.abort(404, message=f"Profile {profile_name} not found")
            if profile.owned_by != session.get('username'):
                return self.abort(500, message=f"Profile {profile_name} not owned by {session.get('username')}")
            data = {
                'bot': bot,
                'description':description,
                'message':'!#v2\n'+chat_data
            }
            profile_repo.update_profile(profile_name,data)
            return {'message':'success'}
        except Exception as e:
            logging.error(e)
            self.abort (400, e.args)
    def chatdev(self):
        description = request.form.get('description')
        bot = request.form.get('bot')
        var_str = request.form.get('var_str')
        profile_name = request.form.get('profile_name')
        profile = profile_repo.get_profile_by_name(profile_name)
        context = {}
        username = session.get('username')
        user = user_repo.get_user_by_username(username)
        try:
            context = json.loads(var_str)
        except:
            logging.warning("var string cannot be parsed")
        try:
            profile = profile_repo.get_profile_by_name(profile_name)
            if profile is None:
                return self.abort(404, message=f"Profile {profile_name} not found")
            if profile.owned_by != session.get('username'):
                return self.abort(500, message=f"Profile {profile_name} not owned by {session.get('username')}")
        
            chat_data = request.form.get('chat_data')
            chatbot = load_bot(bot, description, chat_data, user.id, context)
            message = chatbot.getResponse()
            return {'message':message}
        except Exception as e:
            logging.error(e)
            self.abort (400, e.args)
            
    def execute(self):
        form = request.form

        content = form.get("content")
        profile_name = form.get("profile_name")
        username = session.get('username')

        profile = profile_repo.get_profile_by_name(profile_name)
        user = user_repo.get_user_by_username(username)

        if profile is None:
            self.abort(404, f"Profile {profile_name} not found")
        if profile.owned_by != username and profile.scope == PROFILE_SCOPE_PRIVATE:
            self.abort(500, f"Profile {profile_name} not owned by {username}")
        
        botContext = {"username":username,"displayName":user.displayName}

        bot = load_bot_by_profile(profile,user.id, botContext,username)
        history_repo = chat_history_repo
        history = history_repo.get_chat_history_by_name(username, profile_name)
        try:
            user_message, assist_message = bot.chat(content, history)
            history_repo.insert_message_to_chat_history(username, profile_name, user_message)
            history_repo.insert_message_to_chat_history(username, profile_name, assist_message)
            return {"message":assist_message}
        except InSufficientBalanceException as e:
            self.abort(400,"balance is not enough")
        
