from .__inner__ import api

@api.route('ping', endpoint='v1_ping') 
def ping():
    return {"message": "pong"} 

