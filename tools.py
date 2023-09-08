
from utils import config, model_repos, password_hash
from sqlalchemy import create_engine

def create_user():
    username = input("Enter your name: ")
    password = input("Enter your password: ")
    display_name = input("Enter your display name: ")
    avatar = "images/default.png"
    password_hashed = password_hash.get_password_hash(password, config.secret_key)
    engine = create_engine(config.connection_str)
    user_repo = model_repos.UserRepo(engine)
    user = user_repo.get_user_by_username(username)
    if user is None:
        user_repo.insert_user(username, display_name, password_hashed, avatar)
    else:
        print('user existed')


if __name__ == '__main__':
    action = input("what do you want? create [u]ser?")
    if action == "u":
        create_user()
    else:
        print("invalid action")