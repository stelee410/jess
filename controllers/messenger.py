from .base import Base
import utils.model_repos as model_repos

def getListNoneToEmpty(list):
    if list is None:
        return []
    else:
        return list

class Messenger(Base):

    def mark_read(self):
        engine = self.context.get('engine')
        username = self.session_get('username')
        if username is None:
            return self.redirect('/login')
        message_repo = model_repos.MessageRepo(engine)
        message_id = self.context.get('id')
        message_repo.mark_read(message_id)
        return self.redirect('/messages/all')

    def mark_delete(self):
        engine = self.context.get('engine')
        username = self.session_get('username')
        if username is None:
            return self.redirect('/login')
        message_repo = model_repos.MessageRepo(engine)
        message_id = self.context.get('id')
        message_repo.mark_delete(message_id)
        return self.redirect('/messages/all')
    
    def mark_archive(self):
        engine = self.context.get('engine')
        username = self.session_get('username')
        if username is None:
            return self.redirect('/login')
        message_repo = model_repos.MessageRepo(engine)
        message_id = self.context.get('id')
        message_repo.mark_archive(message_id)
        return self.redirect('/messages/archived')

    def show_message(self):
        engine = self.context.get('engine')
        username = self.session_get('username')
        if username is None:
            return self.redirect('/login')
        message_repo = model_repos.MessageRepo(engine)
        message_id = self.context.get('id')
        message = message_repo.get_message_by_id(message_id)
        if message is None:
            return self.redirect('/messages')
        if message.status == 0:
            message_repo.mark_read(message_id)
        unread_messages = getListNoneToEmpty(message_repo.get_unread_message_list(username))
        return self.render('message_content.html',unread_messages_num=len(unread_messages),message=message)
    
    def execute(self):
        engine = self.context.get('engine')
        username = self.session_get('username')
        if username is None:
            return self.redirect('/login')
        message_repo = model_repos.MessageRepo(engine)
        unread_messages = getListNoneToEmpty(message_repo.get_unread_message_list(username))
        messages = []
        action = self.context.get('scope')
        if action == 'archived':
            messages = message_repo.get_archived_message_list(username)
        elif action == 'all':
            messages = message_repo.get_message_list(username)
        else:
            messages =  message_repo.get_unread_message_list(username)
        messages = getListNoneToEmpty(messages)
        return self.render('message_list.html',unread_messages_num=len(unread_messages),messages=messages)