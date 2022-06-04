'''
    Импорт из библиотеки flask:
        1. Класс Flask - основа для работы приложения на фреймворке flask.
        2. render_template - для отрисовки шаблонов.
        3. request - для работы с запросами
'''
import asyncio
import sys

from flask import Flask
from flask_login import LoginManager
from modelConnector import ModelConnector
from configuration import *

'''
    Создание объекта класса Flask
        __name__ - имя пакета (обязательный аргумент)
'''
app = Flask(__name__)
app.secret_key = "aboba"
glucose_predictor_path = "static/myRNNModel.h5"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
  asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
model_connector = ModelConnector(glucose_predictor_path)

import routes

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
'''
    Условие обеспечивает вызов метода run() в случае,
    если app.py запускается в качестве основной программы
'''
if __name__ == '__app__':
  app.run(debug=False)
