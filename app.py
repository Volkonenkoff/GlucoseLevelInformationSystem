'''
    Импорт из библиотеки flask:
        1. Класс Flask - основа для работы приложения на фреймворке flask.
        2. render_template - для отрисовки шаблонов.
        3. request - для работы с запросами
'''
from flask import Flask
from flask_login import LoginManager
from modelConnector import ModelConnector
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

model_connector = ModelConnector(glucose_predictor_path)

import routes

'''
    Условие обеспечивает вызов метода run() в случае,
    если app.py запускается в качестве основной программы
'''
if __name__ == '__app__':
    app.run(debug=False)
