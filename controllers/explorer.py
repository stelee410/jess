from .base import Base
from forms import ChatForm
from utils.model_repos import ProfileRepo
from bot.chat import ExplorerBot
from bot.agent import Agent
from utils.model_repos import UserRepo
from utils.password_hash import get_password_hash
import re
import json
import logging


class Explorer(Base):
    def execute(self):
        profile_name = self.context['profile_name']
        profile_repo = ProfileRepo(self.context['engine'])
        user_repo = UserRepo(self.context['engine'])
        form = ChatForm()
        history = []
        profile = profile_repo.get_profile_by_name(profile_name)
        avatar = '/images/default.png'
        session = self.get_session()

        bot = ExplorerBot(profile.description, profile.message)
        action = ''
        params = ''

        if form.validate_on_submit():
            history = session.get('history', [])
            content = form.content.data
            my_msg,assistant_msg = bot.get_last_two_messages(content, history)
            content = assistant_msg['content']
            arg = ""
            if content.find("/login") != -1:
                action = 'login'
                params = ''
                assistant_msg['content'] = content.replace("/login","")
            elif content.find("/register") != -1:
                try:
                    # pattern = r'/register\s+(?P<arg>{.*?})'
                    # match = re.search(pattern, content)
                    # arg = match.group('arg')
                    agent=Agent("register",['username','password','nickname','invitation_code'])
                    arg = agent.getResponse(history+[my_msg,assistant_msg])
                    user_register_info = json.loads(arg)
                    username = user_register_info.get('username')
                    password = user_register_info.get('password')
                    display_name = user_register_info.get('nickname')
                    invitation_code = user_register_info.get('invitation_code')
                    logging.info("Start to register for new user " + username)
                    if user_repo.is_invitation_code_available(invitation_code) is False:
                        assistant_msg['content'] = "邀请码错误。"
                    elif user_repo.get_user_by_username(username) is not None:
                        assistant_msg['content'] = "用户名已经存在。"
                    else:
                        password_hashed = get_password_hash(password, self.context['app'].secret_key)
                        user_repo.insert_user(username, display_name, password_hashed, avatar)
                        user_repo.decrease_invitation_count(invitation_code)
                        assistant_msg['content'] = "注册成功了，现在可以登录了。登录进去后别忘了在设置页面设置自己的头像，修改自己的资料。如果忘记密码，请添加'stephenliy'微信找客服。"
                except Exception as error:
                    logging.warning(error)
                    logging.warning(arg)
                    assistant_msg['content'] = "注册失败了，请重新输入注册试试。"

            history.append(my_msg)
            history.append(assistant_msg)
            session['history'] = history
            form.content.data = ''

        else:
            session['history'] =[]
            prompt = f"""
你好，我是你的引导员，你可以通过跟我对话了解这个平台，试试问问怎么注册或者怎么登录吧～
    """
            history = [{"role":"assistant","content":prompt}]

        return self.render('explorer.html', form=form, \
                           history=history,\
                            history_len=len(history), action=action, params=params,\
                            profile = profile, current_user_avatar = avatar)