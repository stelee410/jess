from context import engine
from utils import  model_repos
import logging

def send(from_user, to_user, title, message):
    message_repo = model_repos.MessageRepo(engine)
    user_repo = model_repos.UserRepo(engine)
    #from_user can be any user, but to_user must be an existing user
    user = user_repo.get_user_by_username(to_user)
    if user is None:
        logging.warning(f'trying to send the message, but user {to_user} not found')
        return False
    message_repo.insert_message(from_user, to_user, title, message)
    return True