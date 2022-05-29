from flask_wtf import FlaskForm
from wtforms import StringField, \
    SubmitField, \
    BooleanField, \
    PasswordField, \
    DateField, \
    FloatField
from wtforms.validators import DataRequired, \
    EqualTo, \
    Length, \
    Email, \
    ValidationError
from strUtils import \
    check_invalid_char
from usersDB import \
    find_user
from algebraUtils import \
    positive_glucose_value


class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit_button = SubmitField("Войти")

    def validate_password(self, password):
        if check_invalid_char(self.password.data):
            raise ValidationError("Поле содержит пробел или "
                                  "следующие запрещенные символы "
                                  "*?!'^+%&/()=}][{$#")
        user = find_user(self.email.data)
        if user is None:
            raise ValidationError("Пользователя с таким email не существует")
        if user:
            if not user.check_password(self.password.data):
                raise ValidationError("Пароль неверный")
        return True


class RegistrationForm(FlaskForm):
    firstname = StringField("Введите имя",
                            validators=[DataRequired(message="*Необходимо указать имя")])
    lastname = StringField("Введите фамилию",
                           validators=[DataRequired(message="*Необходимо указать фамилию")])
    middlename = StringField("Введите отчество (при наличии)")
    date_of_birth = DateField("Дата рождения", format='%Y-%m-%d',
                              validators=[DataRequired(message="*Необходимо указать дату рождения")])
    email = StringField("E-mail",
                        validators=[DataRequired(message="*Необходимо указать почту"),
                                    Email(),
                                    Length(max=145)])
    password = PasswordField("Пароль",
                             validators=[DataRequired(message="*Необходимо указать пароль"),
                                         Length(min=10,
                                                message='Пароль должен быть минимум из %(min)d символов')])
    confirm_password = PasswordField(
        "Подтвердите пароль",
        validators=[DataRequired(message="*Необходимо повторить пароль"),
                    EqualTo("password", message="Пароли должны совпадать!")])
    submit_button = SubmitField("Подтвердить")

    def validate_password(self, password):
        if check_invalid_char(self.password.data):
            raise ValidationError("Пароль содержит пробел или "
                                  "следующие запрещенные символы "
                                  "*?!'^+%&;/()=}][{$#")
        return True

    def validate_firstname(self, firstname):

        if check_invalid_char(self.firstname.data):
            raise ValidationError("Имя содержит пробел, латиницу или "
                                  "следующие запрещенные символы "
                                  "*?!'^+%&;/()=}][{$#")
        return True

    def validate_lastname(self, lastname):

        if check_invalid_char(self.lastname.data):
            raise ValidationError("Фамилия содержит пробел, латиницу или "
                                  "следующие запрещенные символы "
                                  "*?!'^+%&;/()=}][{$#")
        return True

    def validate_middlename(self, middlename):

        if check_invalid_char(self.middlename.data):
            raise ValidationError("Отчество содержит пробел, латиницу или "
                                  "следующие запрещенные символы "
                                  "*?!'^+%&;/()=}][{$#")
        return True

    def validate_email(self, email):
        if find_user(self.email.data):
            raise ValidationError("Пользователь с таким e-mail уже существует")

        return True


class ManualInputForm(FlaskForm):
    glucose_value = FloatField("Введите уровнь глюкозы",
                               validators=[DataRequired(message="*Необходимо ввести данные")])
    submit_button = SubmitField("Добавить")

    def validate_glucose_value(self, glucose_value):
        if not positive_glucose_value(self.glucose_value.data):
            raise ValidationError("Значение должно быть положительным")

        return True
