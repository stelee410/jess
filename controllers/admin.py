from .base import Base
from context import *

@app.route('/admin/login_as/<username>', methods=['GET'])
@admin_login_required
def admin_login_as(username):
    return AdminController().login_as(username)

@app.route('/admin/login_back', methods=['GET'])
@admin_was_login_required
def admin_login_back():
    return AdminController().login_back()

class AdminController(Base):
    def login_as(self, username):
        user = user_repo.get_user_by_username(username)
        if user is None:
            self.abort(404,"User not found")
                  
        session["orignal_username"] = session["username"]
        set_session_user(user)
        return self.redirect('/')
    def login_back(self):
        username = session["orignal_username"]
        user = user_repo.get_user_by_username(username)
        set_session_user(user)
        return self.redirect('/')