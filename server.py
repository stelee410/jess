# -*- coding: utf-8 -*-
from enum import Enum
from flask import Flask, render_template, request, flash, redirect, url_for, session
from markupsafe import Markup
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import DataRequired, Length, Regexp
from wtforms.fields import *
from flask_bootstrap import Bootstrap5, SwitchField
from flask_sqlalchemy import SQLAlchemy
import openai
import time
from datetime import datetime

import os
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'

app = Flask(__name__)
app.secret_key = 'dev'



bootstrap = Bootstrap5(app)

csrf = CSRFProtect(app)

with open('./profiles/jess/description.txt', 'r', encoding='utf-8') as f:
    initMsg = f.read()
with open('./profiles/jess/chat.txt', 'r', encoding='utf-8') as f:
    feeds = f.read()

feedsArray = feeds.splitlines()
initContext=[{"role":"system","content":initMsg}]
if len(feedsArray)%2 == 0:
    role = "user"

    for feed in feedsArray:
        initContext.append({"role":role,"content":feed})
        if role == "user":
          role = "assistant"
        else:
          role = "user"
else:
    print("feedsArray is not even!")



def chat(message, history, model="gpt-3.5-turbo-16k",temperature = 0.5):
    history.append({"role":"user","content":message})
    response = openai.ChatCompletion.create(model=model,messages=history,temperature=temperature)
    history.append(response.choices[0].message)
    return response.choices[0].message


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
    form = ChatForm()
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
            else:
                response = chat(content, initContext+history)
                history.append({'role':'user', 'content': content})
                history.append({'role':'assistant', 'content': response.content})
                session['history'] = history
            form.content.data = ''
    return render_template('index.html', form=form, history=history,history_len=len(history))

@app.route('/context', methods=['GET','POST'])
def context():
    session['history'] = []
    return "hello"

@app.route('/reset', methods=['GET'])
def reset():
    session['history'] = []
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)