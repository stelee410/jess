
from utils import config, model_repos, password_hash
from sqlalchemy import create_engine
import random

engine = create_engine(config.connection_str)

def send_message(admin):
    user_repo = model_repos.UserRepo(engine)
    message_repo = model_repos.MessageRepo(engine)
    username = input("Enter the receiver username: ")
    user = user_repo.get_user_by_username(username)
    if user is None:
        print("user not found")
        return
    title = input("Enter the title: ")
    message = input("Enter the message: ")
    message_repo.insert_message(admin.username, user.username, title, message)
    print("message sent!")

def charge_user(admin):
    user_repo = model_repos.UserRepo(engine)
    balance_repo = model_repos.BalanceRepo(engine)

    username = input("Enter the name: ")
    user = user_repo.get_user_by_username(username)
    if user is None:
        print("user not found")
        return
    amount = input("Enter the amount: ")
    amount = int(amount)
    if amount != 0:
        created_with = input("Enter the reason for re-charging or charging: ")
        balance_repo.update_balance_by_user_id(user.id, amount, admin.id, created_with)
    amount_total = balance_repo.get_balance_by_user_id(user.id)
    print(f'balance updated, the total balance is {amount_total}')

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
def reset_password():
    username = input("Enter your name: ")
    user_repo = model_repos.UserRepo(engine)
    user = user_repo.get_user_by_username(username)
    if user is None:
        print("user not found")
        return
    else:
        random_number = random.randint(1000000000, 9999999999)
        password = f"{random_number}"
        new_password = input(f"Enter your new password({password}): ")
        if new_password == "":
            new_password = password
        password_hashed = password_hash.get_password_hash(new_password, config.secret_key)
        user_repo.update_password(username, user.password,password_hashed)

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
    admin_username = input("Enter your admin name: ")
    user_repo = model_repos.UserRepo(engine)
    admin = user_repo.get_user_by_username(admin_username)
    if admin is None:
        print("user not found")
        exit()
    while True:
        print("what do you want?")
        print("create [u]ser | create [i]nvitation code |[r]eset password| [c]harge | [s]end message |[q]uit")
        action = input(":")
        if action == "u":
            create_user()
        elif action == "i":
            create_invitation_code()
        elif action == "q":
            break
        elif action == "r":
            reset_password()
        elif action == "c":
            charge_user(admin)
        elif action == 's':
            send_message(admin)
        else:
            print("invalid action")