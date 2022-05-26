import logging
import sys
import json
import time
from redis_op import redisInit, MessageQueue
from dataType import NodeMessage, NodeMes2json, json2NodeMes

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

redisConnect = redisInit(host='redis', port=6379)
Messages = MessageQueue(redisConnect, 'MessageQueue', 'producer')


def application(env, start_response):
    try:
        requestBodySize = int(env.get('CONTENT_LENGTH', 0))
    except:
        requestBodySize = 0

    requestBody = env['wsgi.input'].read(requestBodySize)
    NodeMessagejson = requestBody.decode()
    if NodeMessagejson != '':
        Messages.produce(NodeMessagejson)
        start_response('202 Accepted', [('Content-Type', 'text/json')])
        return [bytes(NodeMessagejson, 'utf-8')]
    else:
        start_response('204 No Content', [('Content-Type', 'text/html')])
        return [b"None"]
