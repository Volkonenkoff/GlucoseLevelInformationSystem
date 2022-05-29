import numpy as np


def positive_glucose_value(value):
    if value > 0.0:
        return True
    else:
        return False


def count_glucose_error(result):
    if result < 5.55:
        error = 0.83
    else:
        error = result * 0.15
    return error

def make_pred_data(data):
    pred_data = []
    indices = range(0,128)
    pred_data.append(data[indices, 0])
    return pred_data

def make_3D_tensor(data):
    # Преобразование списка в NumPy массив.
    numpyArray = np.array(data)

    # Преобразование массива в трехмерный тензор.
    resultTensor = np.reshape(numpyArray,  # массив на изменение
                              (numpyArray.shape[0],  # кол-во записей
                               numpyArray.shape[1],  # кол-во временных шагов
                               1))  # т.к. имеем только 1 столбец с уровнями

    return resultTensor

def make_numpy_array_from_list(list):
    return np.array(list)