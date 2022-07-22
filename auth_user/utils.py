class UserAlreadyExists(Exception):
    def __init__(self):
        self.txt = 'Пользователь с данной электронной почтой уже зарегистрирован в системе'

    def __str__(self):
        return self.txt
