import redis
from redis_op import MessageQueue, generteMutex
from multiprocessing import Queue
from dataType import NodeMessage, NodeMes2json, json2NodeMes
import json

# 这是 mailroon 用来通知 paxos 管理员需要新建 paxos 简称的通知的结构体


class paxosInform:
    turn = None
    AcceptorMQ = None
    ProposerMQ = None
    LearnerMQ = None


# 单例设计模式
class MailRoom():
    __obj = None

    def __new__(cls, *args, **kwargs):
        if not cls.__obj:
            cls.__obj = object.__new__(cls)
        return cls.__obj

    def __init__(self, MailQueue: MessageQueue, turnBoard, inform: Queue, redisPool: redis.ConnectionPool):
        self.MailQueue = MailQueue
        self.turnBoardName = turnBoard
        self.informQueue = inform
        self.pool = redisPool

    def run():
        while True:
            mesJson = self.MailQueue.consume()
            if mesJson is not None:
                mes = json2NodeMes(mesJson)
                lock = generteMutex(self.pool, self.turnBoardName + 'Mutex')
                if lock.acquire():
                    r = redis.Redis(connection_pool=self.pool,
                                    decode_responses=True)
                    turns = json.loads(r.get(self.turnBoardName))
                lock.release()
                if mes.turn not in turns:
                    lock = generteMutex(
                        self.pool, self.turnBoardName + 'Mutex')
                    if lock.acquire():
                        r = redis.Redis(connection_pool=self.pool,
                                        decode_responses=True)
                        turns = json.loads(r.get(self.turnBoardName))
                        turns.append(mes.turn)
                        r.set(self.tuBoardName, json.dumps(turns))
                    lock.release()

                    inform = paxosInform()
                    inform.turn = mes.turn
                    inform.ProposerMQ = MessageQueue(
                        self.pool, 'proposer_'+str(mes.turn), 'produce')
                    inform.AcceptorMQ = MessageQueue(
                        self.pool, 'acceptor_'+str(mes.turn), 'produce')
                    inform.LearnerMQ = MessageQueue(
                        self.pool, 'learner_'+str(mes.turn), 'produce')
                    self.informQueue.put(inform)

                if mes.targetAgent == 'proposer':
                    MessageQueue(self.pool, 'proposer_' +
                                 str(mes.turn), 'produce').produce(mesJson)
                elif mes.targetAgent == 'acceptor':
                    MessageQueue(self.pool, 'acceptor_' +
                                 str(mes.turn), 'produce').produce(mesJson)
                elif mes.targetAgent == 'learner':
                    MessageQueue(self.pool, 'learner_' +
                                 str(mes.turn), 'produce').produce(mesJson)
