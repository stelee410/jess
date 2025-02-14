from .base import Base
from context import *

@app.route('/v1/api/ping', methods=['GET'])
def ping():
    return ApiController().ping()

class ApiController(Base):
    def ping(self):
        return self.json({"message": "pong"})