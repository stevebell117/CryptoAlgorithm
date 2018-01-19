from enum import Enum
import datetime as dt

class Logs(object):    
    class LogType(Enum):
        INFO = 0
        WARNING = 1
        ERROR = 2

    class Log():
        def __init__(self):
            self.type = None
            self.message = ''
            self.location = ''   
            self.time = dt.datetime.now()         

    def __init__(self):
        self._logs = list()

    def get_logs(self):
        return self._logs

    def get_last_log(self):
        return self._logs[-1]

    def get_first_log(self):
        return self._logs[0]

    def info(self, message = '', location = ''):
        log = self.Log()
        log.type = self.LogType.INFO
        log.message = message
        log.location = location
        self._logs.append(log)

    def warning(self, message = '', location = ''):
        log = self.Log()
        log.type = self.LogType.WARNING
        log.message = message
        log.location = location
        self._logs.append(log)

    def error(self, message = '', location = ''):
        log = self.Log()
        log.type = self.LogType.ERROR
        log.message = message
        log.location = location
        self._logs.append(log)

        