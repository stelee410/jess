from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField,FileField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileRequired, FileAllowed, FileField
from context import ALLOWED_EXTENSIONS

class ChatForm(FlaskForm):
    content = TextAreaField(label="", render_kw={"class":"form-control type_msg"})
    submit = SubmitField('发送')

class ReigsterForm(FlaskForm):
    username = StringField(label="用户名", validators=[DataRequired(), Length(1, 20)])
    password = PasswordField(label="密码", validators=[Length(0, 20)])
    password_confirm = PasswordField(label="确认密码", validators=[Length(0, 20)])
    invitation_code = StringField(label="邀请码", validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField('保存',render_kw={"class":'single-btn',"style":'margin-left:0px'})

class ProfileForm(FlaskForm):
    name = StringField(label="Unique ID", validators=[DataRequired(), Length(1, 20)])
    displayName = StringField(label=" Name", validators=[DataRequired(), Length(1, 20)])
    avatar = FileField(label="Avatar", validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')])
    short_description = TextAreaField(label="Description(not affect settings)", validators=[Length(0, 2048)], render_kw={"rows":"6"})

class ProfileUpdateForm(FlaskForm):
    displayName = StringField(label="Name", validators=[DataRequired(), Length(1, 20)])
    avatar = FileField(label="Avatar", validators=[FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')])
    short_description = TextAreaField(label="Description(not affect settings)", validators=[Length(0, 2048)], render_kw={"rows":"6"})

class LoginForm(FlaskForm):
    username = StringField(label="用户名", validators=[DataRequired(), Length(1, 20)])
    password = PasswordField(label="密码", validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField('登录')

class TransferForm(FlaskForm):
    username = StringField(label="Other User Name", validators=[DataRequired(), Length(1, 10)])
    submit = SubmitField('Send')
class DeleteForm(FlaskForm):
    username = StringField(label='Please enter "Confirmed"', validators=[DataRequired(), Length(1, 10)])
    submit = SubmitField('Send')

class UserForm(FlaskForm):
    displayName = StringField(label="Name", validators=[DataRequired(), Length(1, 20)])
    avatar = FileField(label="Avatar", validators=[FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')])
    description = TextAreaField(label="描述", validators=[Length(0, 2048)], render_kw={"rows":"10"})
    password = PasswordField(label="旧密码", validators=[Length(0, 20)])
    password_new = PasswordField(label="新密码", validators=[Length(0, 20)])
    password_new_confirm = PasswordField(label="确认密码", validators=[Length(0, 20)])