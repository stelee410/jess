#this is the context file for the application
from sqlalchemy import create_engine
from utils import config,model_repos
from flask import session,Flask,request
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap5
from uuid import UUID

import chromadb

from utils.config import cache_uri

#facility functions
from utils import simple_login_required
from utils import admin_login_required
from utils import admin_was_login_required

engine = create_engine(config.connection_str,pool_size=1024, max_overflow=0)
profile_repo = model_repos.ProfileRepo(engine)
user_repo = model_repos.UserRepo(engine)
balance_repo = model_repos.BalanceRepo(engine)
message_repo = model_repos.MessageRepo(engine)
user_profile_rel_repo = model_repos.UserProfileRelRepo(engine)
chat_history_repo =model_repos.ChatHistoryRepo2(engine)
sharing_link_repo = model_repos.SharingLinkRepo(engine)
app = Flask(__name__)
app.secret_key = config.secret_key
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif','JPG', 'JPEG', 'PNG', 'GIF','webp','WEBP'}
EMBEDDING_MODEL = "text-embedding-3-small"

cache = {} #memory cache for other purpose, it was supposed to used in vector data store, but I have moved to use chroma instead

client =  chromadb.PersistentClient(cache_uri)

NAMESPACE_UUID=UUID('6ba7b811-9dad-11d1-80b4-00c04fd430c8')

def set_session_user(user):
    session['username'] = user.username
    session['displayName'] = user.displayName
    session['avatar'] = user.avatar

def empty_session_user():
    session['username'] = None
    session['displayName'] = None
    session['avatar'] = None
    session['orignal_username'] = None

