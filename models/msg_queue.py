import logging
from .log_model import TheLogger
import simpy
from collections import deque

from .unit import Message, Pdu
from .server import BaseServer

class MsgQueue(object):
    '''
    The queue that waits for serve
    FCFS(FIFO)
    '''

    def __init__(self, env, server=None):
        self.queue = deque()
        assert isinstance(env, simpy.Environment)
        self.__env = env
        self.log = TheLogger(self.__class__.__name__)  # modified by lee on 1/4/2017

        if server:
            self.__server = server
        else:
            self.__server = BaseServer(self.__env, self)
        # self.action = self.__env.process(self.run())

    def set_server(self, server):
        assert isinstance(server, BaseServer)
        self.__server = server

    def get_server(self):
        return self.__server
    server = property(get_server, set_server, None, 'Server for this queue')

    def on_arrival(self, msg):
        isinstance(msg, Message)
        print("new message with {0:d} packets arrive at MsgQueue".format(msg.packets_num))
        self.log.logger.info("new message with {0:d} packets arrive at MsgQueue".format(msg.packets_num))      # modified by lee on 1/4/2017

        self.queue.extend([packet.at_arrive() for packet in msg])

    def get_pdu(self, pdu_size):
        to_serve = pdu_size
        serve_pdu = Pdu(self.__env, pdu_size)

        while True:
            if self.queue.__len__() > 0:
                print("generate pdu, except {0:d} bytes".format(to_serve))
                self.log.logger.info("generate pdu, except {0:d} bytes".format(to_serve))      # modified by lee on 1/4/2017
                first = self.queue.popleft()
                if first.size > pdu_size:
                    serve_pdu.append(first.get(to_serve))
                    self.queue.appendleft(first)
                    break
                elif first.size == to_serve:
                    serve_pdu.append(first.get(to_serve))
                    break
                else:
                    to_serve -= first.size
                    serve_pdu.append(first.get(first.size))
                print('Buffer size:{0}'.format(self.queue.__len__()))       # add output buffer size by chengjiyu on 2016/10/13
                self.log.logger.info('Buffer size:{0}'.format(self.queue.__len__()))       # modified by lee on 1/4/2017
            else:
                break
        if serve_pdu.filled is 0:
            print("empty pdu")
            self.log.logger.info("empty pdu")       # modified by lee on 1/4/2017
            return None
        else:
            return serve_pdu


    def run(self):
        while True:
            try:
                yield self.__env.process(self.check_queue())
            except simpy.Interrupt:
                print("send one pdu to server....")
                self.log.logger.info("send one pdu to server....")     # modified by lee on 1/4/2017
                to_serve = self.__server.get_serve_size()
                serve_pdu = Pdu(self.__env, to_serve)
                while True:
                    if self.queue.__len__() > 0:
                        first = self.queue.popleft()
                        if first.size > to_serve:
                            serve_pdu.append(first.get(to_serve))
                            self.queue.appendleft(first)
                            break
                        elif first.size == to_serve:
                            serve_pdu.append(first.get(to_serve))
                            break
                        else:
                            to_serve -= first.size
                            serve_pdu.append(first.get(first.size))
                    else:
                        break
                print("Pdu with {0:d} bytes generated".format(serve_pdu.total_size))
                self.log.logger.info("Pdu with {0:d} bytes generated".format(serve_pdu.total_size))     # modified by lee on 1/4/2017
                yield self.__env.process(self.__server.serve(serve_pdu))
            else:
                yield self.__env.timeout(10)

    def check_queue(self):
        if len(self.queue) == 0:
            yield self.__env.timeout(10)
        else:
            pass
