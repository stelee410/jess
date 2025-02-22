from .base import Base
from forms import ReigsterForm
from utils.password_hash import get_password_hash
from context import *


@app.route('/register/<invitation_code>', methods=['GET','POST'])
def register(invitation_code):
    register = Register()
    return register.execute(invitation_code)


@app.route('/register', methods=['GET','POST'])
def register_no_invite():
    register = Register()
    return register.execute()

class Register(Base):
    def execute(self, invitation_code=""):
        form = ReigsterForm()
        if form.validate_on_submit():
            data ={}
            data['username'] =  form.username.data
            invitation_code = form.invitation_code.data
            if user_repo.is_invitation_code_available(invitation_code) is False:
                self.flash("Wrong invitation code")
                return self.render('register.html', form=form)
            if user_repo.get_user_by_username(data['username']) is not None:
                self.flash("Username already exists")
                return self.render('register.html', form=form)
            data['avatar'] = 'images/default.png'
            password = form.password.data
            passowrd_confirm = form.password_confirm.data
            if password != passowrd_confirm:
                self.flash("Passwords do not match")
                return self.render('register.html', form=form)
            data['password'] = get_password_hash(password,app.secret_key)
            data['displayName'] = form.username.data
            data['description'] = ""
            user_repo.insert_user(**data)
            user_repo.decrease_invitation_count(invitation_code)
            return self.redirect("/login")
        else:
            form.invitation_code.data = invitation_code
        return self.render('register.html', form=form)