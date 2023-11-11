from .base import Base
from forms import ChatForm
from bot.chat import ExplorerBot
from context import *
from utils import config

@app.route('/explore', methods=['GET','POST'])
def explore():
    explorer =  Explorer()
    try:
        profile_name = config.guider_profile_name
    except:
        profile_name = 'pixie'
    return explorer.execute(profile_name)


class Explorer(Base):
    def execute(self, profile_name):
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
            my_msg,assistant_msg = bot.get_last_two_messages(content, [{**c,**{"saved_flag":0}} for c in history])
            content = assistant_msg['content']
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
        self.flash("灵芸网站将迎来从页面到功能的重大更新，届时也将正式上线，敬请期待！")
        return self.render('explorer.html', form=form, \
                           history=history,show_ads = showAds,\
                            history_len=len(history), action=action, params=params,\
                            profile = profile, current_user_avatar = avatar)