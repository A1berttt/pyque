import logging
from .log_model import TheLogger        # modified by lee on 1/4/2017
import simpy
import numpy as np


class BaseSourceModel():
    '''The Base class for source model,
    ------------methods---------------
    get_pkt_num() : return a int that represents the amount of packets that the source generated
    get_interval() : return a float that represents the interval for the next message
    on_served() : decorator for feedback on the successful delivering
    on_dropped() : decorator for feedback on the fail delivering
    '''
    def __init__(self):
        self.log = TheLogger(self.__class__.__name__)  # modified by lee on 1/4/2017

    def get_pkt_num(self):
        return 1

    def get_interval(self):
        return 1.

    def on_served(self):
        print('The source received feedback for successful delivering')
        self.log.logger.info('The source received feedback for successful delivering')     # modified by lee on 1/4/2017

    def on_droped(self):
        print('The source received feedback for transmission failure')
        self.log.logger.info('The source received feedback for transmission failure')      # modified by lee on 1/4/2017

class MMPPModel(BaseSourceModel):
    '''The Markov Modulated Poisson Process Source Model'''

    def __init__(self, Q, Lambda):
        assert(len(np.shape(Q)) is 2)
        assert(len(np.shape(Lambda)) is 1)
        assert(np.shape(Q)[0] == np.shape(Q)[1])
        assert(np.shape(Q)[0] == len(Lambda))
        self.__Q = np.atleast_2d(Q)
        self.__state_transition = np.cumsum(self.__Q, axis = 1)
        self.__Lambda = np.atleast_1d(Lambda)
        self.__states = np.array([i for i in range(Lambda.shape[0])])
        self.__cur_state = np.random.randint(0, self.__states[-1])      # self.__states=[0,1,2,3]; self.__cur_state=[0,1,2]
        self.__init_cwnd = 1
        self.__init_ssth = 65535
        self.__cwnd = 1400
        self.__ssth = 65535
        self.__accumulator = 0
        self.__segment = 1400       # add segment size by chengjiyu on 2016/10/9
        self.log = TheLogger(self.__class__.__name__)  # modified by lee on 1/4/2017

    def get_interval(self):
        state = self.__states[self.__cur_state]
        rate = self.__Lambda[state]
        dice = np.random.random()
        self.__cur_state = np.argwhere(self.__state_transition[self.__cur_state] > dice)[0][0]
        # Find the indices of array elements that are non-zero, grouped by element.
        # return position of the first meet specified condition
        return np.random.exponential(1./ rate) / rate

    @property
    def cur_state(self):
        return self.__cur_state

    @property
    def Q(self):
        return self.__Q

    # add tcp by chengjiyu on 2016/10/8
    def on_served(self):
        print('The source received feedback for successful delivering')
        self.log.logger.info('The source received feedback for successful delivering')     # modified by lee on 1/4/2017
        if self.__cwnd <= self.__ssth:
            self.__cwnd += self.__segment
            print("Acked in Slow Start Phase")
            print("cwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
            self.log.logger.info("Acked in Slow Start Phase")      # modified by lee on 1/4/2017
            self.log.logger.info("cwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
        else:
            print("Acked in Congestion avoidance")
            self.log.logger.info("Acked in Congestion avoidance")       # modified by lee on 1/4/2017
            adder = self.__segment * self.__segment / self.__cwnd
            adder = int(max(1.0, adder))
            # self.__accumulator += 1
            # if self.__accumulator == self.__cwnd:
            # self.__cwnd += 1
            # self.__accumulator = 0
            self.__cwnd += adder
            print("cwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
            self.log.logger.info("cwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))       # modified by lee on 1/4/2017

    def on_droped(self):
        print('The source received feedback for transmission failure')
        self.log.logger.info('The source received feedback for transmission failure')      # modified by lee on 1/4/2017
        self.__ssth = max(2 * self.__segment, self.__cwnd / 2)
        self.__cwnd = self.__ssth + 3 * self.__segment
        # self.__cwnd = max(self.__cwnd / 2, 1)
        # self.__ssth = max(self.__cwnd, 2)
        print("duplicate acks \ncwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
        self.log.logger.info("duplicate acks \ncwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))     # modified by lee on 1/4/2017

    def on_timeout(self):
        # self.__ssth = max(self.__cwnd / 2, 2)
        # self.__cwnd = 0
        self.__ssth = max(2 * self.__segment, self.__cwnd / 2)
        self.__cwnd = self.__segment
        print("time out \ncwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
        self.log.logger.info("time out \ncwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))       # modified by lee on 1/4/2017


class TcpSourceModel(BaseSourceModel):
    '''The emulated TCP source model'''

    def __init__(self, rtt):
        self.__rtt = rtt
        self.segsize = 1440
        self.__cwnd = 1
        self.__ssth = 0xffff
        self.__acked = 0
        self.__cum = 0
        self.log = TheLogger(self.__class__.__name__)  # modified by lee on 1/4/2017

    @property
    def cwnd(self):
        return self.__cwnd

    @property
    def ssth(self):
        return self.__ssth

    def  get_interval(self):
        rate = self.segsize * self.__cwnd / self.__rtt      # ????
        return np.random.exponential(1. / rate) / rate

    def on_served(self):
        if self.__cwnd < self.__ssth:
            self.__cwnd += 1
            print("Acked in Slow Start Phase")
            print("cwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
            self.log.logger.info("Acked in Slow Start Phase")       # modified by lee on 1/4/2017
            self.log.logger.info("cwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))      # modified by lee on 1/4/2017
        else:
            print("Acked in Congestion avoidance")
            self.log.logger.info("Acked in Congestion avoidance")      # modified by lee on 1/4/2017
            self.__cum += 1
            if self.__cum == self.__cwnd:
                self.__cwnd += 1
                self.__cum = 0
            print("cwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
            self.log.logger.info("cwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))      # modified by lee on 1/4/2017

    # add duplicate acks by chengjiyu on 2016/9/28
    def on_droped(self):
        self.__cwnd = max(self.__cwnd / 2, 1)
        self.__ssth = max(self.__cwnd, 2)
        print("duplicate acks \ncwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))
        self.log.logger.info("duplicate acks \ncwnd is {0}, ssth is {1}".format(self.__cwnd, self.__ssth))     # modified by lee on 1/4/2017