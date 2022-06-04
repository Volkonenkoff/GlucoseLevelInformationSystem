
'''
 Функция принимает предсказанное значение уровня глюкозы
 и расчитанную допустимую погрешность и вырабатывает
 рекомендацию для пользователя.
'''

def make_recommendation(predicted_glucose_value, value_error):
  result = ""
  high_border = predicted_glucose_value + value_error
  low_border = predicted_glucose_value - value_error
  if not check_high_normal(predicted_glucose_value) \
      or not check_low_normal(predicted_glucose_value):
    if not check_high_normal(predicted_glucose_value):
      result = "Прогнозируется высокий уровень глюкозы через час. " \
               "Возможно необходима инсулинотерапия."
    if not check_low_normal(predicted_glucose_value):
      result = "Прогнозируется низкий уровень глюкозы через час. " \
               "Возможно необходим приём углеводов."
  else:
    if check_high_normal(high_border) and check_low_normal(high_border) \
        and check_high_normal(low_border) and check_low_normal(low_border):
      result = "Ожидается нормальный уровень сахара. "
    if not check_high_normal(high_border):
      result = "Верхний порог погрешности ожидаемого" \
               " уровня глюкозы превышает рекомендуемый уровень. " \
               "Возможно необходима инсулинотерапия."
    if not check_low_normal(high_border):
      result = "Верхний порог погрешности ожидаемого " \
               "уровня глюкозы ниже рекомендуемого уровня. " \
               "Необходимо принять углеводы."
    if not check_high_normal(low_border):
      result = "Нижний порог погрешности ожидаемого " \
               "уровня глюкозы выше рекомендуемого уровня. " \
               "Необходима инсулинотерапия."
    if not check_low_normal(low_border):
      result = "Нижний порог погрешности ожидаемого " \
               "уровня глюкозы ниже рекомендуемого уровня. " \
               "Возможно следует принять углеводы."

  return result


'''
 Функция принимает значение уровня глюкозы
 и проверяет, не выходит ли оно за допустимые
 пределы. В данном случае нижний.
'''


def check_low_normal(glucose_value):
  if glucose_value < 4.4:
    return False
  return True


'''
 Функция принимает значение уровня глюкозы
 и проверяет, не выходит ли оно за допустимые
 пределы. В данном случае верхний.
'''


def check_high_normal(glucose_value):
  if glucose_value > 7.2:
    return False
  return True
