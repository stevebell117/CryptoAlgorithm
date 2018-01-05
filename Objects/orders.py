import datetime as dt
from enum import Enum

class Order(object):
    def __init__(self, order_id, side = 'sell', size = 0, time = dt.datetime.now()):
        self.side = side
        self.size = size
        self.time = time
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

    def update_order(self, order_id, size = None, status = None):
        index = next(x.order_id == order_id for x in self.OrdersList)
        order = self.OrdersList[index]
        if size != None:
            order.size = size
        if status != None:
            order.status = status
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