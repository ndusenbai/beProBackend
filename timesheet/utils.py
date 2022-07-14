class EmployeeTooFarFromDepartment(Exception):
    def __init__(self):
        self.txt = 'Too far from department'

    def __str__(self):
        return self.txt


class FillUserStatistic(Exception):
    def __init__(self):
        self.txt = 'Fill user statistic'

    def __str__(self):
        return self.txt
