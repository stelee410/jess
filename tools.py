
from utils import config, model_repos, password_hash
from sqlalchemy import create_engine
import random
from services import message as message_service
from services import chat as chat_service
from services import long_term_momory_service as ltm_service

from context import *

import os
import json

engine = create_engine(config.connection_str)

def forward_chat_history(admin):
    inbox = input("Enter the msg inbox: ")
    from_ = input("Enter the sender username: ")
    profile_name = input("Enter the profile name: ")
    profile = model_repos.ProfileRepo(engine).get_profile_by_name(profile_name)
    owner_username = profile.owned_by
    message = chat_service.format_out_chat_history(from_, owner_username, profile_name,False)
    message_service.send(admin.username, inbox, "你有分享的聊天记录", message)
    print("chat history forwarded")


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
    message_service.send(admin.username, user.username, title, message)
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

def _restruct(c,user_display_name,profile_display_name):
  if c.startswith(user_display_name+":"):
    return {'role':'user','content':c[len(user_display_name)+1:]}
  else:
    return {'role':'assistant','content':c[len(profile_display_name)+1:]}

def build_memory_for_user():
    username = input("Enter the user name: ")
    profilename = input("Enter the profile name: ")
    user = user_repo.get_user_by_username(username)
    profile = profile_repo.get_profile_by_name(profilename)
    #the memory will be built from message once.
    messages = message_repo.get_message_list(username)
    for message in messages:
        title = message.title
        content = message.message
        if title == '你有保存的聊天记录' and content.find(f"亲爱的数字人 {profile.displayName}({profile.name}) 用户") >= 0:
            content = content[content.find("-----")+8:]
            chat = content.split('\n\n')
            chat_list =[_restruct(c,user.displayName,profile.displayName) for c in chat if c!=""]
            print("save long term memory...")
            try:
                if chat_list != []:
                    ltm_service.save_longterm_memory(username, profilename, chat_list)
            except Exception as e:
                print("save long term memory...failed")
                print(e)
                continue
            print("save long term memory...done")
def build_memory_from_folder():
    folder_name = input("Enter the folder path: ")
    jsonp_file_names = [filename for filename in os.listdir(folder_name) if filename.endswith('.jsonp')]
    for jsonp_file_name in jsonp_file_names:
        print(f"processing {jsonp_file_name}")
        username, profilename = jsonp_file_name.split('--')[0].split('-')
        blob_path = os.path.join(folder_name, jsonp_file_name)
        chat_list = []
        if os.path.exists(blob_path):
            with open(blob_path, 'rb') as f:
                print("save long term memory...start")
                ltm_service.save_longterm_memory(username, profilename, [json.loads(line) for line in f.readlines()])
                print("save long term memory...done")
    print('job finished')


    

if __name__ == '__main__':
    admin_username = input("Enter your admin name: ")
    user_repo = model_repos.UserRepo(engine)
    admin = user_repo.get_user_by_username(admin_username)
    if admin is None:
        print("user not found")
        exit()
    while True:
        print("what do you want?")
        print("create [u]ser | create [i]nvitation code |[r]eset password | [b]uild memory for a user |build memory from f[o]lder")
        print("[c]harge | [s]end message | [f]foward the chat history | [q]uit")
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
        elif action == 'f':
            forward_chat_history(admin)
        elif action == 'b':
            build_memory_for_user()
        elif action == 'o':
            build_memory_from_folder()
        else:
            print("invalid action")