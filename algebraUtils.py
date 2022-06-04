import numpy as np  # импорт библиотеки NumPy

'''
 Функция принимаает вещественное значение value
 и проверяет, является ли оно положительным
'''


def positive_glucose_value(value):
  if value > 0.0:
    return True
  else:
    return False


'''
 Функция принимает спрогнозированное значение
 result и вычисляет допустимую погрешность.
'''


def count_glucose_error(result):
  if result < 5.55:
    error = 0.83
  else:
    error = result * 0.15
  return error


'''
 Функция принимает список data и преобразует
 его в двумерный в список, где
'''


def make_pred_data(data):
  pred_data = []
  indices = range(0, 128)
  pred_data.append(data[indices, 0])
  return pred_data


'''
 Функция принимает список data и преобразует
 его в трёхмерный тензор NumPy
'''


def make_3D_tensor(data):
  # Преобразование списка в NumPy массив.
  numpyArray = np.array(data)

  # Преобразование массива в трехмерный тензор.
  resultTensor = np.reshape(numpyArray,  # массив на изменение
                            (numpyArray.shape[0],  # кол-во записей
                             numpyArray.shape[1],  # кол-во временных шагов
                             1))  # т.к. имеем только 1 столбец с уровнями

  return resultTensor


'''
 Функция принимает список list
 и преобразует его в массив NumPy
'''


def make_numpy_array_from_list(list):
  return np.array(list)
