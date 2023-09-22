from .base import Base
import re
import json

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

class ProfileEditor(Base):
    def execute(self):
        profile_repo = self.context.get('profile_repo')
        profile_name = self.context.get('profile_name')

        profile = profile_repo.get_profile_by_name(profile_name)
        user_name = self.session_get('username')
        user_display_name = self.session_get('displayName')
        user_avatar = self.session_get('avatar')
        if profile is None:
            return self.render("404.html", message=f"Profile {profile_name} not found")
        if profile.owned_by != self.session_get('username'):
            return self.render("500.html", message=f"Profile {profile_name} not owned by {self.session_get('username')}")
        model_list = ['OpenAIBot','ExplorerBot','GPT4Bot','LoveBot']
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