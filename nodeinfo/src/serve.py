import logging
import sys
import json
import time
from redis_op import redisInit, MessageQueue
from dataType import NodeMessage, NodeMes2json, json2NodeMes

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

redisConnect = redisInit(host='redis', port=6379)
proposerQueue = MessageQueue(redisConnect, 'proposerQueue', 'consumer')
acceptorQueue = MessageQueue(redisConnect, 'acceptorQueue', 'consumer')
learnerQueue = MessageQueue(redisConnect, 'learnerQueue', 'consumer')


def application(env, start_response):
    try:
        requestBodySize = int(env.get('CONTENT_LENGTH', 0))
    except:
        requestBodySize = 0

    requestBody = env['wsgi.input'].read(requestBodySize)
    logging.info(requestBody)
    NodeMessagejson = str(requestBody)[2:requestBodySize+2]
    logging.info(NodeMessagejson)
    if NodeMessagejson != '':
        tartgetAgent = json2NodeMes(NodeMessagejson).targetAgent
        if tartgetAgent == 'proposer':
            proposerQueue.produce(NodeMessagejson)
            logging.info('produce proposer message successfully')
        elif tartgetAgent == 'acceptor':
            acceptorQueue.produce(NodeMessagejson)
            logging.info('produce acceptor message successfully')
        elif tartgetAgent == 'learner':
            learnerQueue.produce(NodeMessagejson)
            logging.info('produce learner message successfully')
        start_response('202 Accepted', [('Content-Type', 'text/json')])
        return [bytes(NodeMessagejson, 'utf-8')]
    else:
        start_response('204 No Content', [('Content-Type', 'text/html')])
        return [b"None"]
