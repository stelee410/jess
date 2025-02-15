from context import *

API_V1_PREFIX = '/api/v1'

def build_url(path):
    return f"{API_V1_PREFIX}/{path}"

class Api:
    def route(self, path, **options):
        def decorator(f):
            return app.route(build_url(path), **options)(f)
        return decorator
    
api = Api()