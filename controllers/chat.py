from .base import Base
from utils.model_repos import UserRepo,ProfileRepo,UserProfileRelRepo,PROFILE_SCOPE_PRIVATE,ChatHistoryRepo
from forms import ChatForm
from context import *
from utils import simple_login_required
from bot.load_bot import if_support_memory
import services.chat as chat_service
import services.message as message_service
from services import long_term_momory_service as ltm_service

@app.route('/reset/<name>', methods=['GET'])
@simple_login_required
def reset(name):
    return Chat().reset_chat_history(name)

@app.route('/reset-save/<name>', methods=['GET'])
@simple_login_required
def reset_save(name):
    return Chat().reset_chat_history(name, True)

@app.route('/reset-memory/<name>', methods=['GET'])
@simple_login_required
def reset_memory(name):
    return Chat().reset_memory(name)

@app.route('/share/<name>', methods=['GET'])
@simple_login_required
def share(name):
    return Chat().share(name)

@app.route('/chat/<name>', methods=['GET'])
@simple_login_required
def chat(name):
    chat = Chat()
    return chat.execute(name)

class Chat(Base):
    def share(self, name):
        from_ = session.get('username')
        profile = profile_repo.get_profile_by_name(name)
        to_ = profile.owned_by
        message = chat_service.format_out_chat_history(from_, to_, name)
        message_service.send(from_, to_, "你有分享的聊天记录", message)
        return self.redirect(f"/chat/{name}")

    def reset_chat_history(self, name, save_flag=False):
        username = session.get('username')
        profile_name = name
        if save_flag:
            message = chat_service.save_and_format_out_chat_history(username, username, name,True)
        else:
            message = chat_service.format_out_chat_history(username, username, name,False)
        message_service.send(username, username, "你有保存的聊天记录", message)
        chat_history_repo.reset_chat_history(username, profile_name)
        return self.redirect(f"/chat/{name}")
    
    def reset_memory(self, name):
        username = session.get('username')
        profile_name = name
        ltm_service.clear_longterm_memroy(username, profile_name)
        self.reset_chat_history(name)
        return {"message":"success"}

    def execute(self,name):
        username = session.get('username')
        avatar = session.get('avatar')
        profile = profile_repo.get_profile_by_name(name)
        if profile is None:
            return self.render("404.html", message=f"Profile {name} not found")
        if profile.scope == PROFILE_SCOPE_PRIVATE and profile.owned_by != username:
            return self.render("500.html", message=f"Profile {name} not owned by {username}")

        user_profile_rel =  user_profile_rel_repo.get_user_profile_rel(username, profile.name)
    
        #udpate user_profile_rel
        if user_profile_rel is None:
            user_profile_rel_repo.add_user_profile_rel(username, profile.name)
        else:
            user_profile_rel_repo.quick_update(username, profile.name)

        history = chat_history_repo.get_chat_history_by_name(username, name)
        support_memory = if_support_memory(profile.bot)
        form = ChatForm()
        return self.render('new_chat.html', form=form, \
                           history=history,\
                            history_len=len(history), rank=0, \
                            profile = profile, current_user_avatar = avatar, support_memory=support_memory)