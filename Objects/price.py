import datetime

class Price:
    def __init__(self):
        self.amount = 0
        self.date_and_time = datetime.datetime.now()  

    def __repr__(self):
        return '{0} - {1}'.format(self.amount, self.date_and_time)