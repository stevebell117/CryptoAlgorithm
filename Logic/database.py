import pyodbc
from Objects.orders import Order
from Objects.orders import OrderStatus
from Objects.log import Log
from datetime import datetime

class Database():
    def __init__(self):
        self.conn = pyodbc.connect(driver='{SQL Server}', SERVER=r'STEVEN-PC\STEVEDB', DATABASE='Trades')
        self._semaphore = False

    def complement_semaphore(self):
        self._semaphore = not self._semaphore

    def insert_order_into_database(self, order):
        while(self._semaphore):
            #do nothing, wait for access
            continue
        self.complement_semaphore()
        try:
            cursor = self.conn.cursor()
            cursor.execute('insert into Orders(side, price, size, fill_fees, done_reason, time, previous_amount, order_id, status, balanced) values (\'{0}\', {1}, {2}, {3}, \'{4}\', ?, {5}, \'{6}\', {7}, {8})'
                                .format(order.side, order.price, order.size, order.fill_fees, order.done_reason, order.previous_amount, order.order_id, order.status.value, '1' if order.balanced else '0'), (order.time))
            self.conn.commit()
        finally:
            self.complement_semaphore()

    def update_order_in_database(self, order):
        while(self._semaphore):
            #do nothing, wait for access
            continue
        try:
            self.complement_semaphore()
            cursor = self.conn.cursor()
            cursor.execute('update Orders SET price = {0}, size = {1}, fill_fees = {2}, done_reason = \'{3}\', previous_amount = {4}, status = {5}, balanced = {6} where order_id = \'{7}\''
                                .format(order.price, order.size, order.fill_fees, order.done_reason, order.previous_amount, order.status.value, '1' if order.balanced else '0', order.order_id))
            self.conn.commit()
        finally:
            self.complement_semaphore()

    def remove_order_from_database(self, order):
        while(self._semaphore):
            #do nothing, wait for access
            continue
        try:
            self.complement_semaphore()
            cursor = self.conn.cursor()
            cursor.execute('delete from Orders where order_id = \'{0}\''
                                .format(order.order_id))
            self.conn.commit()
        finally:
            self.complement_semaphore()

    def populate_most_recent_order_from_database(self, order_book):
        while(self._semaphore):
            #do nothing, wait for access
            continue
        try:
            self.complement_semaphore()
            cursor = self.conn.cursor()
            cursor.execute('select * from Orders where status <> 4 and balanced = 0 and side = \'sell\' order by time')
            rows = cursor.fetchall()
            for row in rows:
                if row[9] == 0: #wtf does Python not have a switch statement
                    order_status = OrderStatus.OPEN
                elif row[9] == 1:
                    order_status = OrderStatus.CLOSED
                elif row[9] == 2:
                    order_status = OrderStatus.FILLED
                elif row[9] == 3:
                    order_status = OrderStatus.CANCELLED
                elif row[9] == 4:
                    order_status = OrderStatus.REJECTED
                else:
                    order_status = OrderStatus.OVERRIDE
                order = Order(row[8], row[1], row[2], float(row[3]), float(row[7]), order_status)
                order_book.Orders.add_order(order)
                order_book.Orders.update_order(order=order, time=datetime.strptime(str(row[6]), '%Y-%m-%d %H:%M:%S.%f'), fill_fees=float(row[4]), done_reason=row[5], balanced=bool(row[10]), finalized=True)
        finally:
            self.complement_semaphore()

    def write_log_to_database(self, log):
        while(self._semaphore):
            #do nothing, wait for access
            continue
        try:
            self.complement_semaphore()
            cursor = self.conn.cursor()
            cursor.execute('insert into Logs(log_type, message, location, additional_message) values (\'{0}\', \'{1}\', \'{2}\', \'{3}\')'.format(log.type.name, str(log.message).replace('\'', ' '), log.location, str(log.additional_message).replace('\'', ' ')))
            self.conn.commit()
        finally:
            self.complement_semaphore()

    #generic, but whatever
    def execute_command_in_database(self, command):
        while(self._semaphore):
            #do nothing, wait for access
            continue
        try:
            self.complement_semaphore()
            cursor = self.conn.cursor()
            cursor.execute(command)
            self.conn.commit()
        finally:
            self.complement_semaphore()

