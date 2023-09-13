from .base import Base
from forms import ChatForm
from utils.model_repos import ProfileRepo
from bot.chat import ExplorerBot


class Explorer(Base):
    def execute(self):
        profile_name = self.context['profile_name']
        profile_repo = ProfileRepo(self.context['engine'])
        form = ChatForm()
        history = []
        rank = 0
        profile = profile_repo.get_profile_by_name(profile_name)
        avatar = '/images/default.png'
        session = self.get_session()

        bot = ExplorerBot(profile.description, profile.message)

        if form.validate_on_submit():
            history = session.get('history', [])
            content = form.content.data
            my_msg,assistant_msg = bot.get_last_two_messages(content, history)
            if assistant_msg['content'].find("【登录】") != -1:
                rank = 100
                assistant_msg['content'].replace("【登录】","")
            history.append(my_msg)
            history.append(assistant_msg)
            session['history'] = history
            form.content.data = ''

        else:
            session['history'] =[]

        return self.render('explorer.html', form=form, \
                           history=history,\
                            history_len=len(history), rank=rank, \
                            profile = profile, current_user_avatar = avatar)