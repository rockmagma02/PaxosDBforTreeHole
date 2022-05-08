from multiprocessing import Process, Queue
from paxos import paxos
from redis_op import redisInit, MessageQueue, generteMutex
import redis
import redis_lock
import json
import time
from mail_room import MailRoom

address = ['111', '222', '333']
host = '111'

if __name__ == '__main__':
    redisPool = redisInit(host='redis', port=6379)
    mailQueue = MessageQueue(redisPool, 'MessageQueue', 'consumer')
    insQueue = MessageQueue(redisPool, 'insQueue', 'consumer')
    inform = Queue()
    turnBoard = 'turnBoard'
    turnBoardMutex = 'turnBoardMutex'
    turn = 0

    lock = generteMutex(redisPool, turnBoardMutex)
    if lock.acquire():
        r = redis.Redis(connection_pool=redisPool, decode_responses=True)
        r.set(turnBoard, json.dumps([]))
    lock.release()

    mailRoom = MailRoom(MailQueue=mailQueue, turnBoard=turnBoard,
                        inform=inform, redisPool=redisPool)
    mailRoomProcess = Process(target=mailRoom.run())
    mailRoomProcess.start()

    while True:
        lock = generteMutex(redisPool, turnBoardMutex)
        if lock.acquire():
            r = redis.Redis(connection_pool=redisPool, decode_responses=True)
            turns = r.get(turnBoard)
        lock.release()

        if len(turns) <= 5:
            proposer = insQueue.consume_withoutBreaking()
            if proposer is not None:
                paxos(max(turns)+1, host, addresses, proposal, MQ_p, MQ_a, MQ_l, sender, redisPool)
            # 主动提案

        try:
            info = inform.get(False)
            pass
        except:
            time.sleep(0.0001)
        # 被动提案
