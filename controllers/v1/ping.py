from context import *

@app.route('/api/v1/ping', endpoint='v1_ping') 
def ping():
    return {"message": "pong"} 