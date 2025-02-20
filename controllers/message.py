from .base import Base
from context import *
from utils import simple_login_required


@app.route('/messages', methods=['GET'])
@simple_login_required
def message():
    return MessageController().execute(session.get('username'), 'unread')

@app.route('/messages/<scope>', methods=['GET'])
@simple_login_required
def message_with_scope(scope):
    return MessageController().execute(session.get('username'), scope)

@app.route('/message/<id>', methods=['GET'])
@simple_login_required
def show_message(id):
    return MessageController().show_message(session.get('username'), id)

@app.route('/message/<id>/archive', methods=['GET'])
@simple_login_required
def mark_archive(id):
    return MessageController().mark_archive(session.get('username'), id)

@app.route('/message/<id>/read', methods=['GET'])
@simple_login_required
def mark_read(id):
    return MessageController().mark_read(session.get('username'), id)

@app.route('/message/<id>/delete', methods=['GET'])
@simple_login_required
def mark_delete(id):
    return MessageController().mark_delete(session.get('username'), id)

def getListNoneToEmpty(list):
    if list is None:
        return []
    else:
        return list

class MessageController(Base):
    def mark_read(self, username, message_id):
        if username is None:
            return self.redirect('/login')
        message_repo.mark_read(message_id)
        return self.redirect('/legacy/messages/all')
    
    def mark_delete(self, username, message_id):
        if username is None:
            return self.redirect('/login')
        message_repo.mark_delete(message_id)
        return self.redirect('/legacy/messages/all')
    
    def mark_archive(self, username, message_id):
        if username is None:
            return self.redirect('/login')
        message_repo.mark_archive(message_id)
        return self.redirect('/legacy/messages/archived')

    def show_message(self,username, message_id):
        if username is None:
            return self.redirect('/login')
        message = message_repo.get_message_by_id_reciever(message_id,username)
        line_data = []
        if message is None:
            return self.redirect('/legacy/messages')
        else:
            line_data = message.message.splitlines()
        if message.status == 0:
            message_repo.mark_read(message_id)
        unread_messages = getListNoneToEmpty(message_repo.get_unread_message_list(username))
        return self.render('message_content.html',unread_messages_num=len(unread_messages),message=message, line_data=line_data)
    
    def execute(self, username, scope):
        if username is None:
            return self.redirect('/login')
        unread_messages = getListNoneToEmpty(message_repo.get_unread_message_list(username))
        messages = []
        if scope == 'archived':
            messages = message_repo.get_archived_message_list(username)
        elif scope == 'all':
            messages = message_repo.get_message_list(username)
        else:
            messages =  message_repo.get_unread_message_list(username)
        messages = getListNoneToEmpty(messages)
        return self.render('message_list.html',unread_messages_num=len(unread_messages),messages=messages)