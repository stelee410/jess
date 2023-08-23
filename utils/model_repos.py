import json
import datetime
from models import ChatHistory
from sqlalchemy.orm import Session
from sqlalchemy import select,delete


def rebuild_history(history):
    new_history = []
    for item in history:
        content_string = item['content']
        try:
            json_object = json.loads(content_string)
            content_string = json_object['content']
        except json.JSONDecodeError:
            pass
        if item['role'] == 'user':
            new_history.append({"role":"user","content":content_string})
        else:
            new_history.append({"role":"assistant","content":content_string})
    return new_history

class ChatHistoryRepo():
    def __init__(self,engine,username) -> None:
        self.engine = engine
        self.username = username

    def get_chat_history_by_name(self,name):
        session = Session(self.engine)
        stmt = select(ChatHistory).where(ChatHistory.username == self.username).where(ChatHistory.name == name)
        chat_history = []
        if session.execute(stmt).scalars().first() is None:
            return chat_history
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