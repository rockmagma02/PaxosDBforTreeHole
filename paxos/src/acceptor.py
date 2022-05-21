from dataType import NodeMessage, NodeMes2json, json2NodeMes
from redis_op import MessageQueue
import json

import threading


class Acceptor(threading.Thread):
    def __init__(self, turn, host, addresses, MQ: MessageQueue, sender: MessageQueue):
        threading.Thread.__init__(self)
        self.addresses = addresses
        self.host = host  # 记录自己的地址
        self.turn = turn
        self.promiseID = None
        self.isAccept = False
        self.FirstAccept = False
        self.acceptID = None
        self.acceptValue = None
        self.mq = MQ
        self.sd = sender

    def run(self):
        while True:
            if self.FirstAccept == True:
                self.broadcastAccept()
                self.FirstAccept = False
            mes = self.mq.consume()
            if mes is not None:
                mes = json2NodeMes(mes)
                if mes.type == 'prepareRequest':
                    self.makePrepareResponce(mes)
                elif mes.type == 'acceptRequest':
                    self.makeAcceptorResponce(mes)

    def makePrepareResponce(self, mes):
        ProposalNum = mes.number
        reply = NodeMessage()
        reply.type = 'prepareRespond'
        reply.source = mes.target
        reply.target = mes.source
        reply.targetAgent = 'proposer'
        reply.turn = mes.turn
        if (self.promiseID is not None) and (ProposalNum < self.promiseID):
            reply.number = self.promiseID
            reply.value = self.acceptValue
            reply.promise = False
            reply.accept = None
        else:
            reply.number = self.acceptID
            reply.value = self.acceptValue
            reply.promise = True
            reply.accept = None
            self.promiseID = mes.number
        self.sd.produce(NodeMes2json(reply))

    def makeAcceptorResponce(self, mes):
        ProposalNum = mes.number
        reply = NodeMessage()
        reply.type = 'acceptRespond'
        reply.source = mes.target
        reply.target = mes.source
        reply.targetAgent = 'proposer'
        reply.turn = mes.turn
        if (self.promiseID is not None) and (mes.number >= self.promiseID):
            if self.isAccept == False:
                self.FirstAccept = True
            self.isAccept = True
            self.acceptID = mes.number
            self.acceptValue = mes.value
            reply.number = self.acceptID
            reply.value = self.acceptValue
            reply.promise = None
            reply.accept = True
        else:
            reply.accept = False
        self.sd.produce(NodeMes2json(reply))

    def broadcastAccept(self):
        for target in self.addresses:
            message = NodeMessage()
            message.type = 'BroadcastAccept'
            message.source = self.host
            message.target = target
            message.targetAgent = 'learner'
            message.turn = self.turn
            message.num = self.acceptID
            message.value = self.acceptValue
            message.accept = None
            message.promise = None
            self.sd.produce(NodeMes2json(message))
