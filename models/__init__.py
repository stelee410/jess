import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

SCOPE_PUBLIC = 0
SCOPE_PRIVATE = 1

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(80), nullable=False)
    name = sa.Column(sa.String(80), nullable=False)
    message = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False)

    def __repr__(self):
        return '<ChatHistory %r>' % self.name

class Profile(Base):
    __tablename__ = 'profile'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), nullable=False)
    displayName = sa.Column(sa.String(100), nullable=False)
    avatar = sa.Column(sa.String(100), nullable=False)
    bot = sa.Column(sa.String(100), nullable=False)
    short_description = sa.Column(sa.Text, nullable=True)
    description = sa.Column(sa.Text, nullable=False)
    message = sa.Column(sa.Text, nullable=False)
    offline = sa.Column(sa.Integer, nullable=False)
    deleted = sa.Column(sa.Integer, nullable=False)
    owned_by = sa.Column(sa.String(100), nullable=False)
    scope = sa.Column(sa.Integer, nullable=False)

class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(100), nullable=False)
    displayName = sa.Column(sa.String(100), nullable=False)
    password = sa.Column(sa.String(100), nullable=False)
    avatar = sa.Column(sa.String(100), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    invitation_code = sa.Column(sa.String(100), nullable=True)
    invitation_count = sa.Column(sa.Integer, nullable=False)

class User_Profile_Rel(Base):
    __tablename__ = 'user_profile_rel'
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(100), nullable=False)
    profile_name = sa.Column(sa.String(100), nullable=False)
    last_chat_at = sa.Column(sa.DateTime, nullable=False)
    number_of_chats = sa.Column(sa.Integer, nullable=False)
    relations = sa.Column(sa.Integer, nullable=False)  #0: stranger, 1: friends, 2: close friends

class Balance(Base):
    __tablename__ = 'balance'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))
    balance = sa.Column(sa.Integer, default=0)
    created_by = sa.Column(sa.Integer, sa.ForeignKey("user.id"))
    created_at = sa.Column(sa.DateTime, default=sa.func.now())
    created_with =  sa.Column(sa.String(128))

class Message(Base):
    __tablename__ = 'message'
    STATUS_UNREAD = 0
    STATUS_READ = 1
    STATUS_DELETED = 2
    STATUS_ARCHIVED = 3
    
    id = sa.Column(sa.Integer, primary_key=True)
    receiver = sa.Column(sa.String(100), nullable=False)#username for receiver
    sender = sa.Column(sa.String(100), nullable=False)#username for sender
    title = sa.Column(sa.String(100), nullable=False)
    message = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime, default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, default=sa.func.now())
    status = sa.Column(sa.Integer, nullable=False, default=0)#0:unread,1:read,2:deleted,3:archived

class SharingLink(Base):
    __tablename__ = 'sharing_link'
    STATUS_ACTIVE = 0
    STATUS_INACTIVE = 1
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(100), nullable=False)
    profile_name = sa.Column(sa.String(100), nullable=False)
    extra_description = sa.Column(sa.String(100), nullable=False)
    link = sa.Column(sa.String(200), nullable=False)
    status = sa.Column(sa.Integer, nullable=False)#0:active, 1:inactive
    created_at = sa.Column(sa.DateTime, default=sa.func.now())

    