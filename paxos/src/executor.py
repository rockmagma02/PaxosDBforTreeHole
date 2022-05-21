from redis_op import MessageQueue
from database import dbProcess
import json


class Executor:
    def __init__(self, redisPool, dbPool, firstTurn):
        self.redisPool = redisPool
        self.execution = MessageQueue(self.redisPool, 'executor', 'consumer')
        self.dbPool = dbPool
        self.firstTurn = firstTurn
        self.nowTurn = firstTurn
        self.insQ = {}
        self.minNeedEx = float('inf')

    def run(self):
        while True:
            message = self.execution.consume()
            if message is not None:
                message = json.loads(message)
                if message['turn'] == self.nowTurn + 1:
                    self.execute(message['ins'])
                    self.nowTurn += 1
                else:
                    self.insQ[message['turn']] = message['ins']
                    if message['turn'] < self.minNeedEx:
                        self.minNeedEx = message['turn']
            while self.minNeedEx == self.nowTurn + 1:
                self.execute(self.insQ[self.minNeedEx])
                self.insQ.pop(self.minNeedEx)
                self.nowTurn += 1
                if not self.insQ:
                    self.minNeedEx = min(list(self.insQ.keys()))
                else:
                    self.minNeedEx = float('inf')

    def execute(self, ins):
        ins = json.loads(ins)
        dbProcess(self.dbPool, [ins])
