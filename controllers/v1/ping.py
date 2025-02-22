from .__inner__ import api
from context import session

@api.route('ping', endpoint='v1_ping') 
def ping():
     username = session['username']
     avatar = session['avatar']
     displayName = session['displayName']
     return {
        "success": True,
        "message": "pong",
        "username": username,
        "avatar": avatar,
        "displayName": displayName
     } 

