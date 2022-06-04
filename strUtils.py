'''
  Функция получает на вход строку data
  и проверяет её на наличие запрещённых
  символов.
'''
def check_invalid_char(data):
  excluded_chars = " *?!'^+%&;/()=}][{$#"
  for char in data:
    if char in excluded_chars:
      return True
  return False

