# -*- coding: utf-8 -*-
from enum import Enum
from flask import Flask, render_template, request, flash, redirect, url_for, session
from markupsafe import Markup
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import DataRequired, Length, Regexp
from wtforms.fields import *
from flask_bootstrap import Bootstrap5
import time
from datetime import datetime
from bot.chat import LoveBot, OpenAIBot
from utils.model_repos import ChatHistoryRepo,rebuild_history,ProfileRepo,UserRepo
from utils.password_hash import get_password_hash
from sqlalchemy import create_engine
from flask_wtf.file import FileRequired, FileAllowed, FileField
from werkzeug.utils import secure_filename
from functools import wraps

import os

os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'



app = Flask(__name__)
app.secret_key = 'mysecretsalt'
engine = create_engine("sqlite:///jess.db")
profile_repo = ProfileRepo(engine)


bootstrap = Bootstrap5(app)

csrf = CSRFProtect(app)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def simple_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



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
    username = StringField(label="用户名", validators=[DataRequired(), Length(1, 10)])
    password = PasswordField(label="密码", validators=[DataRequired(), Length(1, 10)])
    submit = SubmitField('登录')

class ProfileForm(FlaskForm):
    name = StringField(label="姓名", validators=[DataRequired(), Length(1, 20)])
    displayName = StringField(label="昵称", validators=[DataRequired(), Length(1, 20)])
    avatar = FileField(label="头像", validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    #avatar = StringField(label="头像", validators=[DataRequired(), Length(1, 20)])
    bot = StringField(label="机器人", validators=[DataRequired(), Length(1, 20)],default='OpenAIBot')
    description = TextAreaField(label="描述", validators=[DataRequired(), Length(1, 2048)], render_kw={"rows":"25"})
    message = TextAreaField(label="消息", validators=[DataRequired()], render_kw={"rows":"30"})

class ProfileUpdateForm(FlaskForm):
    displayName = StringField(label="昵称", validators=[DataRequired(), Length(1, 20)])
    avatar = FileField(label="头像", validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    bot = StringField(label="机器人", validators=[DataRequired(), Length(1, 20)],default='OpenAIBot')
    description = TextAreaField(label="描述", validators=[DataRequired(), Length(1, 2048)], render_kw={"rows":"25"})
    message = TextAreaField(label="消息", validators=[DataRequired()], render_kw={"rows":"30"})

def load_bot(profile):
    if profile.bot == 'LoveBot':
        return LoveBot(profile.description,profile.message)
    else:
        return OpenAIBot(profile.description,profile.message)


@app.route('/', methods=['GET'])
@simple_login_required
def index():
    profile_list = profile_repo.get_profile_list()
    return render_template('index.html', profiles = profile_list,userDisplayName = session.get('displayName'))


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
    profile = profile_repo.get_profile_by_name(name)
    bot = load_bot(profile)
    repo = ChatHistoryRepo(engine,username)
    history = repo.get_chat_history_by_name(name)
    rank = 0 #TODO: this is going to update to meta data or prompt agent.
    form = ChatForm()
    if form.validate_on_submit():
        content = form.content.data
        response,history = bot.chat(content, history)
        for record in history[-2:]:
            repo.insert_message_to_chat_history(name, record)
        if isinstance(response['content'], dict) and 'rank' in response['content']:
            rank = response['content']['rank']
        else:
            rank = 0
        form.content.data = ''
    return render_template('chat.html', form=form, \
                           history=rebuild_history(history),\
                            history_len=len(history), rank=rank, \
                            profile = profile)

@app.route('/profile/<name>', methods=['GET','POST'])
@simple_login_required
def profile(name):
    form = ProfileUpdateForm()
    profile = profile_repo.get_profile_by_name(name)
    if profile is None:
        return render_template("404.html", message=f"Profile {name} not found")
    if form.validate_on_submit():
        data = form.data
        if form.avatar.data:
            file = form.avatar.data
            filename = secure_filename(file.filename)
            if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                file.save(os.path.join('./static/profiles', filename))
                data['avatar'] = f"profiles/{filename}"
        else:
            data['avatar'] = profile.avatar
        data['name'] = name
        profile_repo.add_or_update_profile(data,session.get('username'))
    else:
        form.displayName.data = profile.displayName
        form.bot.data = profile.bot
        form.description.data = profile.description
        form.message.data = profile.message
    return render_template("profile.html", name=name, form=form, profile=profile)

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
            if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                file.save(os.path.join('./static/profiles', filename))
                data['avatar'] = f"profiles/{filename}"
        profile_repo.add_or_update_profile(data,session.get('username'))
        return redirect("/")
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
            return redirect("/")
    return render_template("login.html", form=form)

@app.route('/logout', methods=['GET'])
@simple_login_required
def logout():
    session['username'] = None
    session['displayName'] = None
    return redirect("/login")

@app.route('/profile/<name>/offline', methods=['GET'])
@simple_login_required
def offline(name):
    profile_repo.set_profile_offline(name)
    return redirect(f"/profile/{name}")

@app.route('/profile/<name>/online', methods=['GET'])
@simple_login_required
def online(name):
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

if __name__ == '__main__':
    app.run(debug=True, port=8080)