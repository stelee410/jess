from .base import Base
from utils.model_repos import UserRepo,ProfileRepo,UserProfileRelRepo,PROFILE_SCOPE_PRIVATE,ChatHistoryRepo
from flask import abort
from bot.load_bot import load_bot, load_bot_by_profile
from bot.chat import InSufficientBalanceException
import logging

class NewChat(Base):
    def execute(self):
        engine = self.context.get("engine")
        profile_repp = ProfileRepo(engine)
        user_repp = UserRepo(engine)
        form = self.context.get("form")

        content = form.get("content")
        profile_name = form.get("profile_name")
        username = self.session_get("username")

        profile = profile_repp.get_profile_by_name(profile_name)
        user = user_repp.get_user_by_username(username)

        if profile is None:
            abort(404, f"Profile {profile_name} not found")
        if profile.owned_by != username and profile.scope == PROFILE_SCOPE_PRIVATE:
            abort(500, f"Profile {profile_name} not owned by {username}")
        
        botContext = {"username":username,"displayName":user.displayName}

        bot = load_bot_by_profile(profile,user.id, botContext)
        history_repo = ChatHistoryRepo(engine,username)
        history = history_repo.get_chat_history_by_name(profile_name)
        try:
            user_message, assist_message = bot.chat(content, history)
            history_repo.insert_message_to_chat_history(profile_name, user_message)
            history_repo.insert_message_to_chat_history(profile_name, assist_message)
            return {"message":assist_message}
        except InSufficientBalanceException as e:
            abort(400,"balance is not enough")
        
