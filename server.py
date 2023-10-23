# -*- coding: utf-8 -*-
import sys
from sys import platform
if platform == "linux" or platform == "linux2":
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from context import app
import controllers
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    app.run(debug=True, port=8080)