from enum import Enum
import datetime as dt

class LogType(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2

class Log():
    def __init__(self):
        self.type = None
        self.message = ''
        self.additional_message = ''
        self.location = ''   
        self.time = dt.datetime.now()   

class Logs(object):    
    def __init__(self):
        self._logs = list()

    def get_logs(self):
        return self._logs

    def get_last_log(self):
        return self._logs[-1]

    def get_first_log(self):
        return self._logs[0]

    def info(self, message = '', location = '', additional_message = '', db_object = None):
        log = Log()
        log.type = LogType.INFO
        log.additional_message = additional_message
        log.message = message
        log.location = location
        self._logs.append(log)
        if db_object is not None:
            db_object.write_log_to_database(log)
        return log

    def warning(self, message = '', location = '', additional_message = '', db_object = None):
        log = Log()
        log.type = LogType.WARNING
        log.additional_message = additional_message
        log.message = message
        log.location = location
        self._logs.append(log)
        if db_object is not None:
            db_object.write_log_to_database(log)
        return log

    def error(self, message = '', location = '', additional_message = '', db_object = None):
        log = Log()
        log.type = LogType.ERROR
        log.additional_message = additional_message
        log.message = message
        log.location = location
        self._logs.append(log)
        if db_object is not None:
            db_object.write_log_to_database(log)
        return log

        