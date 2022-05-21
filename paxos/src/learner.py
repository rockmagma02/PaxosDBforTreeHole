from dataType import NodeMessage, NodeMes2json, json2NodeMes
from redis_op import MessageQueue
from collections import Counter
import json

import threading
from queue import Queue

class Learner(threading.Thread):
    def __init__(self, turn, host, addresses, MQ: MessageQueue, sender: MessageQueue):
        threading.Thread.__init__(self)
        self.addresses = addresses
        self.majority = len(self.addresses) // 2 + 1
        self.host = host  # 记录自己的地址
        self.turn = turn
        self.mq = MQ
        self.sd = sender
        self.values = [None for i in range(len(self.addresses))]
        self.decide = None

    def run(self):
        while True:
            mes = self.mq.consume()
            if mes is not None:
                mes = json2NodeMes(mes)
                targetId = self.addresses.index(mes.source)
                self.values[targetId] = mes.value
                value = Counter(self.values).most_common()
                if (value[0][0] is not None) and (value[0][1] >= self.majority):
                    self.decide = value[0][0]
                    return value[0][0]
