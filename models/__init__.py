import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

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
    description = sa.Column(sa.Text, nullable=False)
    message = sa.Column(sa.Text, nullable=False)

class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(100), nullable=False)
    displayName = sa.Column(sa.String(100), nullable=False)
    password = sa.Column(sa.String(100), nullable=False)