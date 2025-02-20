from context import *
from utils import simple_login_required
from .__inner__ import api

@api.route('has-new-mail', endpoint='v1_mail', methods=['GET'])
@simple_login_required
def hasNewMail():
    message_list = message_repo.get_unread_message_list(session.get('username'))
    if len(message_list) > 0:
        return {
            'has_unread_message': True,
            'unread_message_num': len(message_list)
        }
    else:
        return {
            'has_unread_message': False,
            'unread_message_num': 0
        }
