# -*- coding: utf-8 -*-
from enum import Enum
from flask import Flask, render_template, request, flash, redirect, url_for, session,abort
from markupsafe import Markup
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import DataRequired, Length, Regexp
from wtforms.fields import *
from flask_bootstrap import Bootstrap5
import time
from datetime import datetime
from bot.chat import InSufficientBalanceException
from bot.load_bot import load_bot, load_bot_by_profile
from utils.model_repos import ChatHistoryRepo,rebuild_history,ProfileRepo,UserRepo, UserProfileRelRepo,BalanceRepo,PROFILE_SCOPE_PUBLIC, PROFILE_SCOPE_PRIVATE
from utils.password_hash import get_password_hash
from sqlalchemy import create_engine
from flask_wtf.file import FileRequired, FileAllowed, FileField
from werkzeug.utils import secure_filename
from functools import wraps
from utils import config

from controllers import Explorer,Register,ProfileEditor

from flask_restful import Api, Resource

import os
import logging
import json

app = Flask(__name__)
api = Api(app)
app.secret_key = config.secret_key
engine = create_engine(config.connection_str,pool_size=1024, max_overflow=0)
profile_repo = ProfileRepo(engine)
user_repo = UserRepo(engine)
balance_repo = BalanceRepo(engine)


bootstrap = Bootstrap5(app)

csrf = CSRFProtect(app)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
logging.basicConfig(level=logging.INFO)

def simple_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None:
            return redirect("/explore")
        return f(*args, **kwargs)
    return decorated_function

context = {
    "app": app,
    "engine": engine,
    "profile_repo": profile_repo,
}

class UserForm(FlaskForm):
    displayName = StringField(label="昵称", validators=[DataRequired(), Length(1, 20)])
    avatar = FileField(label="头像", validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    description = TextAreaField(label="描述", validators=[Length(0, 2048)], render_kw={"rows":"10"})
    password = PasswordField(label="旧密码", validators=[Length(0, 20)])
    password_new = PasswordField(label="新密码", validators=[Length(0, 20)])
    password_new_confirm = PasswordField(label="确认密码", validators=[Length(0, 20)])
    submit = SubmitField('保存',render_kw={"class":'single-btn',"style":'margin-left:0px'})
    

class ChatForm(FlaskForm):
    content = TextAreaField(label="", render_kw={"class":"form-control type_msg"})
    submit = SubmitField('发送')

class TransferForm(FlaskForm):
    username = StringField(label="对方用户名", validators=[DataRequired(), Length(1, 10)])
    submit = SubmitField('发送')

class DeleteForm(FlaskForm):
    username = StringField(label='请输入“我确认删除这个数字人”', validators=[DataRequired(), Length(1, 10)])
    submit = SubmitField('发送')

class LoginForm(FlaskForm):
    username = StringField(label="用户名", validators=[DataRequired(), Length(1, 20)])
    password = PasswordField(label="密码", validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField('登录')

class ProfileForm(FlaskForm):
    name = StringField(label="唯一数字人ID", validators=[DataRequired(), Length(1, 20)])
    displayName = StringField(label="姓名", validators=[DataRequired(), Length(1, 20)])
    avatar = FileField(label="头像", validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    short_description = TextAreaField(label="描述（不影响设定）", validators=[Length(0, 2048)], render_kw={"rows":"8"})

class ProfileUpdateForm(FlaskForm):
    displayName = StringField(label="昵称", validators=[DataRequired(), Length(1, 20)])
    avatar = FileField(label="头像", validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    short_description = TextAreaField(label="描述（不影响设定）", validators=[Length(0, 2048)], render_kw={"rows":"8"})


@app.route('/', methods=['GET'])
@simple_login_required
def index():
    username = session.get('username')
    profile_list = profile_repo.get_ordered_profile_list(username)
    profile_private_list = profile_repo.get_ordered_profile_private_list(username)
    user = user_repo.get_user_by_username(username)
    balance = balance_repo.get_balance_by_user_id(user.id)
    userDisplayName = session.get('displayName')
    if userDisplayName is None or userDisplayName == "":
        userDisplayName = username
    return render_template('index.html', profiles = profile_list,profiles_private=profile_private_list,\
                           userDisplayName = userDisplayName,balance=balance)

@app.route('/explore', methods=['GET','POST'])
def explore():
    explorer =  Explorer({**context, **{"profile_name": "pixie"}})
    return explorer.execute()

@app.route('/register/<invitation_code>', methods=['GET','POST'])
def register(invitation_code):
    register = Register({**context, **{"invitation_code": invitation_code}})
    return register.execute()

@app.route('/register', methods=['GET','POST'])
def register_no_invite():
    register = Register({**context, **{"invitation_code": ""}})
    return register.execute()

@app.route('/reset/<name>', methods=['GET'])
@simple_login_required
def reset(name):
    repo = ChatHistoryRepo(engine,session.get('username'))
    repo.reset_chat_history(name)
    return redirect(f"/chat/{name}")

@app.route('/chat/<name>', methods=['GET','POST'])
@simple_login_required
def chat(name):
    username = session.get('username')
    avatar = session.get('avatar')
    user = user_repo.get_user_by_username(username)

    profile = profile_repo.get_profile_by_name(name)
    if profile is None:
        return render_template("404.html", message=f"Profile {name} not found")
    if profile.scope == PROFILE_SCOPE_PRIVATE and profile.owned_by != username:
        return render_template("500.html", message=f"Profile {name} not owned by {username}")

    uprRepo = UserProfileRelRepo(engine)
    user_profile_rel =  uprRepo.get_user_profile_rel(username, profile.name)
    
    #udpate user_profile_rel
    if user_profile_rel is None:
        uprRepo.add_user_profile_rel(username, profile.name)
    else:
        uprRepo.quick_update(username, profile.name)
    botContext = {"username":username,"displayName":session.get("displayName")}

    bot = load_bot_by_profile(profile,user.id, botContext)
    repo = ChatHistoryRepo(engine,username)
    history = repo.get_chat_history_by_name(name)
    rank = 0 #TODO: this is going to update to meta data or prompt agent.
    form = ChatForm()
    if form.validate_on_submit():
        content = form.content.data
        try:
            user_message, response = bot.chat(content, history)
        except InSufficientBalanceException as e:
            flash("余额不足，请充值")
            return redirect(f"/chat/{name}")
        repo.insert_message_to_chat_history(name, user_message)
        repo.insert_message_to_chat_history(name, response)
        history.append(user_message)
        history.append(response)
        form.content.data = ''
    return render_template('chat.html', form=form, \
                           history=rebuild_history(history),\
                            history_len=len(history), rank=rank, \
                            profile = profile, current_user_avatar = avatar)

@app.route('/profile/<name>', methods=['GET','POST'])
@simple_login_required
def profile(name):
    form = ProfileUpdateForm()
    profile = profile_repo.get_profile_by_name(name)
    if profile is None:
        return render_template("404.html", message=f"Profile {name} not found")
    if profile.owned_by != session.get('username'):
        return render_template("500.html", message=f"Profile {name} not owned by {session.get('username')}")
    if form.validate_on_submit():
        data = form.data
        data_to_update={}
        if form.avatar.data:
            file = form.avatar.data
            filename = secure_filename(file.filename)
            current_timestamp = int(time.time())
            filename = f"{current_timestamp}_{filename}"
            if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                file.save(os.path.join('./static/profiles', filename))
                data_to_update['avatar'] = f"profiles/{filename}"
        else:
            data_to_update['avatar'] = profile.avatar
        data_to_update['displayName'] = data['displayName']
        data_to_update['short_description'] = data['short_description']
        profile_repo.update_profile(name, data_to_update)
    else:
        form.displayName.data = profile.displayName
        form.short_description.data = profile.short_description
    return render_template("profile.html", name=name, form=form, profile=profile)

@app.route('/profile/<name>/advanced_edit', methods=['GET','POST'])
@simple_login_required
def profile_advanced_edit(name):
    profileEditor = ProfileEditor({**context, **{"profile_name": name}})
    return profileEditor.execute()

@app.route('/profile/:create', methods=['GET','POST'])
@simple_login_required
def new_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        profile = profile_repo.get_profile_by_name(form.name.data)
        if profile is not None:
            flash('用户已存在')
            return render_template("new_profile.html", form=form)
        data = form.data
        if form.avatar.data:
            file = form.avatar.data
            filename = secure_filename(file.filename)
            current_timestamp = int(time.time())
            filename = f"{current_timestamp}_{filename}"
            if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                file.save(os.path.join('./static/profiles', filename))
                data['avatar'] = f"profiles/{filename}"
        profile_repo.add(data,session.get('username'))
        return redirect("/profile/"+data['name'])
    return render_template("new_profile.html", form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password_hash = get_password_hash(form.password.data,app.secret_key)
        print(password_hash)
        user = UserRepo(engine).get_user_by_username_password(username, password_hash)
        if user is None:
            flash('用户名或密码错误')
            form.password.data = ""
            return render_template("login.html", form=form)
        else:
            session['username'] = username
            session['displayName'] = user.displayName
            session['avatar'] = user.avatar
            return redirect("/")
    return render_template("login.html", form=form)

@app.route('/logout', methods=['GET'])
@simple_login_required
def logout():
    session['username'] = None
    session['displayName'] = None
    session['avatar'] = None
    return redirect("/login")

@app.route('/profile/<name>/offline', methods=['GET'])
@simple_login_required
def offline(name):
    profile = profile_repo.get_profile_by_name(name)
    if profile.owned_by != session.get('username'):
        return render_template("500.html", message=f"Profile {name} not owned by {session.get('username')}")
    profile_repo.set_profile_offline(name)
    return redirect(f"/profile/{name}")

@app.route('/profile/<name>/online', methods=['GET'])
@simple_login_required
def online(name):
    profile = profile_repo.get_profile_by_name(name)
    if profile.owned_by != session.get('username'):
        return render_template("500.html", message=f"Profile {name} not owned by {session.get('username')}")
    profile_repo.set_profile_online(name)
    return redirect(f"/profile/{name}")

@app.route('/profile/<name>/transfer', methods=['GET','POST'])
@simple_login_required
def transfer(name):
    form = TransferForm()
    profile = profile_repo.get_profile_by_name(name)
    if profile is None:
        return render_template("404.html", message=f"Profile {name} not found")
    if profile.owned_by != session.get('username'):
        return render_template("500.html", message=f"Profile {name} not owned by {session.get('username')}")
    if form.validate_on_submit():
        profile_repo.transfer_profile(name,session.get('username'),form.username.data)
        return redirect("/")
    return render_template("transfer.html", form=form)

@app.route('/profile/<name>/delete', methods=['GET','POST'])
@simple_login_required
def delete(name):
    form = DeleteForm()
    profile = profile_repo.get_profile_by_name(name)
    if profile is None:
        return render_template("404.html", message=f"Profile {name} not found")
    if profile.owned_by != session.get('username'):
        return render_template("500.html", message=f"Profile {name} not owned by {session.get('username')}")
    if form.validate_on_submit():
        if form.username.data == "我确认删除这个数字人":
            profile_repo.delete_profile(name)
            return redirect("/")
        else:
            flash('输入错误')
    return render_template("delete.html", form=form)

@app.route('/profile/<name>/:scope/<scope_str>', methods=['GET','POST'])
@simple_login_required
def set_profile_scope(name, scope_str):
    if scope_str == 'public':
        scope = PROFILE_SCOPE_PUBLIC
    else:
        scope = PROFILE_SCOPE_PRIVATE
    profile = profile_repo.get_profile_by_name(name)
    if profile.owned_by != session.get('username'):
        return render_template("500.html", message=f"Profile {name} not owned by {session.get('username')}")
    profile_repo.set_profile_scope(name,scope)
    return redirect(f"/profile/{name}")

@app.route('/my', methods=['GET','POST'])
@simple_login_required
def my():
    username = session.get('username')
    user = UserRepo(engine).get_user_by_username(username)
    session['avatar'] = user.avatar
    session['displayName'] = user.displayName

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
        UserRepo(engine).update_user(username, data)

        if form.password_new.data:
            password_hashed = get_password_hash(form.password.data,app.secret_key)
            new_password_hashed = get_password_hash(form.password_new.data,app.secret_key)
            if user.password != password_hashed:
                flash('旧密码错误')
                return render_template('my.html', form = form)
            if form.password_new.data != form.password_new_confirm.data:
                flash('两次输入的密码不一致')
                return render_template('my.html', form = form)
            UserRepo(engine).update_password(username,password_hashed,new_password_hashed)

        return redirect("/my")
    else:
        form.displayName.data = user.displayName
        form.description.data = user.description
    return render_template('my.html', form = form)


@app.route('/api/chatdev', methods=['POST'])
@csrf.exempt
@simple_login_required
def chatdev():
    description = request.form.get('description')
    bot = request.form.get('bot')
    var_str = request.form.get('var_str')
    profile_name = request.form.get('profile_name')
    profile = profile_repo.get_profile_by_name(profile_name)
    context = {}
    username = session.get('username')
    user = user_repo.get_user_by_username(username)
    try:
        context = json.loads(var_str)
    except:
        logging.warning("var string cannot be parsed")
    try:
        profile = profile_repo.get_profile_by_name(profile_name)
        if profile is None:
            return abort(404, message=f"Profile {profile_name} not found")
        if profile.owned_by != session.get('username'):
            return abort(500, message=f"Profile {profile_name} not owned by {session.get('username')}")
    
        chat_data = request.form.get('chat_data')
        chatbot = load_bot(bot, description, chat_data, user.id, context)
        message = chatbot.getResponse()
        return {'message':message}
    except Exception as e:
        logging.error(e)
        abort (400, e.args)

@app.route('/api/savechatdev', methods=['POST'])
@csrf.exempt
@simple_login_required
def save_chatdev():
    description = request.form.get('description')
    bot = request.form.get('bot')
    chat_data = request.form.get('chat_data')
    profile_name = request.form.get('profile_name')
    try:
        profile = profile_repo.get_profile_by_name(profile_name)
        if profile is None:
            return abort(404, message=f"Profile {profile_name} not found")
        if profile.owned_by != session.get('username'):
            return abort(500, message=f"Profile {profile_name} not owned by {session.get('username')}")
        data = {
            'bot': bot,
            'description':description,
            'message':'!#v2\n'+chat_data
        }
        profile_repo.update_profile(profile_name,data)
        return {'message':'success'}
    except Exception as e:
        logging.error(e)
        abort (400, e.args)
if __name__ == '__main__':
    app.run(debug=True, port=8080)