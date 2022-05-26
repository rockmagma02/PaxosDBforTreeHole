from queue import Queue
import threading
import redis_lock
import redis
from redis_op import MessageQueue, generteMutex
from dataType import NodeMessage, NodeMes2json, json2NodeMes
from proposer import Proposer
from acceptor import Acceptor
from learner import Learner
from database import dbProcess
import sys
import json
import time

import logging
logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)


def paxos(turn, host, addresses, proposal, sender: MessageQueue, redisPool, dbPool, turnBoard):
    MQ_p = MessageQueue(redisPool, 'proposer_' + str(turn), 'consumer')
    MQ_a = MessageQueue(redisPool, 'acceptor_' + str(turn), 'consumer')
    MQ_l = MessageQueue(redisPool, 'learner_' + str(turn), 'consumer')
    
    if proposal is not None:
        proposer = Proposer(turn, proposal, host, addresses, MQ_p, sender)
        proposer.start()

    acceptor = Acceptor(turn, host, addresses, MQ_a, sender)
    acceptor.start()

    learner = Learner(turn, host, addresses, MQ_l, sender)
    learner.start()

    learner.join()
    ins = learner.decide

    insQueue = MessageQueue(redisPool, 'insQueue', 'consumer')
    if (proposal is not None) and (proposal != ins):
        insQueue.pushR(proposal)

    execution = MessageQueue(redisPool, 'executor', 'producer')
    execution.produce(json.dumps({'turn': turn, 'ins': ins}))

    turnBoardMutex = turnBoard + 'Mutex'
    lock = generteMutex(redisPool, turnBoardMutex)
    if lock.acquire():
        tt = dbProcess(dbPool, [{'type': 'select', 'table': 'PaxosTurns', 'data': {'id': turn}}])
        if len(tt) == 0:

            dbProcess(dbPool, [{'type': 'insert', 'table': 'PaxosTurns', 'data': {'id': turn, 'status': 'done'}}])



        r = redis.Redis(connection_pool=redisPool, decode_responses=True)
        turns = json.loads(r.get(turnBoard))
        turns.remove(turn)
        r.set(turnBoard, json.dumps(turns))
        r.set(f'{turn} done', f'{time.time()}')
    lock.release()
