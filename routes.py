import base64
from io import BytesIO

from algebraUtils import count_glucose_error, make_numpy_array_from_list
from app import app, \
    model_connector
from flask import render_template, \
    redirect, \
    url_for, \
    jsonify, \
    request
from forms import RegistrationForm, \
    LoginForm, \
    ManualInputForm
from flask_login import login_required, \
    login_user, \
    current_user, \
    logout_user
from matplotlib import ticker
from matplotlib.figure import Figure
from usersDB import User, \
    Measurement, \
    add_data, \
    find_user, \
    get_last_measurement, \
    get_time_series_data
from datetime import datetime, timedelta

from wtforms import ValidationError

import matplotlib.pyplot as plt


@app.route('/')  # Маршрут
def index():  # Функция отвечающая на запрос по маршруту '/'
    if current_user.is_authenticated:
        return redirect(url_for('user_profile', user_id=current_user.get_id()))
    return render_template('index.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        user = User(firstname=registration_form.firstname.data,
                    lastname=registration_form.lastname.data,
                    middlename=registration_form.middlename.data,
                    date_of_birth=registration_form.date_of_birth.data,
                    email=registration_form.email.data)
        user.set_password(registration_form.password.data)
        add_data(user)
        return redirect(url_for('login'))
    return render_template("registration.html", form=registration_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_profile', user_id=current_user.get_id()))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = find_user(login_form.email.data)
        login_user(user, remember=login_form.remember_me.data)
        return redirect(url_for('user_profile', user_id=user.user_id))
    return render_template('login.html', form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/user/id<user_id>')
@login_required
def user_profile(user_id):
    return render_template('userPage.html', user_data=current_user)


@app.route('/user/id<user_id>/<device>')
@login_required
def user_device_connected(user_id, device):
    return "aboba"


@app.route('/user/id<user_id>/manual', methods=['GET', 'POST'])
@login_required
def user_manual_work(user_id):
    manual_input_form = ManualInputForm()
    errors = ""

    if request.method == 'POST':
        data = request.form.get('glucose_value')
        try:
            if float(data) and \
                    manual_input_form.validate_glucose_value(data):
                timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
                measurement = Measurement(measurement_user=user_id,
                                          timestamp=int(timestamp),
                                          glucose_value=float(data))
                add_data(measurement)
                redirect(url_for('user_manual_work', user_id=current_user.get_id()))
        except ValidationError as err:
            errors = err
        except ValueError:
            errors = "Значение не должно быть строкой"

    return render_template('userManualMode.html', form=manual_input_form,
                           errors=errors)


@app.route('/update_data/<user_id>', methods=['GET'])
@login_required
def update_data(user_id):
    last_measurement = get_last_measurement(user_id)
    result_plot = ""
    if last_measurement is None:
        current_glucose_value = "Нет данных"
        current_time = "Нет данных"
    else:
        current_glucose_value = str(last_measurement.glucose_value)
        current_time = datetime.fromtimestamp(last_measurement.timestamp)
    time_series = get_time_series_data(user_id)
    if len(time_series) < 128:
        predicted_glucose_value = "Данных еще недостаточно"
    else:
        time_series_list = []
        datetime_list = []
        for i in range(len(time_series)):
            time_series_list.append(time_series[i].glucose_value)
            datetime_list.append(datetime.
                                 fromtimestamp(time_series[i].timestamp).
                                 strftime("%H:%M:%S"))
        time_series_list.reverse()
        datetime_list.reverse()
        predicted_value_timestamp = (datetime. \
                                     fromtimestamp(time_series[0].timestamp) \
                                     + timedelta(hours=1)).strftime("%H:%M:%S")
        predicted_glucose_value = model_connector.make_prediction(time_series_list)
        predicted_glucose_value = round(predicted_glucose_value[0][0], 2)
        glucose_error_value = round(count_glucose_error(predicted_glucose_value), 2)
        time_series_array = make_numpy_array_from_list(time_series_list)
        datetime_array = make_numpy_array_from_list(datetime_list)
        image = Figure(figsize=(10, 8))
        plot = image.subplots()
        plot.plot(datetime_array, time_series_array, color='blue')
        plot.plot([predicted_value_timestamp,
                   predicted_value_timestamp,
                   predicted_value_timestamp],
                  [predicted_glucose_value - glucose_error_value,
                   predicted_glucose_value,
                   predicted_glucose_value + glucose_error_value],
                  'p-')
        plot.plot(predicted_value_timestamp,
                   predicted_glucose_value,
                  'r*')
        ax = image.gca()
        ax.xaxis.set_major_locator(ticker.MultipleLocator(4))
        ax.tick_params(axis='x', labelrotation=90)
        buffer = BytesIO()
        image.savefig(buffer, format="png")
        result_plot = base64.b64encode(buffer.getbuffer()).decode("ascii")

    return jsonify({
        'current_time': current_time.strftime("%d-%m-%Y %H:%M:%S"),
        'current_glucose_value': current_glucose_value,
        'predicted_glucose_value': str(predicted_glucose_value) + " ± " + str(glucose_error_value),
        'plot': f"<img class='edge' src='data:image/png;base64,{result_plot}'/>",
        'recommendation': "-"
    })
