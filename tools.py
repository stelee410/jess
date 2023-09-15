
from utils import config, model_repos, password_hash
from sqlalchemy import create_engine

engine = create_engine(config.connection_str)

def create_user():
    username = input("Enter your name: ")
    password = input("Enter your password: ")
    display_name = input("Enter your display name: ")
    avatar = "images/default.png"
    password_hashed = password_hash.get_password_hash(password, config.secret_key)
    user_repo = model_repos.UserRepo(engine)
    user = user_repo.get_user_by_username(username)
    if user is None:
        user_repo.insert_user(username, display_name, password_hashed, avatar)
    else:
        print('user existed')
def create_invitation_code():
    user_repo = model_repos.UserRepo(engine)
    username = input("Enter your name: ")
    user = user_repo.get_user_by_username(username)
    if user is None:
        print("user not found")
        return
    invitation_code = input("Enter your invitation code: ")
    if user_repo.check_invitation_code_resuable(username, invitation_code) is False:
        print("invitation code not reusable")
        return
    count = input("Enter your invitation count: ")
    count = int(count)
    user_repo.update_invitation(username, invitation_code, count)
    print('invitation code updated')
    

if __name__ == '__main__':
    while True:
        action = input("what do you want? create [u]ser | create [i]nvitation code |[q]uit: ")
        if action == "u":
            create_user()
        elif action == "i":
            create_invitation_code()
        elif action == "q":
            break
        else:
            print("invalid action")