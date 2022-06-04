from threading import Lock

from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from algebraUtils import make_3D_tensor, \
  make_pred_data, \
  make_numpy_array_from_list


class ModelConnector:
  def __init__(self, path):
    try:
      self.mutex = Lock()
      self.model = load_model(path)
      self.scaler = MinMaxScaler(feature_range=(0, 1))
    except IOError:
      print("Произошла ошибка: Выбран неверный файл")
    except ImportError:
      print("Произошла ошибка: Загрузка недоступна")

  def make_prediction(self, data):
    data_array = make_numpy_array_from_list(data)
    data_array = data_array.reshape(-1, 1)
    scaled_data = self.scaler.fit_transform(data_array)
    listed_data = make_pred_data(scaled_data)
    tensor_data = make_3D_tensor(listed_data)
    self.mutex.acquire()
    prediction = self.model.predict(tensor_data)
    self.mutex.release()
    results = self.scaler.inverse_transform(prediction)
    return results

