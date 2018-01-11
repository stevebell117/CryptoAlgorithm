import datetime as dt
from enum import Enum

class Order(object):
    def __init__(self, order_id, side = 'sell', size = 0, price = 0, previous_amount = 0):
        self.side = side
        self.price = price
        self.size = size
        self.fill_fees = 0
        self.done_reason = 'open'
        self.time = dt.datetime.now()
        self.previous_amount = previous_amount
        self.order_id = order_id
        self.status = OrderStatus.OPEN

class Orders(Order):
    def __init__(self):
        self.OrdersList = list()

    def add_order(self, order):
        self.OrdersList.append(order)

    def remove_order(self, order_id = None, order = None):
        if order_id != None:
            index = next(x.order_id == order_id for x in self.OrdersList)
            self.OrdersList.pop(index)
        elif order != None:
            self.OrdersList.remove(order)
        else:
            print('An order must be entered. Order removal failed @ {0}'.format(dt.datetime.now()))

    def update_order(self, order_id, size = None, status = None, done_reason = None, fill_fees = None):
        index = next(x.order_id == order_id for x in self.OrdersList)
        print('Index {0}'.format(index))
        if index >= 0:
            order = self.OrdersList[index]
            if size != None:
                order.size = size
            if status != None:
                order.status = status
            if done_reason != None:
                order.done_reason = done_reason
            if fill_fees != None:
                order.fill_fees = fill_fees
            self.OrdersList[index] = order #This is probably redundant, but I have no clue if Python does pointers...

    def get_orders(self):
        return self.OrdersList

    def get_order_by_id(self, order_id):
        index = next(x.order_id == order_id for x in self.OrdersList)
        return self.OrdersList[index]

class OrderStatus(Enum):
    OPEN = 0
    CLOSED = 1
    FILLED = 2