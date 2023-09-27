from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField,FileField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileRequired, FileAllowed, FileField

class ChatForm(FlaskForm):
    content = TextAreaField(label="", render_kw={"class":"form-control type_msg"})
    submit = SubmitField('发送')
class ReigsterForm(FlaskForm):
    username = StringField(label="用户名", validators=[DataRequired(), Length(1, 20)])
    password = PasswordField(label="密码", validators=[Length(0, 20)])
    password_confirm = PasswordField(label="确认密码", validators=[Length(0, 20)])
    invitation_code = StringField(label="邀请码", validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField('保存',render_kw={"class":'single-btn',"style":'margin-left:0px'})
