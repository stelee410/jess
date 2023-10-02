#this is the context file for the application
from sqlalchemy import create_engine
from utils import config,model_repos

engine = create_engine(config.connection_str,pool_size=1024, max_overflow=0)
profile_repo = model_repos.ProfileRepo(engine)
user_repo = model_repos.UserRepo(engine)
balance_repo = model_repos.BalanceRepo(engine)
message_repo = model_repos.MessageRepo(engine)