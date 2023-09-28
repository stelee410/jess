from .base import Base
from utils.model_repos import UserRepo,ProfileRepo,UserProfileRelRepo,PROFILE_SCOPE_PRIVATE,ChatHistoryRepo
from forms import ChatForm

class Chat(Base):
    def execute(self):
        name = self.context.get('profile_name')
        session = self.get_session()
        username = session.get('username')
        engine = self.context.get('engine')
        user_repo = UserRepo(engine)
        profile_repo = ProfileRepo(engine)


        avatar = session.get('avatar')
        user = user_repo.get_user_by_username(username)
        profile = profile_repo.get_profile_by_name(name)
        if profile is None:
            return self.render("404.html", message=f"Profile {name} not found")
        if profile.scope == PROFILE_SCOPE_PRIVATE and profile.owned_by != username:
            return self.render("500.html", message=f"Profile {name} not owned by {username}")

        uprRepo = UserProfileRelRepo(engine)
        user_profile_rel =  uprRepo.get_user_profile_rel(username, profile.name)
    
        #udpate user_profile_rel
        if user_profile_rel is None:
            uprRepo.add_user_profile_rel(username, profile.name)
        else:
            uprRepo.quick_update(username, profile.name)
        botContext = {"username":username,"displayName":session.get("displayName")}

        repo = ChatHistoryRepo(engine,username)
        history = repo.get_chat_history_by_name(name)
        rank = 0 #TODO: this is going to update to meta data or prompt agent.
        form = ChatForm()
        return self.render('new_chat.html', form=form, \
                           history=history,\
                            history_len=len(history), rank=rank, \
                            profile = profile, current_user_avatar = avatar)