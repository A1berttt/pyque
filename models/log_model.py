import logging
import os

logName = "log.log"
isExist = os.path.exists(logName)
if isExist:
    os.remove(logName)

class TheLogger:
    def __init__(self, user):
        self.logger = logging.getLogger(user)
        self.logger.setLevel(logging.INFO)
        self.fh = logging.FileHandler(logName)
        self.fh.setLevel(logging.INFO)
        self.formartter = logging.Formatter('%(asctime)s - ClassName: %(name)s - Operation: %(message)s')
        self.fh.setFormatter(self.formartter)
        self.logger.addHandler(self.fh)