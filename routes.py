import base64  # Для кодирования информации в 64-битный код.
import os # Импорт функций для работы с ОС.
from io import BytesIO # Для байтового ввод-вывода.
# Для алгебраических преобразований.
from algebraUtils import count_glucose_error, \
  make_numpy_array_from_list
# Для генерации рекомендаций.
from analyzeUtils import make_recommendation
# Импорт объекта app для использования аннотаций
# Импорт объекта model_connector для обращения к модели.
from app import app, \
  model_connector
# Импорт render_template для рендеринга страницы.
# Импорт redirect для переадресации.
# Импорт url_for для генерации ссылки по имени функции.
# Импорт jsonify - генерация объекта JSON.
# Импорт request - для получения данных из запроса.
# Импорт session - для сохранения в сессии значений.
# Импорт current_app для получения пути до приложения
# Импорт send_from_directory для отправки пользователю файла.
from flask import render_template, \
  redirect, \
  url_for, \
  jsonify, \
  request, session, current_app, send_from_directory
# Импорт необходимых форм/
from forms import RegistrationForm, \
  LoginForm, \
  ManualInputForm
# Импорт login_required для указания необходимости авторизации.
# Импорт login_user для авторизации пользователя.
# Импорт current_user для получения данных о текущем пользователе.
# Импорт logout_ser для реализации выхода из системы.
from flask_login import login_required, \
  login_user, \
  current_user, \
  logout_user
# Для работы с метками на графике.
from matplotlib import ticker
# Для создания графика.
from matplotlib.figure import Figure
# Для работы с БД.
from usersDB import User, \
  Measurement, \
  add_data, \
  find_user, \
  get_last_measurement, \
  get_time_series_data, \
  get_history
# Для работы с временными метками.
from datetime import datetime, \
  timedelta # Для арифметики со временем.
# Для обработки ошибок.
from wtforms import ValidationError


# Адрес запроса.
@app.route('/')
# Функция для обработки запросов к начальной странице.
def index():
  # Если пользователь уже авторизован.
  if current_user.is_authenticated:
    #Установка значения connected в переменнах сессии.
    session['connected'] = False
    # Генерация ссылки и переадресации по ней (осуществляется GET-запрос).
    return redirect(url_for('user_profile', user_id=current_user.get_id()))
  # Рендеринг страницы.
  return render_template('index.html')

# Адрес запроса и типы запроса.
@app.route('/registration', methods=['GET', 'POST'])
def registration():
  # Создание объекта формы.
  registration_form = RegistrationForm()
  # Если была нажата кнопка "Подтвердить", то проверка введёных данных.
  if registration_form.validate_on_submit():
    # Если данные корректны, создать объект "пользователь"
    user = User(firstname=registration_form.firstname.data,
                lastname=registration_form.lastname.data,
                middlename=registration_form.middlename.data,
                date_of_birth=registration_form.date_of_birth.data,
                email=registration_form.email.data)
    # Хэширование пароля.
    user.set_password(registration_form.password.data)
    # Добавление в БД.
    add_data(user)
    # Переадресация на страницу входа.
    return redirect(url_for('login'))
  # Рендеринг страницы с формой.
  return render_template("registration.html", form=registration_form)

# Адрес запроса и типы запроса.
@app.route('/login', methods=['GET', 'POST'])
# Функция для входа пользователя.
def login():
  # Если пользователь уже авторизован.
  if current_user.is_authenticated:
    # Установка значения переменной сессии.
    session['connected'] = False
    # Переадресация в личный кабинет пользователя.
    return redirect(url_for('user_profile', user_id=current_user.get_id()))
  # Создание объекта формы.
  login_form = LoginForm()
  # Если была нажата кнопка войти.
  if login_form.validate_on_submit():
    # Поиск существующего пользователя.
    user = find_user(login_form.email.data)
    # Авторизация пользователя.
    login_user(user, remember=login_form.remember_me.data)
    # Установка значения переменной сессии.
    session['connected'] = False
    # Переадресация в личный кабинет.
    return redirect(url_for('user_profile', user_id=user.user_id))
  # Рендеринг страницы с формой.
  return render_template('login.html', form=login_form)

# Адрес запроса.
@app.route('/logout')
# Указание необходимой авторизации.
@login_required
# Функция для выхода пользователя из системы.
def logout():
  # Реализация выхода из системы.
  logout_user()
  # Установка в переменной сессии значения.
  session['connected'] = False
  # Переадресация на страницу входа.
  return redirect(url_for('login'))

# Адрес запроса с параметром.
@app.route('/user/id<user_id>')
# Указание необходимой авторизации.
@login_required
# Функция для отрисовки страницы личного кабинета пользователя.
def user_profile(user_id):
  # Рендеринг страницы личного кабинета пользователя.
  return render_template('userPage.html', user_data=current_user)

# Адрес запроса с параметром и типы запроса.
@app.route('/user/id<user_id>/<device>', methods=['GET', 'POST'])
# Указание необходимой авторизации.
@login_required
# Функция для рендеринга рабочего пространства в авто режиме.
def user_device_connected(user_id, device):
  return render_template('userDeviceConnected.html')

# Адрес запроса с параметром и типы запроса.
@app.route('/user/id<user_id>/manual', methods=['GET', 'POST'])
# Указание необходимой авторизации.
@login_required
# Функция для рендеринга рабочего пространства в ручном режиме.
def user_manual_work(user_id):
  # Создание формы ввода данных в ручном режиме.
  manual_input_form = ManualInputForm()
  # Для вывода ошибок.
  errors = ""
  # Если совершен POST запрос.
  if request.method == 'POST':
    # Получение отправленных данных с запросом.
    data = request.form.get('glucose_value')
    try:
      # Если данные корректны.
      if float(data) and \
          manual_input_form.validate_glucose_value(data):
        # Создание временной метки
        timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        # Создание объекта "Измерение"
        measurement = Measurement(measurement_user=user_id,
                                  timestamp=int(timestamp),
                                  glucose_value=float(data))
        # Добавление записи в БД.
        add_data(measurement)
        # Переадресация на рабочее пространство пользователя.
        return redirect(url_for('user_manual_work', user_id=current_user.get_id()))
    # Поймана ошибка валидации.
    except ValidationError as err:
      errors = err
    # Поймана ошибка неверного типа данных.
    except ValueError:
      errors = "Значение не должно быть строкой"
  # Рендеринг страницы для рабочего пространства.
  return render_template('userManualMode.html', form=manual_input_form,
                         errors=errors)

# Адрес запроса с параметром и типы запроса.
@app.route('/update_data/<user_id>', methods=['GET'])
# Указание необходимой авторизации.
@login_required
# Функция для обновления данных на рабочем пространстве.
def update_data(user_id):
  # Получение последней записи измерения.
  last_measurement = get_last_measurement(user_id)
  result_plot = ""
  # Если данных еще нет.
  if last_measurement is None:
    current_glucose_value = "Нет данных"
    current_time = "Нет данных"
  else:
    current_glucose_value = str(last_measurement.glucose_value)
    current_time = datetime.fromtimestamp(last_measurement.timestamp)
  # Попытка получения последних 128 записей измерений.
  time_series = get_time_series_data(user_id)
  # Если данных в базе недостаточно.
  if len(time_series) < 128:
    predicted_glucose_value = "Данных еще недостаточно"
    recommendation = "Данных еще недостаточно"
  else:
    # Списки для осей и графика.
    time_series_list = []
    datetime_list = []
    # Заполнение списков.
    for i in range(len(time_series)):
      time_series_list.append(time_series[i].glucose_value)
      datetime_list.append(datetime.
                           fromtimestamp(time_series[i].timestamp).
                           strftime("%H:%M:%S"))
    # Разворот списков для соблюдения хронологии.
    time_series_list.reverse()
    datetime_list.reverse()
    # Временная метка для предсказанного значения.
    predicted_value_timestamp = (datetime. \
                                 fromtimestamp(time_series[0].timestamp) \
                                 + timedelta(hours=1)).strftime("%H:%M:%S")
    # Прогнозирование.
    predicted_glucose_value = model_connector.make_prediction(time_series_list)
    # Округление до 2 знаков после запятой.
    predicted_glucose_value = round(predicted_glucose_value[0][0], 2)
    # Расчёт и округление до 2 знаков после запятой допустимой погрешности.
    glucose_error_value = round(count_glucose_error(predicted_glucose_value), 2)
    # Выработка рекомендации.
    recommendation = make_recommendation(predicted_glucose_value, glucose_error_value)
    # Преобразование списков в NumPy массив.
    time_series_array = make_numpy_array_from_list(time_series_list)
    datetime_array = make_numpy_array_from_list(datetime_list)
    # Создание фигуры для графика
    image = Figure(figsize=(10, 8))
    # Создание конструктора графиков.
    plot = image.subplots()
    # График изменения уровня глюкозы за 128 значений.
    plot.plot(datetime_array, time_series_array, color='blue')
    # Отображение погрешности на графике.
    plot.plot([predicted_value_timestamp,
               predicted_value_timestamp,
               predicted_value_timestamp],
              [predicted_glucose_value - glucose_error_value,
               predicted_glucose_value,
               predicted_glucose_value + glucose_error_value],
              'p-')
    # Точка для предсказанного значения.
    plot.plot(predicted_value_timestamp,
              predicted_glucose_value,
              'r*')
    # Для редактирований свойств графика.
    ax = image.gca()
    # Уменьшения общего кол-ва меток на графике.
    ax.xaxis.set_major_locator(ticker.MultipleLocator(4))
    # Разворот меток на оси X на 90 градусов.
    ax.tick_params(axis='x', labelrotation=90)
    # Создание буфера для байтового ввода-вывода.
    buffer = BytesIO()
    # Сохранение изображения в буфере.
    image.savefig(buffer, format="png")
    # Кодировка графика в 64-разрядном формате и его последующая декодировка в ASCII.
    result_plot = base64.b64encode(buffer.getbuffer()).decode("ascii")

  # Возвращает JSON объект.
  return jsonify({
    'current_time': current_time.strftime("%d-%m-%Y %H:%M:%S"),
    'current_glucose_value': current_glucose_value,
    'predicted_glucose_value': str(predicted_glucose_value) + " ± " + str(glucose_error_value),
    'plot': f"<img class='edge' src='data:image/png;base64,{result_plot}'/>",
    'recommendation': recommendation
  })

# Адрес запроса с параметром и типы запроса.
@app.route('/history/<user_id>', methods=['GET'])
# Указание необходимой авторизации.
@login_required
# Функция для генерации истории изменения уровня глюкозы
def download_history(user_id):
  # Получение данных за весь период времени.
  time_series = get_history(user_id)
  # Списки для создания осей и графика.
  time_series_list = []
  datetime_list = []
  # Заполнение списков.
  for i in range(len(time_series)):
    time_series_list.append(time_series[i].glucose_value)
    datetime_list.append(datetime.
                         fromtimestamp(time_series[i].timestamp).
                         strftime("%H:%M:%S"))
  # Разворот списков для соблюдения хронологии.
  time_series_list.reverse()
  datetime_list.reverse()
  # Создания фигуры для графика.
  image = Figure(figsize=(10, 8))
  # Создание конструктора графиков.
  plot = image.subplots()
  # Создание NumPy массивов из списков.
  time_series_array = make_numpy_array_from_list(time_series_list)
  datetime_array = make_numpy_array_from_list(datetime_list)
  # Построение графика.
  plot.plot(datetime_array, time_series_array, color='blue')
  # Для редактирований св-в графика.
  ax = image.gca()
  # Убираем ось х, т.к. слишком много временных меток.
  ax.tick_params(axis='x', length=0, labelsize=0)
  # Соединяем адрес расположения приложения с адресом расположения папки с историями.
  uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
  # Имя сгенерированного файла.
  filename = user_id + "_history.png"
  # Сохранение графика по указанному пути.
  image.savefig(os.path.join(uploads, filename))
  # Отправка файла пользователю.
  return send_from_directory(directory=uploads, path=filename)

# Адрес запроса с параметром и типы запроса.
@app.route('/bluconnect/<user_id>', methods=['GET'])
# Указание необходимой авторизации.
@login_required
# Функция для изменения переменной сессии
def device_connected(user_id):
  session['connected'] = True
  return "OK"

# Адрес запроса с параметром и типы запроса.
@app.route('/bludisconnect/<user_id>', methods=['GET'])
# Указание необходимой авторизации.
@login_required
# Функция для изменения переменной сессии
def device_disconnected(user_id):
  session['connected'] = False
  return "OK"

# Адрес запроса с параметром и типы запроса.
@app.route('/bluvalue/<user_id>', methods=['POST'])
# Указание необходимой авторизации.
@login_required
# Функция для записи в БД сигнала с устройства
def device_value(user_id):
  data = request.get_json()
  value = data['glucose_value']
  # Создание временной метки
  timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
  # Создание объекта "Измерение"
  measurement = Measurement(measurement_user=user_id,
                            timestamp=int(timestamp),
                            glucose_value=float(value))
  # Добавление записи в БД.
  add_data(measurement)
  return "OK"