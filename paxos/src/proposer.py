from dataType import NodeMessage, NodeMes2json, json2NodeMes
from redis_op import MutexVar, MessageQueue
from collections import Counter
import json
import time

import threading


class Proposer(threading.Thread):
    def __init__(self, turn, proposal, host, addresses, MQ: MessageQueue, sender: MessageQueue):
        threading.Thread.__init__(self)
        self.addresses = addresses
        self.majority = len(self.addresses) // 2 + 1
        self.acceptValues = [False for i in range(len(self.addresses))]
        self.hadsent = [False for i in range(len(self.addresses))]
        self.host = host  # 记录自己的地址
        self.turn = turn
        self.number = int(- time.time() * 1e7)
        self.value = proposal
        self.mq = MQ
        self.sd = sender

    def run(self):
        self.makePrepareRequest()
        while True:
            mes = self.mq.consume()
            mes = json2NodeMes(mes)
            if mes.type == 'prepareRespond':
                if mes.promise == False:
                    return False
                elif mes.promise == True:
                    senderId = self.addresses.index(mes.source)
                    self.acceptValues[senderId] = res.value
                    mostCommonValue = Counter(
                        self.acceptValues).most_common(1)[0]
                    if (mostCommonValue[0] != False) and (mostCommonValue[1] >= self.majority):
                        if mostCommonValue[0] != None:
                            self.value = mostCommonValue[0]
                        self.makeAcceptRequest()

    def makePrepareResquest(self):
        for target in self.addresses:
            mes = NodeMessage()
            mes.type = 'prepareRequest'
            mes.source = self.host
            mes.target = target
            mes.targetAgent = 'acceptor'
            mes.turn = self.turn
            mes.number = self.number
            mes.value = None
            mes.promise = None
            mes.accept = None
            self.sd.produce(NodeMes2json(mes))

    def makeAcceptRequest(self):
        for i in range(len(self.addresses)):
            if (self.acceptValues[i] != False) and (self.hadsent[i] == False):
                mes = NodeMessage()
                mes.type = 'acceptRequest'
                mes.source = self.host
                mes.target = self.address[i]
                mes.targetAgent = 'acceptor'
                mes.turn = self.turn
                mes.number = self.number
                mes.value = self.value
                mes.promise = None
                mes.accept = None
                self.sd.produce(NodeMes2json(mes))
