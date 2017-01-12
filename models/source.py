import logging
import simpy
from numpy import random

from .unit import Message
from .msg_queue import MsgQueue
from .source_model import BaseSourceModel

class BaseSource(object):
    __doc__ = """
    This is Base class for all kinds of source
    the Source class should support the method below
    run() : the main loop that control the message generation and send

    the properties are:
    dst : where the generated massage is sent to
    """

    def __init__(self, env, source_model):  #source_model = mmpp = source_model.MMPPModel(Q, Lambda)
        assert(isinstance(env, simpy.Environment))
        assert(isinstance(source_model, BaseSourceModel))
        self.__env = env
        self.action = self.__env.process(self.run())
        self.__dst = None
        self.__source_model = source_model

    @property
    def dst(self):
        return self.__dst
    @dst.setter
    def dst(self, destination):
        assert(isinstance(destination, MsgQueue))
        self.__dst = destination

    def run(self):
        assert(self.__dst is not None)
        print("source generator start run at %d" % self.__env.now)
        while True:
            interval = self.__source_model.get_interval()
            pkg_num = self.__source_model.get_pkt_num()
            # print('the pkt num is : %f' % (pkg_num))
            msg = Message(self.__env, self.__source_model, pkg_num)
            self.sendto(self.__dst, msg)
            yield self.__env.timeout(interval)

    def sendto(self, dst, msg):
        assert(isinstance(dst, MsgQueue))
        dst.on_arrival(msg)


class PoissonSource(BaseSource):
    """
    source generator in queueing theory
    generates customers as a given process
    default is Possion process with lambda = 1
    """

    def __init__(self, env, **kwargs):
        assert (isinstance(env, simpy.Environment()))
        if 'send_rate' in kwargs:
            self.__send_rate = kwargs['send_rate']
            kwargs.pop('send_rate')
        else:
            self.__send_rate = 1.
        super().__init__(env, **kwargs)
        self.__interval_gen = random.exponential

    @property
    def send_rate(self):
        return self.__send_rate
    @send_rate.setter
    def send_rate(self, val):
        self.__send_rate = float(val)

    def get_interval(self):
        assert(self.__send_rate is not None)
        return self.__interval_gen(scale = 1 / self.__send_rate) / self.__send_rate

    def get_pkg_num(self):
        return 1


class TCPLikeSource(object):
    __doc__ = """
    A TCP like source generator.
    Each time it generate a Massage which contains certain amount of packets.
    The Massage are generated as Poission Process.
    The number of packet in each massage obeys the TCP CWND revolution 
    """

    def __init__(self, env, **kwargs):
        assert(isinstance(env, simpy.Environment))
        if 'rtt' in kwargs:
            self.__rtt = kwargs['rtt']
            kwargs.pop('rtt')
        else:
            self.__rtt = 1.

    @property
    def rtt(self):
        return self.__rtt

    @rtt.setter
    def rtt(self, val):
        self.__rtt = val

