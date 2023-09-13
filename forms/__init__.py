from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField

class ChatForm(FlaskForm):
    content = TextAreaField(label="", render_kw={"class":"form-control type_msg"})
    submit = SubmitField('发送')