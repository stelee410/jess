from .base import Base
from context import *
from utils import simple_login_required
from utils.password_hash import get_password_hash
from werkzeug.utils import secure_filename

from forms import LoginForm, UserForm

import os
import time


@app.route('/', methods=['GET'])
@simple_login_required
def index():
    return IndexController().execute()

@app.route('/ping', methods=['GET'])
def ping():
    return IndexController().ping()

@csrf.exempt
@app.route('/api/login', methods=['POST'])
def api_login():
    username = request.json.get('username')
    password = request.json.get('password')
    return IndexController().api_login(username, password)

@app.route('/login', methods=['GET','POST'])
def login():
    return IndexController().login()


@app.route('/api/logout', methods=['GET'])
def logout_():
   return IndexController().logout()

@app.route('/logout', methods=['GET'])
@simple_login_required
def logout():
   return IndexController().logout()

@app.route('/my', methods=['GET','POST'])
@simple_login_required
def my():
    return IndexController().my()

@app.route('/api/is_login', methods=['GET'])
def is_login():
    return IndexController().is_login()

class IndexController(Base):
    def my(self):
        username = session.get('username')
        user = user_repo.get_user_by_username(username)
        set_session_user(user)
        balance = balance_repo.get_balance_by_user_id(user.id)

        form = UserForm()
        if form.validate_on_submit():
            data ={}
            if form.avatar.data:
                file = form.avatar.data
                filename = secure_filename(file.filename)
                current_timestamp = int(time.time())
                filename = f"{current_timestamp}_{filename}"
                if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                    file.save(os.path.join('./static/profiles', filename))
                    data['avatar'] = f"profiles/{filename}"
            else:
                data['avatar'] = user.avatar
            data['displayName'] = form.displayName.data
            data['description'] = form.description.data
            user_repo.update_user(username, data)

            if form.password_new.data:
                password_hashed = get_password_hash(form.password.data,app.secret_key)
                new_password_hashed = get_password_hash(form.password_new.data,app.secret_key)
                if user.password != password_hashed:
                    self.flash('old password is wrong')
                    return self.render('my.html', form = form)
                if form.password_new.data != form.password_new_confirm.data:
                    self.flash('two passwords are not the same')
                    return self.render('my.html', form = form)
                user_repo.update_password(username,password_hashed,new_password_hashed)

            return self.redirect("/legacy/my")
        else:
            form.displayName.data = user.displayName
            form.description.data = user.description
            form.balance.data = balance
        return self.render('my.html', form = form)
    
    def logout(self):
        empty_session_user()
        return self.redirect("/login")
    
    def api_login(self, username, password):
        password_hash = get_password_hash(password,app.secret_key)
        user = user_repo.get_user_by_username_password(username, password_hash)
        if user is None:
            return self.json({
                'success': False,
                'message': 'username or password error'
            })
        else:
            set_session_user(user)
            return self.json({
                'success': True,
                'message': 'login success'
            })
    
    def login(self):
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password_hash = get_password_hash(form.password.data,app.secret_key)
            print(password_hash)
            user = user_repo.get_user_by_username_password(username, password_hash)
            if user is None:
                self.flash('用户名或密码错误')
                form.password.data = ""
                return self.render("login.html", form=form)
            else:
                set_session_user(user)
                return self.redirect("/")
        return self.render("login.html", form=form)
    def ping(self):
        return {"message":"pong"}
    
    def is_login(self):
        if session.get('username') is not None:
            return self.json({
                'is_login': True,
                'username':  session.get('username') 
            })
        else:
            return self.json({
                'is_login': False,
                'username': None
            })
    def execute(self):
        username = session.get('username')
        profile_list = profile_repo.get_ordered_profile_list(username)
        profile_private_list = profile_repo.get_ordered_profile_private_list(username)
        user = user_repo.get_user_by_username(username)
        if balance_repo.has_user_balance_data(user.id) is False:
            #init balance for new user
            balance_repo.update_balance_by_user_id(user.id, config.initial_balance, 1, "init")
        balance = balance_repo.get_balance_by_user_id(user.id)
        userDisplayName = session.get('displayName')
        unread_message_list = message_repo.get_unread_message_list(username)
        has_unread_msg = True
        if unread_message_list is  None or len(unread_message_list) == 0:
            has_unread_msg = False
        if userDisplayName is None or userDisplayName == "":
            userDisplayName = username
        return self.render('index.html', profiles = profile_list,profiles_private=profile_private_list,\
                           userDisplayName = userDisplayName,balance=balance,has_unread_msg = has_unread_msg)
    