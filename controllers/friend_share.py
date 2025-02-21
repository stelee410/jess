from .base import Base
from context import *
from utils import simple_login_required
from services.friend_sharing import generate_link_and_qr_code_for_friend_sharing
from services.chat import get_msg_body
from services.message import send
from utils.config import base_url
from bot.load_bot import load_bot
from bot.chat import InSufficientBalanceException
import logging

@app.route('/friend/<profile_name>', methods=['GET'])
@simple_login_required
def set_friend_share(profile_name):
    return FriendShareController().set_friend_share(profile_name)

@app.route('/friend/chat/<link>', methods=['GET'])
#@simple_login_required no login required!
@csrf.exempt
def friend(link):
    return FriendShareController().start_chat(link)

@app.route('/friend/reset_chat', methods=['GET'])
def reset_chat():
    session['chat_history'] = []
    return {'message':'success'}
@app.route('/friend/api/chat', methods=['POST'])
@csrf.exempt
def do_chat():
    return FriendShareController().do_chat()

@app.route('/friend/api/share/<link>', methods=['GET'])
def do_share(link):
    return FriendShareController().share(link)

@app.route('/friend/api/generate_link', methods=['POST'])
@simple_login_required
@csrf.exempt
def generate_link():
    return FriendShareController().generate_link()


class FriendShareController(Base):
   def share(self, link):
        share_link = sharing_link_repo.get_sharing_link(link)
        if share_link is None:
            return self.render("404.html", message=f"Link {link} not found")
        username = share_link.username
        profile_name = share_link.profile_name
        user = user_repo.get_user_by_username(username)
        profile = profile_repo.get_profile_by_name(profile_name)
        history = session.get('chat_history')
        msg_body = get_msg_body(user, profile, history)
        send("你的好友", user.username, "你有新的好友分享的聊天记录", msg_body)
        return {'message':'success'}
   def do_chat(self):
        link = request.form.get('link')
        content = request.form.get('content')
        share_link = sharing_link_repo.get_sharing_link(link)
        user = user_repo.get_user_by_username(share_link.username)
        profile = profile_repo.get_profile_by_name(share_link.profile_name)
        description = profile.description + '\n如果我的称呼和性别，需要先提问了解我的称呼和性别。\n' + share_link.extra_description
        bot = load_bot(profile.bot, description, profile.message, user.id, {"profile":profile,'from_friend':True})
        history = session.get('chat_history')
        try:
            bot.disabled_longterm_memory()
            user_input, response = bot.chat(content, [{**c,**{"saved_flag":0}} for c in history])
            history.append(user_input)
            history.append(response)
            session['chat_history'] = history
            return {'message':response}
        except InSufficientBalanceException as e:
            logging.warning(f'balance of {user.username} is not enough')
            self.abort(400,"balance is not enough")
        except Exception as e:
            logging.warning(f'error in chat {e}')
            self.abort(500,str(e))


   def start_chat(self, link):
        share_link = sharing_link_repo.get_sharing_link(link)
        if share_link is None:
            return self.render("404.html", message=f"Link {link} not found")
        if link!=session.get('link'):
            session['chat_history'] = []
        session['link'] = link

        username = share_link.username
        profile_name = share_link.profile_name
        user = user_repo.get_user_by_username(username)
        profile = profile_repo.get_profile_by_name(profile_name)
        histroy = session.get('chat_history')
        if histroy is None:
                histroy = []
        session['chat_history']=histroy

        return self.render("friend_chat.html", link=link, user=user, profile=profile,history=histroy)
   
   def set_friend_share(self, profile_name):
       username = session.get('username')
       existing_link = sharing_link_repo.get_sharing_link_by_username_profile_name(username, profile_name)
       return self.render("set_friend_share.html", profile_name=profile_name, existing_link=existing_link, base_url=base_url)
   def generate_link(self):
       username = session.get('username')
       profile_name = request.form.get('profile_name')
       extra_description = request.form.get('message')
       link = generate_link_and_qr_code_for_friend_sharing(username, profile_name, extra_description)
       return {"link":link,"share_url":f"{base_url}legacy/friend/chat/{link}"}