from .__inner__ import api
from context import *
from utils import simple_login_required
from utils.password_hash import get_password_hash

@csrf.exempt
@api.route('login', endpoint='v1_login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    password_hash = get_password_hash(password,app.secret_key)
    user = user_repo.get_user_by_username_password(username, password_hash)
    if user is None:
        return {
            'success': False,
            'message': 'username or password error'
        }
    else:
        set_session_user(user)
        return {
            'success': True,
            'message': 'login success',
            'user': {
                'username': user.username,
                'displayName': user.displayName,
                'avatar': user.avatar,
            }
        }

