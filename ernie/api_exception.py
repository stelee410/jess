class APIException(Exception):
    code:int
    msg: str
    def __init__(self, code, msg) -> None:
        self.code = code
        self.msg = msg