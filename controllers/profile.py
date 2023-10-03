from .base import Base
from context import *
from utils import simple_login_required
from utils.model_repos import PROFILE_SCOPE_PUBLIC,PROFILE_SCOPE_PRIVATE
from forms import ProfileUpdateForm,ProfileForm,TransferForm,DeleteForm
from werkzeug.utils import secure_filename
import os
import time

@app.route('/profile/<name>', methods=['GET','POST'])
@simple_login_required
def profile(name):
    return ProfileController().execute(name)

@app.route('/profile/:create', methods=['GET','POST'])
@simple_login_required
def new_profile():
    return ProfileController().new()

@app.route('/profile/<name>/offline', methods=['GET'])
@simple_login_required
def offline(name):
    return ProfileController().offline(name)

@app.route('/profile/<name>/online', methods=['GET'])
@simple_login_required
def online(name):
    return ProfileController().online(name)

@app.route('/profile/<name>/transfer', methods=['GET','POST'])
@simple_login_required
def transfer(name):
    return ProfileController().transfer(name)

@app.route('/profile/<name>/delete', methods=['GET','POST'])
@simple_login_required
def delete(name):
    return ProfileController().delete(name)
@app.route('/profile/<name>/:scope/<scope_str>', methods=['GET','POST'])
@simple_login_required
def set_profile_scope(name, scope_str):
    return ProfileController().set_scope(name, scope_str)

class ProfileController(Base):
    def set_scope(self, name, scope_str):
        if scope_str == 'public':
            scope = PROFILE_SCOPE_PUBLIC
        else:
            scope = PROFILE_SCOPE_PRIVATE
        profile = profile_repo.get_profile_by_name(name)
        if profile.owned_by != session.get('username'):
            return self.render("500.html", message=f"Profile {name} not owned by {session.get('username')}")
        profile_repo.set_profile_scope(name,scope)
        return self.redirect(f"/profile/{name}")
    
    def delete(self,name):
        form = DeleteForm()
        profile = profile_repo.get_profile_by_name(name)
        if profile is None:
            return self.render("404.html", message=f"Profile {name} not found")
        if profile.owned_by != session.get('username'):
            return self.render("500.html", message=f"Profile {name} not owned by {session.get('username')}")
        if form.validate_on_submit():
            if form.username.data == "我确认删除这个数字人":
                profile_repo.delete_profile(name)
                return self.redirect("/")
            else:
                self.flash('输入错误')
        return self.render("delete.html", form=form)
    def transfer(self,name):
        form = TransferForm()
        profile = profile_repo.get_profile_by_name(name)
        if profile is None:
            return self.render("404.html", message=f"Profile {name} not found")
        if profile.owned_by != session.get('username'):
            return self.render("500.html", message=f"Profile {name} not owned by {session.get('username')}")
        if form.validate_on_submit():
            user = user_repo.get_user_by_username(form.username.data)
            if user is None:
                return self.render("404.html", message=f"User {form.username.data} not found")
            profile_repo.transfer_profile(name,session.get('username'),form.username.data)
            return self.redirect("/")
        return self.render("transfer.html", form=form)
    def online(self,name):
        profile = profile_repo.get_profile_by_name(name)
        if profile.owned_by != session.get('username'):
            return self.render("500.html", message=f"Profile {name} not owned by {session.get('username')}")
        profile_repo.set_profile_online(name)
        return self.redirect(f"/profile/{name}")
    
    def offline(self,name):
        profile = profile_repo.get_profile_by_name(name)
        if profile.owned_by != session.get('username'):
            return self.render("500.html", message=f"Profile {name} not owned by {session.get('username')}")
        profile_repo.set_profile_offline(name)
        return self.redirect(f"/profile/{name}")
    def new(self):
        form = ProfileForm()
        if form.validate_on_submit():
            profile = profile_repo.get_profile_by_name(form.name.data)
            if profile is not None:
                self.flash('用户已存在')
                return self.render("new_profile.html", form=form)
            data = form.data
            if form.avatar.data:
                file = form.avatar.data
                filename = secure_filename(file.filename)
                current_timestamp = int(time.time())
                filename = f"{current_timestamp}_{filename}"
                if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                    file.save(os.path.join('./static/profiles', filename))
                    data['avatar'] = f"profiles/{filename}"
            profile_repo.add(data,session.get('username'))
            return self.redirect("/profile/"+data['name'])
        return self.render("new_profile.html", form=form)
    
    def execute(self,name):
        form = ProfileUpdateForm()
        profile = profile_repo.get_profile_by_name(name)
        if profile is None:
            return self.render("404.html", message=f"Profile {name} not found")
        if profile.owned_by != session.get('username'):
            return self.render("500.html", message=f"Profile {name} not owned by {session.get('username')}")
        if form.validate_on_submit():
            data = form.data
            data_to_update={}
            if form.avatar.data:
                file = form.avatar.data
                filename = secure_filename(file.filename)
                current_timestamp = int(time.time())
                filename = f"{current_timestamp}_{filename}"
                if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                    file.save(os.path.join('./static/profiles', filename))
                    data_to_update['avatar'] = f"profiles/{filename}"
            else:
                data_to_update['avatar'] = profile.avatar
            data_to_update['displayName'] = data['displayName']
            data_to_update['short_description'] = data['short_description']
            profile_repo.update_profile(name, data_to_update)
        else:
            form.displayName.data = profile.displayName
            form.short_description.data = profile.short_description
        return self.render("profile.html", name=name, form=form, profile=profile)