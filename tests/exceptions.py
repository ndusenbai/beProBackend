class VersionAlreadyExists(Exception):
    def __init__(self):
        self.txt = 'Данный пользователь уже сдавал вариант этого теста'

    def __str__(self):
        return self.txt


class TestAlreadyFinished(Exception):
    def __init__(self):
        self.txt = 'Тест уже пройден и не может быть сдан повторно'

    def __str__(self):
        return self.txt


class NoEmailTestException(Exception):
    def __init__(self):
        self.txt = 'Невозможно отправить приглашение, т.к. не указана электронная почта'

    def __str__(self):
        return self.txt


class TestAlreadyFinishedEmailException(Exception):
    def __init__(self):
        self.txt = 'Невозможно отправить приглашение, т.к. тест уже пройден'

    def __str__(self):
        return self.txt


class NoPaidTestException(Exception):
    def __init__(self):
        self.txt = 'Необходимо сначала оплатить тест'

    def __str__(self):
        return self.txt
