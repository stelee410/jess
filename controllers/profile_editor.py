from .base import Base
import re

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
        user_display_name = self.session_get('displayName')
        user_avatar = self.session_get('avatar')
        if profile is None:
            return self.render("404.html", message=f"Profile {profile_name} not found")
        if profile.owned_by != self.session_get('username'):
            return self.render("500.html", message=f"Profile {profile_name} not owned by {self.session_get('username')}")
        model_list = ['OpenAIBot','ExplorerBot','GPT4Bot','LoveBot']
        return self.render('advanced_editor.html',profile=profile,
                           history = get_history(profile.message.splitlines()),
                           user_display_name = user_display_name,
                           user_avatar=user_avatar,
                            model_list=model_list)