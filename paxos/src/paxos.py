from queue import Queue
import threading
import redis_lock
import redis
from redis_op import MessageQueue
from dataType import NodeMessage, NodeMes2json, json2NodeMes
from proposer import Proposer
from acceptor import Acceptor
from learner import Learner
import sys

import logging
logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)


def paxos(turn, host, addresses, proposal, sender: MessageQueue, redisPool):
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


    # TODO 删掉turnBorad里的轮次
    # TODO 执行指令
    # TODO 标记执行过的轮次
    # TODO fanhui proposal

    logging.critical('paxos done')
    logging.critical(ins)