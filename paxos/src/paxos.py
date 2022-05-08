from proposer import Proposer
from acceptor import Acceptor
from learner import Learner

import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

from dataType import NodeMessage, NodeMes2json, json2NodeMes
from redis_op import MessageQueue
import redis
import redis_lock

import threading
from queue import Queue

def paxos(turn, host, addresses, proposal, MQ_p: MessageQueue, MQ_a: MessageQueue, MQ_l: MessageQueue, sender: MessageQueue, redisPool):
    if proposal is not None:
        proposer = Proposer(turn, proposal, host, addresses, MQ_p, sender)
        proposer.start()
        
    acceptor = Acceptor(turn, host, addresses, MQ_a, sender)
    acceptor.start()
    
    learner = Learner(turn, host, addresses, MQ_l, sender)
    learner.start()
    
    learner.join()
    ins = learner.decide
    
    logging.info(ins)
    
    
