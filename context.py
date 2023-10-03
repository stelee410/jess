#this is the context file for the application
from sqlalchemy import create_engine
from utils import config,model_repos
from flask import session,Flask,request
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap5

engine = create_engine(config.connection_str,pool_size=1024, max_overflow=0)
profile_repo = model_repos.ProfileRepo(engine)
user_repo = model_repos.UserRepo(engine)
balance_repo = model_repos.BalanceRepo(engine)
message_repo = model_repos.MessageRepo(engine)
user_profile_rel_repo = model_repos.UserProfileRelRepo(engine)
chat_history_repo =model_repos.ChatHistoryRepo2(engine)
app = Flask(__name__)
app.secret_key = config.secret_key
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif','JPG', 'JPEG', 'PNG', 'GIF','webp','WEBP'}
