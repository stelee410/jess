import os
from .chat_completion import (ChatCompletion)

api_key = os.getenv('BAIDU_API_KEY') 
secret_key = os.getenv('BAIDU_SECRET_KEY') 

__all__ =[
    "api_key",
    "secret_key",
    "ChatCompletion"
]








    