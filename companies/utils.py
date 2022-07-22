class CompanyAlreadyExists(Exception):
    def __init__(self):
        self.txt = 'Компания с таким названием уже существует'

    def __str__(self):
        return self.txt


class WrongAddress(Exception):
    def __init__(self):
        self.txt = 'Введите правильный адрес'

    def __str__(self):
        return self.txt
