import datetime as dt
from enum import Enum

class OrderStatus(Enum):
    OPEN = 0
    CLOSED = 1
    FILLED = 2
    CANCELLED = 3
    REJECTED = 4
    OVERRIDE = 5

class Order(object):
    def __init__(self, order_id, side = 'sell', size = 0, price = 0, previous_amount = 0, status = OrderStatus.OPEN):
        self.side = side
        self.price = price
        self.size = size
        self.fill_fees = 0
        self.done_reason = 'open'
        self.time = dt.datetime.now()
        self.previous_amount = previous_amount
        self.order_id = order_id
        self.status = status
        self.balanced = False
        self.balanced_order = None

class Orders(Order):
    def __init__(self):
        self.OrdersList = list()

    def add_order(self, order):
        self.OrdersList.append(order)

    def remove_order(self, order_id = None, order = None):
        if order_id != None:
            order_found = next(x.order_id == order_id for x in self.OrdersList)
            self.OrdersList.remove(order_found)
        elif order != None:
            self.OrdersList.remove(order)
        else:
            print('An order must be entered. Order removal failed @ {0}'.format(dt.datetime.now()))

    def get_last_order(self):
        if self.OrdersList:
            return self.OrdersList[-1]
        return None

    def update_order(self, order_id = None, order = None, size = None, status = None, done_reason = None, fill_fees = None, time = None, balanced = None):
        if order is None: 
            use_order = self.get_order_by_id(order_id)
        else: 
            use_order = order
        if use_order is not None:
            if size is not None:
                use_order.size = size
            if status is not None:
                use_order.status = status
            if done_reason is not None:
                use_order.done_reason = done_reason
            if fill_fees is not None:
                use_order.fill_fees = fill_fees
            if balanced is not None:
                use_order.balanced = balanced
            if time is not None:
                use_order.time = time

    def get_orders(self):
        return self.OrdersList

    def get_order_by_id(self, order_id):
        order = next((x for x in self.OrdersList if x.order_id == order_id), None)
        return order
