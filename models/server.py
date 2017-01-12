import logging
from .log_model import TheLogger  # modified by lee on 1/4/2017
import simpy
from numpy import random

from .unit import Pdu
from .channel import ErrorChannel, Channel


class BaseServer():
    '''the base server model, associated with a transmission channel,
    do the serve process according to the channel capacity
    '''
    def __init__(self, env, queue):
        super(BaseServer, self).__init__()
        assert isinstance(env, simpy.Environment)
        self.__env = env
        self.__queue = queue
        self.__channel = None
        self.action = self.__env.process(self.run())
        self.log = TheLogger(self.__class__.__name__)       # modified by lee on 1/4/2017

    def get_channel(self):
        return self.__channel

    def set_channel(self, channel):
        assert isinstance(channel, Channel)
        self.__channel = channel
    channel = property(
        get_channel, set_channel, None, 'the associated channel model')

    def get_serve_size(self):
        return self.__channel.get_available()

    def serve(self, serve_pdu):
        assert isinstance(serve_pdu, Pdu)
        service_time, error = self.__channel.do_serve(serve_pdu)
        serve_pdu.on_serve_begin()
        print("server start to serve pdu at : {0:f}".format(self.__env.now))        # {0:d} --> {0:f} by chengjiyu on 2016/9/23
        self.log.logger.info("server start to serve pdu at : {0:f}".format(self.__env.now))      # modified by lee on 1/4/2017
        yield self.__env.process(self.do_serve(service_time))

        print("server finish serving pdu at : {0:f}".format(self.__env.now))        # {0:d} --> {0:f} by chengjiyu on 2016/9/23
        self.log.logger.info("server finish serving pdu at : {0:f}".format(self.__env.now))      # modified by lee on 1/4/2017
        dice = random.random()
        # add timeout by chengjiyu on 2016/10/8
        rtt = service_time
        if rtt < 4:
            if error:
                serve_pdu.on_dropped()
            else:
                serve_pdu.on_serve_end()
        else:
            serve_pdu.on_timeout()

    def do_serve(self, duration):
        yield(self.__env.timeout(duration))

    def run(self):
        while True:
            serve_pdu = self.__queue.get_pdu(self.get_serve_size())
            print("serve pdu")
            self.log.logger.info("serve pdu")      # modified by lee on 1/4/2017
            if serve_pdu is None:
                yield self.__env.timeout(1)
            else:
                yield self.__env.process(self.serve(serve_pdu))     # add yield self.__env.process() by chengjiyu on 2016/9/19