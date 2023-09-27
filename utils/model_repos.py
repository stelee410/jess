import json
import datetime
from models import ChatHistory, Profile,User,User_Profile_Rel,Balance
from models import SCOPE_PRIVATE,SCOPE_PUBLIC
from sqlalchemy.orm import Session
from sqlalchemy import select,delete,update,and_, func
from sqlalchemy.orm import outerjoin
import logging

PROFILE_SCOPE_PUBLIC = SCOPE_PUBLIC
PROFILE_SCOPE_PRIVATE = SCOPE_PRIVATE

def rebuild_history(history):
    return history
    # new_history = []
    # for item in history:
    #     content_string = item['content']
    #     try:
    #         json_object = json.loads(content_string)
    #         content_string = json_object['content']
    #     except json.JSONDecodeError:
    #         pass
    #     if item['role'] == 'user':
    #         new_history.append({"role":"user","content":content_string})
    #     else:
    #         new_history.append({"role":"assistant","content":content_string})
    # return new_history

class ChatHistoryRepo():
    def __init__(self,engine,username) -> None:
        self.engine = engine
        self.username = username

    def get_chat_history_by_name(self,name):
        session = Session(self.engine)
        stmt = select(ChatHistory).where(ChatHistory.username == self.username).where(ChatHistory.name == name)
        chat_history = []
        for chat in  session.execute(stmt).scalars():
            chat_history.append(json.loads(chat.message))
        return chat_history
    
    def insert_message_to_chat_history(self, name, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        else:
            message = str(message)
        chatHistory = ChatHistory(username=self.username, name=name, message=str(message), created_at=datetime.datetime.now())
        session = Session(self.engine)
        session.add(chatHistory)
        session.commit()

    def reset_chat_history(self, name):
        session = Session(self.engine)
        stmt = delete(ChatHistory).where(ChatHistory.username == self.username).where(ChatHistory.name == name)
        session.execute(stmt)
        session.commit()
    def reset_all_chat_history(self):
        session = Session(self.engine)
        stmt = delete(ChatHistory).where(ChatHistory.username == self.username)
        session.execute(stmt)
        session.commit()

class UserRepo():
    def __init__(self,engine) -> None:
        self.engine = engine
    def insert_user(self,username,displayName,password,avatar,description=""):
        session = Session(self.engine)
        user = User(username=username, displayName=displayName, password=password, avatar=avatar, description=description, invitation_code="N/A", invitation_count=0)
        session.add(user)
        session.commit()
    def get_user_by_username_password(self,username,password):
        session = Session(self.engine)
        stmt = select(User).where(User.username==username).where(User.password==password)
        return session.execute(stmt).scalars().first()
    def get_user_by_username(self, username):
        session = Session(self.engine)
        stmt = select(User).where(User.username==username)
        return session.execute(stmt).scalars().first()
    def check_invitation_code_resuable(self, username,invitation_code):
        session = Session(self.engine)
        stmt = select(User).where(User.invitation_code == invitation_code).where(User.username!=username)
        if session.execute(stmt).scalars().first() is None:
            return True
        else:
            return False
        
    def update_user(self, username, data):
        session = Session(self.engine)
        stmt = update(User).where(User.username == username).values(displayName=data['displayName'], avatar=data['avatar'], description=data['description'])
        session.execute(stmt)
        session.commit()
    def update_password(self, username, password_hashed, new_password_hashed):
        session = Session(self.engine)
        stmt = update(User).where(User.username == username).where(User.password==password_hashed).values(password=new_password_hashed)
        session.execute(stmt)
        session.commit()
    def update_invitation(self, username, invitation_code, invitation_count):
        session = Session(self.engine)
        stmt = update(User).where(User.username == username).values(invitation_code=invitation_code, invitation_count=invitation_count)
        session.execute(stmt)
        session.commit()
    def get_invitation_status(self, invitation_code):
        session = Session(self.engine)
        stmt = select(User).where(User.invitation_code==invitation_code)
        result = session.execute(stmt).scalars().first()
        if result is not None:
            return result.invitation_code, result.invitation_count
        else:
            return 'N/A', 0
    def is_invitation_code_available(self,invitation_code):
        session = Session(self.engine)
        stmt = (select(User).where(User.invitation_code==invitation_code)
                .where(User.invitation_count>0))
        if session.execute(stmt).scalars().first() is None:
            return False
        else:
            return True

    def decrease_invitation_count(self, invitation_code):
        __, count = self.get_invitation_status(invitation_code)
        if count > 0 :
            session = Session(self.engine)
            stmt = update(User).where(User.invitation_code == invitation_code).values(invitation_count = count-1)
            session.execute(stmt)
            session.commit()

class ProfileRepo():
    def __init__(self,engine) -> None:
        self.engine = engine
    def get_profile_by_name(self,name):
        session = Session(self.engine)
        stmt = select(Profile).where(Profile.name==name).where(Profile.deleted==0)
        return session.execute(stmt).scalars().first()
    def get_profile_list(self):
        session = Session(self.engine)
        stmt = select(Profile).where(Profile.deleted==0).where(Profile.scope==SCOPE_PUBLIC)
        result = session.execute(stmt).scalars().all()
        return result
    def get_profile_private_list(self, owner):
        session = Session(self.engine)
        stmt = select(Profile).where(Profile.deleted==0).where(Profile.scope==SCOPE_PRIVATE).where(Profile.owned_by==owner)
        result = session.execute(stmt).scalars().all()
        return result
        
    def get_ordered_profile_list(self, username):
        session = Session(self.engine)
        query = (
            session.query(Profile)
            .outerjoin(User_Profile_Rel,and_(Profile.name==User_Profile_Rel.profile_name,User_Profile_Rel.username==username))
            .filter(Profile.deleted==0)
            .filter(Profile.scope==SCOPE_PUBLIC)
            .order_by(User_Profile_Rel.last_chat_at.desc())
        )
        print(query.statement)
        return query.all()
    
    def get_ordered_profile_private_list(self, owner):
        session = Session(self.engine)
        query = (
            session.query(Profile)
            .outerjoin(User_Profile_Rel,and_(Profile.name==User_Profile_Rel.profile_name,User_Profile_Rel.username==owner))
            .filter(Profile.deleted==0)
            .filter(Profile.scope==SCOPE_PRIVATE)
            .filter(Profile.owned_by==owner)
            .order_by(User_Profile_Rel.last_chat_at.desc())
        )
        return query.all()
    
    def update_profile(self, name,data):
        session = Session(self.engine)
        if 'name' in data: #omit the update of the name field
            del data['name']
        stmt = update(Profile).where(Profile.name == name).values(**data)
        session.execute(stmt)
        session.commit()
    
    def add(self, data, owner):
        session = Session(self.engine)
        existing_profile = self.get_profile_by_name(data['name'])
        if existing_profile is not None:
            logging.warn(f"profile {data['name']} exists!")
        else:
            profile = Profile(name=data['name'], displayName=data['displayName'], avatar=data['avatar'], bot='SimpleBot', short_description = data["short_description"] ,description="", message="", owned_by=owner, deleted=0, offline=0, scope = PROFILE_SCOPE_PRIVATE)
            session.add(profile)
            session.commit()

    def set_profile_offline(self, name):
        session = Session(self.engine)
        stmt = update(Profile).where(Profile.name == name).values(offline=1)
        session.execute(stmt)
        session.commit()

    def set_profile_online(self, name):
        session = Session(self.engine)
        stmt = update(Profile).where(Profile.name == name).values(offline=0)
        session.execute(stmt)
        session.commit()

    def delete_profile(self,name):
        session = Session(self.engine)
        stmt = update(Profile).where(Profile.name == name).values(deleted=1)
        session.execute(stmt)
        session.commit()

    def transfer_profile(self, name, from_username, to_username):
        session = Session(self.engine)
        stmt = update(Profile).where(Profile.name==name).where(Profile.owned_by == from_username).values(owned_by=to_username)
        session.execute(stmt)
        session.commit()
    
    def set_profile_scope(self, name, scope):
        session = Session(self.engine)
        stmt = update(Profile).where(Profile.name==name).values(scope=scope)
        session.execute(stmt)
        session.commit()

class UserProfileRelRepo():
    def __init__(self,engine) -> None:
        self.engine = engine
    def get_user_profile_rel(self,username,profile_name):
        session = Session(self.engine)
        stmt = select(User_Profile_Rel).where(User_Profile_Rel.username==username).where(User_Profile_Rel.profile_name==profile_name)
        return session.execute(stmt).scalars().first()
    def add_user_profile_rel(self,username, profilename):
        session = Session(self.engine)
        user_profile_rel = User_Profile_Rel(username=username, profile_name=profilename, last_chat_at=datetime.datetime.now(), number_of_chats=0, relations=0)
        session.add(user_profile_rel)
        session.commit()

    def quick_update(self, username, profilename):
        session = Session(self.engine)
        stmt = update(User_Profile_Rel).where(User_Profile_Rel.username == username).where(User_Profile_Rel.profile_name == profilename).values(number_of_chats=User_Profile_Rel.number_of_chats+1,last_chat_at=datetime.datetime.now())
        session.execute(stmt)
        session.commit()

    def update_user_porfile_rel(self,username, profilename, data):
        if 'username' in data:
            del data['username']
        if 'profile_name' in data:
            del data['profile_name']
        logging.warning("data contains username and profile_name, wnich should not be updated")
        session = Session(self.engine)
        stmt = update(User_Profile_Rel).where(User_Profile_Rel.username == username).where(User_Profile_Rel.profile_name == profilename).values(**data)
        session.execute(stmt)
        session.commit()
    def update_user_profile_rel_count(self,username, profilename):
        session = Session(self.engine)
        stmt = update(User_Profile_Rel).where(User_Profile_Rel.username == username).where(User_Profile_Rel.profile_name == profilename).values(number_of_chats=User_Profile_Rel.number_of_chats+1)
        session.execute(stmt)
        session.commit()
    def update_user_profile_rel_last_chat_at(self,username, profilename):
        session = Session(self.engine)
        stmt = update(User_Profile_Rel).where(User_Profile_Rel.username == username).where(User_Profile_Rel.profile_name == profilename).values(last_chat_at=datetime.datetime.now())
        session.execute(stmt)
        session.commit()
class BalanceRepo():
    def __init__(self,engine) -> None:
        self.engine = engine
    def get_balance_by_user_id(self,user_id):
        session = Session(self.engine)
        stmt = select([func.sum(Balance.balance)]).where(Balance.user_id==user_id)
        result = session.execute(stmt).scalars().first()
        print(stmt.compile(self.engine))
        if result is None:
            return 0
        return result
    def update_balance_by_user_id(self,user_id,amount, created_by, created_with):
        session = Session(self.engine)
        record = Balance(user_id=user_id,\
                              balance=amount,\
                                created_by=created_by,\
                                created_with=created_with,\
                                created_at=datetime.datetime.now())
        session.add(record)
        session.commit()
