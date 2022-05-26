import redis
from paxos import paxos
from redis_op import MessageQueue, generteMutex
from database import dbInit, dbProcess, Ins2Sql
from multiprocessing import Queue
import logging
from multiprocessing import Process
from dataType import NodeMessage, NodeMes2json, json2NodeMes
import json


# 单例设计模式
class MailRoom():
    __obj = None

    def __new__(cls, *args, **kwargs):
        if not cls.__obj:
            cls.__obj = object.__new__(cls)
        return cls.__obj

    def __init__(self, MailQueue: MessageQueue, turnBoard, redisPool: redis.ConnectionPool, dbPool, host, address):
        self.MailQueue = MailQueue
        self.turnBoardName = turnBoard
        self.redispool = redisPool
        self.dbPool = dbPool
        self.host = host
        self.address = address

    def run(self):
        insQueue = MessageQueue(self.redispool, 'insQueue', 'consumer')
        senderQueue = MessageQueue(self.redispool, 'sender', 'producer')
        while True:
            mesJson = self.MailQueue.consume()
            if mesJson is not None:
                mes = json2NodeMes(mesJson)

                # 获取正在进行的轮次
                lock = generteMutex(
                    self.redispool, self.turnBoardName + 'Mutex')
                if lock.acquire():
                    r = redis.Redis(connection_pool=self.redispool,
                                    decode_responses=True)
                    turns = json.loads(r.get(self.turnBoardName))
                lock.release()

                # 如果消息的轮次是正在进行的轮次，则会分发消息
                if mes.turn in turns:
                    if mes.targetAgent == 'proposer':
                        MessageQueue(self.redispool, 'proposer_' +
                                     str(mes.turn), 'producer').produce(mesJson)
                    elif mes.targetAgent == 'acceptor':
                        MessageQueue(self.redispool, 'acceptor_' +
                                     str(mes.turn), 'producer').produce(mesJson)
                    elif mes.targetAgent == 'learner':
                        MessageQueue(self.redispool, 'learner_' +
                                     str(mes.turn), 'producer').produce(mesJson)

                else:
                    # 如果消息的轮次不是正在进行的轮次，且该轮次没有done，则会建立新的轮次

                    # 查看该轮次是否结束
                    ins = {'type': 'select', 'table': 'PaxosTurns',
                           'data': {'id': mes.turn}}
                    res = dbProcess(self.dbPool, [ins])
                    if len(res) == 0:  # 轮次没有done

                        # 建立新轮次
                        lock = generteMutex(
                            self.redispool, self.turnBoardName + 'Mutex')
                        if lock.acquire():
                            r = redis.Redis(connection_pool=self.redispool,
                                            decode_responses=True)
                            turns = json.loads(r.get(self.turnBoardName))
                            turns.append(mes.turn)
                            r.set(self.turnBoardName, json.dumps(turns))
                        lock.release()

                        # 新的paxos
                        proposal = insQueue.consume_withoutBreaking()
                        paxosP = Process(target=paxos, args=(
                            mes.turn, self.host, self.address, proposal, senderQueue, self.redispool, self.dbPool, self.turnBoardName))
                        paxosP.start()

                        if mes.targetAgent == 'proposer':
                            MessageQueue(self.redispool, 'proposer_' +
                                        str(mes.turn), 'producer').produce(mesJson)
                        elif mes.targetAgent == 'acceptor':
                            MessageQueue(self.redispool, 'acceptor_' +
                                        str(mes.turn), 'producer').produce(mesJson)
                        elif mes.targetAgent == 'learner':
                            MessageQueue(self.redispool, 'learner_' +
                                        str(mes.turn), 'producer').produce(mesJson)
