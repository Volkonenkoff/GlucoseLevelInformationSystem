from app import login_manager
from flask_login import UserMixin
from sqlalchemy import MetaData, \
  create_engine, \
  Column, \
  Integer, \
  String, \
  ForeignKey, \
  Float, \
  desc
from sqlalchemy.orm import \
  declarative_base, \
  sessionmaker, \
  relationship
from werkzeug.security import \
  generate_password_hash, \
  check_password_hash
from threading import Lock

mutex = Lock()
mutex.acquire()
metadata = MetaData()
engine = create_engine('sqlite:///usersDB.sqlite',
                       connect_args={'check_same_thread': False},
                       echo=False)
Base = declarative_base()
db_session = sessionmaker(bind=engine)()
mutex.release()

'''
    КЛАСС ПОЛЬЗОВАТЕЛЬ (User):
    
    Используется для работы с таблицой ПОЛЬЗОВАТЕЛЬ.
    Наследует классы Base, UserMixin.
    
    *Поле __tablename__ - имя таблицы.
    *Поле user_id - ID пользователя.
    *Поле firstname - имя пользователя.
    *Поле lastname - фамилия пользователя.
    *Поле middlename - отчество пользователя. 
    *Поле date_of_birth - дата рождения пользователя.
    *Поле email - электронная почта пользователя.
    *Поле password_hash - хэш пароля.
    *Поле measurements - для установления связи
    один-ко-многим между таблицей User и таблицей
    Measurement.
'''


class User(Base, UserMixin):
  __tablename__ = 'user'
  user_id = Column(Integer(),  # Целочисленное значение
                   primary_key=True,  # Первичный ключ
                   unique=True,  # Уникальное значение
                   autoincrement=True)  # Автоинкремент
  firstname = Column(String(100),  # Строка не более 100 символов.
                     nullable=False)  # Не должна быть пустой.
  lastname = Column(String(100),  # Строка не более 100 символов.
                    nullable=False)  # Не должна быть пустой.
  middlename = Column(String(100))  # Строка не более 100 символов.
  date_of_birth = Column(String(10),  # Строка не более 10 символов.
                         nullable=False)  # Не должна быть пустой.
  email = Column(String(145),  # Строка не более 145 символов.
                 nullable=False,  # Не должна быть пустой.
                 unique=True)  # Уникальна, т.к. по сути это логин.
  password_hash = Column(String(100),  # Строка не более 100 символов.
                         nullable=False)  # Не должна быь пустой.
  measurements = relationship('Measurement',  # С чем связываеся.
                              backref='user')  # Обратная ссылка к таблице.

  def __repr__(self):
    return "<{}:{}>".format(self.user_id, self.email)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def get_id(self):
    return self.user_id


@login_manager.user_loader  # аннотация для подгрузки по
def load_user(user_id):
  result = db_session. \
    query(User). \
    get(user_id)
  return result


def find_user(email):
  result = db_session. \
    query(User). \
    filter(User.email == email).first()
  return result


'''
    КЛАСС ИЗМЕРЕНИЕ (Measurement):
    
    Используется для работы с таблицой ИЗМЕРЕНИЕ.
    Наследует классы Base.
    
    *Поле __tablename__ - имя таблицы.
    *Поле measurement_id - ID измерения.
    *Поле measurement_user - внешний ключ, относится
    к ID пользователя, необоходим для установки связи
    один-ко-многим.
    *Поле timestamp - временная метка измерения.
    *Поле glucose_value - значение уровня глюкозы в
    момент времени timestamp. 
'''


class Measurement(Base):
  __tablename__ = 'measurement'
  measurement_id = Column(Integer(),
                          primary_key=True,
                          autoincrement=True)
  measurement_user = Column(Integer(),
                            ForeignKey('user.user_id'))
  timestamp = Column(Integer())
  glucose_value = Column(Float())


def get_time_series_data(user_id):
  result = db_session.query(Measurement). \
    filter(Measurement.measurement_user == user_id). \
    order_by(desc(Measurement.timestamp)). \
    limit(128).all()
  return result


def get_history(user_id):
  result = db_session.query(Measurement). \
    filter(Measurement.measurement_user == user_id). \
    order_by(desc(Measurement.timestamp)). \
    all()
  return result


def get_last_measurement(user_id):
  result = db_session.query(Measurement). \
    filter(Measurement.measurement_user == user_id). \
    order_by(desc(Measurement.timestamp)). \
    first()
  return result


def add_data(entry):
  mutex.acquire()
  db_session.add(entry)
  db_session.commit()
  mutex.release()
