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
from utils.chat_history import get_profile_history, rebuild_history, save_profile_history, reset_all_history, reset_profile_history
from flask_sqlalchemy import SQLAlchemy

import os

os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'

db = SQLAlchemy()

app = Flask(__name__)
app.secret_key = 'dev'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jess.db"
db.init_app(app)


bootstrap = Bootstrap5(app)

csrf = CSRFProtect(app)

profile_list = [
    {"name":"jess", "displayName" : "JESS🦖🥥", "profile" :"./profiles/jess", "avatar":"jess.jpg", "bot":"LoveBot"},
    {"name":"stephen", "displayName" : "恋爱学长", "profile" :"./profiles/stephen","avatar":"boy.jpg","bot":"OpenAIBot"},
    {"name":"qing", "displayName" : "秦明超医生", "profile" :"./profiles/doc_who","avatar":"doc.jpg","bot":"OpenAIBot"},
    {"name":"wang", "displayName" : "王海涛投资部", "profile" :"./profiles/wang","avatar":"qing.jpg","bot":"OpenAIBot"}
]

class ChatForm(FlaskForm):
    content = TextAreaField(label="", render_kw={"class":"form-control type_msg"})
    submit = SubmitField('发送')

def load_bot(profile):
    if profile['bot'] == 'LoveBot':
        return LoveBot(profile['profile'])
    else:
        return OpenAIBot(profile['profile'])


@app.route('/', methods=['GET','POST'])
def index():
    if 'current_profile' in session:
        current_profile = session['current_profile']
    else:
        current_profile = profile_list[0]
        session['current_profile'] = current_profile
    bot = load_bot(current_profile)
    history = get_profile_history()
    form = ChatForm()
    rank = 0
    if form.validate_on_submit():
        if form.content.data=='':
            flash('输入内容不能为空')
        else:
            content = form.content.data
            if content.startswith('/save'):#command save the chat history
                filename = content[5:]
                if filename is None or not filename:
                    filename = 'chat_history'
                timestamp = int(time.time())
                dt_object = datetime.fromtimestamp(timestamp)
                formatted_date = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                with open(f'{current_profile["profile"]}/{filename}_{formatted_date}.txt', 'w', encoding='utf-8') as f:
                    for item in history:
                        if item['role'] == 'user':
                            f.write("我：" + item['content']+'\n')
                        else:
                            f.write(current_profile.displayName + "：" + item['content']+'\n')
            elif content.startswith('/dump'):#dump load the chat history
                filename = content[5:]
                if filename is None or not filename:
                    filename = 'dump'
                timestamp = int(time.time())
                dt_object = datetime.fromtimestamp(timestamp)
                formatted_date = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                with open(f'{current_profile["profile"]}/{filename}_{formatted_date}.txt', 'w', encoding='utf-8') as f:
                    for item in rebuild_history(history):
                        f.write(item['content']+'\n')
            else:
                response,history = bot.chat(content, history)
                save_profile_history(history)
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
    reset_all_history()
    return "hello"

@app.route('/reset', methods=['GET'])
def reset():
    reset_profile_history()
    return redirect("/")
@app.route('/changeProfile', methods=['GET'])
def change_profile():
    name = request.args.get('name')
    current_profile = session['current_profile']
    if name == current_profile['name']:
        pass #do nothing
    else:
        for profile in profile_list:
            if profile['name'] == name:
                session['current_profile'] = profile
                break
        
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True, port=8080)