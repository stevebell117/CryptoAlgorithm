select o.*--, os.value 
from Orders o
	join Orders_Status os
	on o.status = os.id
order by time desc

select time, message, additional_message from Logs order by time desc


--select SUM((price - previous_amount) * size) from Orders where status = 1

--TRUNCATE TABLE Logs
