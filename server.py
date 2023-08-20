# -*- coding: utf-8 -*-
from enum import Enum
from flask import Flask, render_template, request, flash, redirect, url_for, session
from markupsafe import Markup
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import DataRequired, Length, Regexp
from wtforms.fields import *
from flask_bootstrap import Bootstrap5, SwitchField
import time
import json
from datetime import datetime
from bot.chat import LoveBot, OpenAIBot

import os
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'

app = Flask(__name__)
app.secret_key = 'dev'



bootstrap = Bootstrap5(app)

csrf = CSRFProtect(app)

profile_list = [
    {"name":"jess", "displayName" : "JESS🦖🥥", "profile" :"./profiles/jess", "avatar":"jess.jpg"},
    {"name":"stephen", "displayName" : "Stephen Li", "profile" :"./profiles/stephen","avatar":"stephen.jpg"}
]

bot = LoveBot("./profiles/jess")

def rebuild_history(history):
    new_history = []
    for item in history:
        content_string = item['content']
        try:
            json_object = json.loads(content_string)
            content_string = json_object['content']
        except json.JSONDecodeError:
            pass
        if item['role'] == 'user':
            new_history.append({"role":"user","content":content_string})
        else:
            new_history.append({"role":"assistant","content":content_string})
    return new_history

class ChatForm(FlaskForm):
    content = TextAreaField(label="", render_kw={"class":"form-control type_msg"})
    submit = SubmitField('发送')
    


@app.route('/', methods=['GET','POST'])
def index():
    if 'history' in session:
        history = session['history']
    else:
        history = []
        session['history'] = history
    if 'current_profile' in session:
        current_profile = session['current_profile']
    else:
        current_profile = profile_list[0]
        session['current_profile'] = current_profile

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
                with open(f'./profiles/jess/{filename}_{formatted_date}.txt', 'w', encoding='utf-8') as f:
                    for item in history:
                        if item['role'] == 'user':
                            f.write("我：" + item['content']+'\n')
                        else:
                            f.write("Jess：" + item['content']+'\n')
            elif content.startswith('/dump'):#dump load the chat history
                filename = content[5:]
                if filename is None or not filename:
                    filename = 'dump'
                timestamp = int(time.time())
                dt_object = datetime.fromtimestamp(timestamp)
                formatted_date = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                with open(f'./profiles/jess/{filename}_{formatted_date}.txt', 'w', encoding='utf-8') as f:
                    for item in rebuild_history(history):
                        f.write(item['content']+'\n')
            else:
                response,history = bot.chat(content, history)
                session['history'] = history
                rank = response['content']['rank']
            form.content.data = ''
    return render_template('index.html', form=form, \
                           history=rebuild_history(history),\
                            history_len=len(history), rank=rank, \
                            profiles = profile_list, current_profile = current_profile)

@app.route('/context', methods=['GET','POST'])
def context():
    session['history'] = []
    return "hello"

@app.route('/reset', methods=['GET'])
def reset():
    session['history'] = []
    return redirect("/")
@app.route('/changeProfile', methods=['GET'])
def change_profile():
    name = request.args.get('name')
    current_profile = session['current_profile']
    if name == current_profile.name:
        pass #do nothing
    else:
        for profile in profile_list:
            if profile.name == name:
                session['current_profile'] = profile
                break
        
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)