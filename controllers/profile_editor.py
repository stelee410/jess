from .base import Base
from bot.load_bot import get_bots_list
import re
import json
from context import *
from utils import simple_login_required

def detect_jinja_tags(s):
    pattern = r'{%.*?%}'
    return bool(re.search(pattern, s))

def get_history(feeds):
    history = []
    role = "user"
    for feed in feeds:
        if detect_jinja_tags(feed):
            history.append({"role":"code","content":feed})
        else:
            history.append({"role":role,"content":feed})
            if role == "user":
                role = 'assistant'
            else:
                role = 'user'
    return history

@app.route('/profile/<name>/advanced_edit', methods=['GET'])
@simple_login_required
def profile_advanced_edit(name):
    return  ProfileEditor().execute(name)

class ProfileEditor(Base):
    def execute(self, profile_name):
        profile = profile_repo.get_profile_by_name(profile_name)
        user_name = self.session_get('username')
        user_display_name = self.session_get('displayName')
        user_avatar = self.session_get('avatar')
        if profile is None:
            return self.render("404.html", message=f"Profile {profile_name} not found")
        if profile.owned_by != self.session_get('username'):
            return self.render("500.html", message=f"Profile {profile_name} not owned by {self.session_get('username')}")
        model_list = get_bots_list()
        message = profile.message
        if message is None:
            message = ""
        history = []
        if message.startswith("!#v2\n"):
            feeds = message[5:]
            feeds = feeds.split("\n")
            for feed in feeds:
                feed = feed.strip()
                if feed=="":
                    continue
                if feed.endswith(','):
                    feed = feed.strip(',')
                try:
                    history.append(json.loads(feed))
                except:
                    history.append({"role":"code","content":feed})             
        else:
            history = get_history(message.splitlines())
        return self.render('advanced_editor.html',profile=profile,
                           history = history,
                           user_name = user_name,
                           user_display_name = user_display_name,
                           user_avatar=user_avatar,
                            model_list=model_list)