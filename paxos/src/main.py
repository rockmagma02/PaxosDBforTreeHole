from multiprocessing import Process, Queue
from paxos import paxos
from redis_op import redisInit, MessageQueue, generteMutex
from database import dbInit, dbProcess, Ins2Sql
import redis
import redis_lock
import json
import logging
import sys
import time
from mail_room import MailRoom
from executor import Executor

logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)

# 一些 常量
address = ['paxos111', 'paxos222', 'paxos333', 'paxos444', 'paxos555']
host = 'paxos111'

dbPool = dbInit('db', 'root', 'sry200253', 'TreeHole')
redisPool = redisInit(host='redis', port=6379)
mailQueue = MessageQueue(redisPool, 'MessageQueue', 'consumer')
insQueue = MessageQueue(redisPool, 'insQueue', 'consumer')
senderQueue = MessageQueue(redisPool, 'sender', 'producer')
turnBoard = 'turnBoard'
turnBoardMutex = 'turnBoardMutex'

if __name__ == '__main__':
    lock = generteMutex(redisPool, turnBoardMutex)
    if lock.acquire():
        r = redis.Redis(connection_pool=redisPool, decode_responses=True)
        r.set(turnBoard, json.dumps([]))
    lock.release()

    mailRoom = MailRoom(mailQueue, turnBoard, redisPool, dbPool, host, address)
    mailRoomProcess = Process(target=mailRoom.run)
    mailRoomProcess.start()
    logging.critical('mail room begin to work')
    
    executor = Executor(redisPool, dbPool, 0)
    executorProcess = Process(target=executor.run)
    executorProcess.start()
    logging.critical('executor begin to work')

    while True:
        lock = generteMutex(redisPool, turnBoardMutex)
        if lock.acquire(blocking=True):
            r = redis.Redis(connection_pool=redisPool, decode_responses=True)
            turns = json.loads(r.get(turnBoard))
            if len(turns) <= 10:
                proposal = insQueue.consume_withoutBreaking()
                if proposal is not None:
                    tt = dbProcess(dbPool, [{'type': 'selectLast', 'table': 'PaxosTurns', 'data': {'id': None}}])
                    if len(tt) == 0:
                        turn = 1
                    else:
                        turn = tt[0][0] + 1
                    if len(turns) != 0:
                        turn = max(turn, max(turns)+1)
                    if turn == 1:
                        r.set('start_time', f'{time.time()}')
                    turns.append(turn)
                    r.set(turnBoard, json.dumps(turns))
                    paxosP = Process(target=paxos, args=(turn, host, address, proposal, senderQueue, redisPool, dbPool, turnBoard))
                    paxosP.start()
        lock.release()
        time.sleep(0.02)
            # 主动提案
