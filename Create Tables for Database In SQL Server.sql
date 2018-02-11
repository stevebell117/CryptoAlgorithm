IF EXISTS(SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = N'Orders') BEGIN DROP TABLE Orders END
IF EXISTS(SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = N'Orders_status') BEGIN DROP TABLE Orders_Status END

CREATE TABLE Orders_Status
(
	id int default 0 PRIMARY KEY,
	value nvarchar(50) NOT NULL unique
);

GO

CREATE TABLE Orders
(
	id uniqueidentifier default newid() PRIMARY KEY,
	side nvarchar(5) NOT NULL,
	size decimal(32, 8) NOT NULL,
	price decimal(32, 8) NOT NULL,
	fill_fees decimal(32, 8) default 0,
	done_reason nvarchar(MAX) NOT NULL,
	time datetime NOT NULL,
	previous_amount decimal(32, 8) NOT NULL,
	order_id nvarchar(MAX) NOT NULL,
	status int FOREIGN KEY REFERENCES Orders_Status(id),
	balanced bit,
	product nvarchar(MAX)
);

insert into Orders_Status
(id, [value])
VALUES
(0, 'Open'),
(1, 'Closed'),
(2, 'Filled'),
(3, 'Cancelled'),
(4, 'Rejected'),
(5, 'Override')

insert into Orders
(side, size, price,done_reason, time, previous_amount, order_id, status, balanced, product)
VALUES
('sell', .002, 8199.99, 'TEST', GETDATE(), 8200.01, 'fake', 1, 0, 'BTC-USD')

select * from Orders where status = 1 order by time desc