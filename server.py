# -*- coding: utf-8 -*-
from context import app
import controllers
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    app.run(debug=True, port=8080)