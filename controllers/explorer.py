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
import random


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

        bot = ExplorerBot(profile.description, profile.message,0)
        action = ''
        params = ''
        if form.validate_on_submit():
            history = session.get('history', [])
            content = form.content.data
            my_msg,assistant_msg = bot.get_last_two_messages(content, history)
            content = assistant_msg['content']
            arg = ""
            showAds = False
            if content.find("/login") != -1:
                action = 'login'
                params = ''
                assistant_msg['content'] = content.replace("/login","")
            elif content.find("/register") != -1:
                action = 'register'
                params = ''
                assistant_msg['content'] = content.replace("/register","")

            history.append(my_msg)
            history.append(assistant_msg)
            session['history'] = history
            form.content.data = ''

        else:
            showAds = True
            session['history'] =[]
            prompt = f"""
你好，我是你的引导员，你可以通过跟我对话了解这个平台，试试问问怎么注册或者怎么登录吧～
    """
            history = [{"role":"assistant","content":prompt}]

        return self.render('explorer.html', form=form, \
                           history=history,show_ads = showAds,\
                            history_len=len(history), action=action, params=params,\
                            profile = profile, current_user_avatar = avatar)