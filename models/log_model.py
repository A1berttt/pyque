import logging
import os

logName = "log"
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

        # 对handlers进行判断，防止重复添加handler
        if not self.logger.handlers:
            self.logger.addHandler(self.fh)