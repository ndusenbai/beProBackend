class VersionAlreadyExists(Exception):
    def __init__(self):
        self.txt = 'Данный пользователь уже сдавал вариант этого теста'

    def __str__(self):
        return self.txt


class TestAlreadyFinished(Exception):
    def __init__(self):
        self.txt = 'Компания с таким названием уже существует'

    def __str__(self):
        return self.txt
