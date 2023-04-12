class EmployeeTooFarFromDepartment(Exception):
    def __init__(self):
        self.txt = 'Вы не находитесь в радиусе вашего отдела'

    def __str__(self):
        return self.txt


class FillUserStatistic(Exception):
    def __init__(self):
        self.txt = 'Заполните статистику'

    def __str__(self):
        return self.txt


class CheckInAlreadyExistsException(Exception):
    def __init__(self):
        self.txt = 'Сначала сделайте check out'

    def __str__(self):
        return self.txt


class TooEarlyCheckoutException(Exception):
    def __init__(self):
        self.txt = "Еще рано до check out"

    def __str__(self):
        return self.txt