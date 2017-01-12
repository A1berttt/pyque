import logging
from .log_model import TheLogger                # modified by lee on 1/4/2017
from .unit import Packet

class TcpReno():
    __doc__ = """
    The TcpReno class emulates the cwnd evolution.
    Based on the TCP NewReno cwnd evolution.
    On Slow Start phase, the cwnd increase by 1 for every ack
    On Congesion Avoidance phase, the cwnd is increas by 1/cwnd for every ack
    On duplicate acks, the cwnd decrease to cwnd/2
    On timeout, the cwnd is set to 0
    Once recover from timeout, the cwnd is set to init_cwnd
    """

    def __init__(self):
        self.__init_cwnd = 1
        self.__init_ssth = 65535
        self.__cwnd = 1400
        self.__ssth = 65535
        self.__accumulator = 0
        self.__segment = 1400       # add segment size by chengjiyu on 2016/10/9
        self.log = TheLogger(self.__class__.__name__)       # modified by lee on 1/4/2017

    def on_ack(self, func):
        def wrapper(self):
            if self.__cwnd <= self.__ssth:
                self.__cwnd += self.__segment
                print("Acked in Slow Start Phase")              # modified by lee on 1/4/2017
                print("cwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
                self.log.logger.info("Acked in Slow Start Phase")
                self.log.logger.info("cwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
            else:
                print("Acked in Congestion avoidance")              # modified by lee on 1/4/2017
                self.log.logger.info("Acked in Congestion avoidance")
                adder = self.__segment * self.__segment / self.__cwnd
                adder = int(max(1.0, adder))
                # self.__accumulator += 1
                # if self.__accumulator == self.__cwnd:
                    # self.__cwnd += 1
                    # self.__accumulator = 0
                self.__cwnd += adder
                print("cwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))                # modified by lee on 1/4/2017
                self.log.logger.info("cwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
            func()
        return wrapper

    def on_dupack(self, func):
        def wrapper(self):
            self.__ssth = max(2 * self.__segment, self.__cwnd / 2)
            self.__cwnd = self.__ssth + 3 * self.__segment
            # self.__cwnd = max(self.__cwnd / 2, 1)
            # self.__ssth = max(self.__cwnd, 2)
            print("duplicate acks \ncwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
            func()
        return wrapper

    def on_timeout(self, func):
        def wrapper(self):
            # self.__ssth = max(self.__cwnd / 2, 2)
            # self.__cwnd = 0
            self.__ssth = max(2 * self.__segment, self.__cwnd / 2)
            self.__cwnd = self.__segment
            print("time out \ncwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
            func()
        return wrapper


