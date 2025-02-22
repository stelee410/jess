from .__inner__ import api
from context import session

@api.route('ping', endpoint='v1_ping') 
def ping():
     try:
          username = session['username']
          avatar = session['avatar']
          displayName = session['displayName']
     except:
          return {
               "success": False,
               "message": "Unauthorized"
          }
     return {
        "success": True,
        "message": "pong",
        "username": username,
        "avatar": avatar,
        "displayName": displayName
     } 

