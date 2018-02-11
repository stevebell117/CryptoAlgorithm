import pyodbc
from Objects.orders import Order
from Objects.orders import OrderStatus

class Database():
    def __init__(self):
        self.conn = pyodbc.connect(driver='{SQL Server}', SERVER=r'STEVEN-PC\STEVEDB', DATABASE='Trades')

    def insert_order_into_database(self, order):
        cursor = self.conn.cursor()
        cursor.execute('insert into Orders(side, price, size, fill_fees, done_reason, time, previous_amount, order_id, status, balanced) values ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}'
                            .format(order.side, order.price, order.size, order.fill_fees, order.done_reason, order.time, order.previous_amount, order.order_id, order.status, order.balanced))
        self.conn.commit()

    def update_order_in_database(self, order):
        cursor = self.conn.cursor()
        cursor.execute('update Orders SET price = {0}, size = {1}, fill_fees = {2}, done_reason = {3}, previous_amount = {4}, status = {5}, balanced = {6} where order_id = \'{7}\''
                            .format(order.price, order.size, order.fill_fees, order.done_reason, order.previous_amount, order.status, order.balanced, order.order_id))
        self.conn.commit()

    def remove_order_from_database(self, order):
        cursor = self.conn.cursor()
        cursor.execute('delete from Orders where order_id = \'{0}\''
                            .format(order.order_id))
        self.conn.commit()

    def populate_most_recent_order_from_database(self, order_book):
        cursor = self.conn.cursor()
        cursor.execute('select top 1 * from Orders order by time desc')
        row = cursor.fetchone()
        if row:
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
            order = Order(row[8], row[1], row[2], row[3], row[7], order_status)
            order_book.Orders.add_order(order)
            order_book.Orders.update_order(order=order, fill_fees=float(row[4]), done_reason=row[5], balanced=bool(row[9]))

    #generic, but whatever
    def execute_command_in_database(self, command):
        cursor = self.conn.cursor()
        cursor.execute(command)
        self.conn.commit()

