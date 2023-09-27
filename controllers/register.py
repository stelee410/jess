from .base import Base
from forms import ReigsterForm
from werkzeug.utils import secure_filename
from utils.model_repos import UserRepo
from utils.password_hash import get_password_hash
import time
import os


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

class Register(Base):
    def execute(self):
        form = ReigsterForm()
        engine = self.context["engine"]
        app = self.context["app"]
        userRep = UserRepo(engine)
        if form.validate_on_submit():
            data ={}
            data['username'] =  form.username.data
            invitation_code = form.invitation_code.data
            if userRep.is_invitation_code_available(invitation_code) is False:
                self.flash("邀请码错误")
                return self.render('register.html', form=form)
            if userRep.get_user_by_username(data['username']) is not None:
                self.flash("用户名已经存在")
                return self.render('register.html', form=form)
            data['avatar'] = 'images/default.png'
            password = form.password.data
            passowrd_confirm = form.password_confirm.data
            if password != passowrd_confirm:
                self.flash("两次输入的密码不一致")
                return self.render('register.html', form=form)
            data['password'] = get_password_hash(password,app.secret_key)
            data['displayName'] = form.username.data
            data['description'] = ""
            userRep.insert_user(**data)
            userRep.decrease_invitation_count(invitation_code)
            return self.redirect("/login")
        else:
            form.invitation_code.data = self.context['invitation_code']
        return self.render('register.html', form=form)