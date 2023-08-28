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
from utils.model_repos import ChatHistoryRepo,rebuild_history,ProfileRepo
from sqlalchemy import create_engine

import os

os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'



app = Flask(__name__)
app.secret_key = 'dev'
engine = create_engine("sqlite:///jess.db")
repo = ChatHistoryRepo(engine, 'stelee')
profile_repo = ProfileRepo(engine)


bootstrap = Bootstrap5(app)

csrf = CSRFProtect(app)



class ChatForm(FlaskForm):
    content = TextAreaField(label="", render_kw={"class":"form-control type_msg"})
    submit = SubmitField('发送')

class ProfileForm(FlaskForm):
    name = StringField(label="姓名", validators=[DataRequired(), Length(1, 20)])
    displayName = StringField(label="昵称", validators=[DataRequired(), Length(1, 20)])
    avatar = StringField(label="头像", validators=[DataRequired(), Length(1, 20)])
    bot = StringField(label="机器人", validators=[DataRequired(), Length(1, 20)],default='OpenAIBot')
    description = TextAreaField(label="描述", validators=[DataRequired(), Length(1, 2048)], render_kw={"rows":"25"})
    message = TextAreaField(label="消息", validators=[DataRequired()], render_kw={"rows":"30"})
    submit = SubmitField('提交')

def load_bot(profile):
    if profile.bot == 'LoveBot':
        return LoveBot(profile.description,profile.message)
    else:
        return OpenAIBot(profile.description,profile.message)


@app.route('/', methods=['GET','POST'])
def index():
    profile_list = profile_repo.get_profile_list()
    if 'current_profile_name' in session:
        current_profile_name = session['current_profile_name']
        current_profile = profile_repo.get_profile_by_name(current_profile_name)
    else:
        current_profile = profile_list[0]
        session['current_profile_name'] = current_profile.name
    bot = load_bot(current_profile)
    history = repo.get_chat_history_by_name(current_profile.name)
    form = ChatForm()
    rank = 0
    if form.validate_on_submit():
        if form.content.data=='':
            flash('输入内容不能为空')
        else:
            content = form.content.data
            if content.startswith('/save'):#command save the chat history
                pass#todo: save the chat history
            elif content.startswith('/dump'):#dump load the chat history
                filename = content[5:]
                if filename is None or not filename:
                    filename = 'dump'
                timestamp = int(time.time())
                dt_object = datetime.fromtimestamp(timestamp)
                formatted_date = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                with open(f'./profiles/{current_profile.name}/{filename}_{formatted_date}.txt', 'w', encoding='utf-8') as f:
                    for item in rebuild_history(history):
                        f.write(item['content']+'\n')
            else:
                response,history = bot.chat(content, history)
                for record in history[-2:]:
                    repo.insert_message_to_chat_history(current_profile.name, record)
                if isinstance(response['content'], dict) and 'rank' in response['content']:
                    rank = response['content']['rank']
                else:
                    rank = 0
            form.content.data = ''
    return render_template('index.html', form=form, \
                           history=rebuild_history(history),\
                            history_len=len(history), rank=rank, \
                            profiles = profile_list, current_profile = current_profile)

@app.route('/context', methods=['GET','POST'])
def context():
    session.pop('current_profile', None)
    repo.reset_all_history()
    return "hello"

@app.route('/reset', methods=['GET'])
def reset():
    current_profile_name = session['current_profile_name']
    repo.reset_chat_history(current_profile_name)
    return redirect("/")

@app.route('/changeProfile', methods=['GET'])
def change_profile():
    name = request.args.get('name')
    session['current_profile_name'] = name
    return redirect("/")

@app.route('/profile/<name>', methods=['GET','POST'])
def profile(name):
    form = ProfileForm()
    
    form.name.data = name
    
    if form.validate_on_submit():
        profile_repo.add_or_update_profile(form.data)
    else:
        profile = profile_repo.get_profile_by_name(name)
        if profile is not None:
            form.displayName.data = profile.displayName
            form.avatar.data = profile.avatar
            form.bot.data = profile.bot
            form.description.data = profile.description
            form.message.data = profile.message
    return render_template("profile.html", name=name, form=form)

if __name__ == '__main__':
    app.run(debug=True, port=8080)