import logging
import sys
from urllib import parse
import json
import time
from redis_op import redisInit, MessageQueue
from database import dbInit, dbProcess

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

redisConnect = redisInit(host='redis', port=6379)
insQueue = MessageQueue(redisConnect, 'insQueue', 'producer')
dbPool = dbInit(host='db', username='root',
                password='sry200253', database='TreeHole')


def application(env, start_response):
    if env['REQUEST_METHOD'] == 'GET':
        if env['QUERY_STRING'] != '':
            start_response('200 OK', [('Content-Type', 'text/json')])
            res = str(processGet(env['QUERY_STRING']))
            return [bytes(res, 'utf-8')]
        else:
            start_response('204 No Content', [('Content-Type', 'text/html')])
            return [b"None"]
    elif env['REQUEST_METHOD'] == 'POST':
        res = processPost(env)
        start_response('202 Accepted', [('Content-Type', 'text/json')])
        insQueue.produce(res)
        logging.info(res)
        return [bytes(res, 'utf-8')]


def processGet(queryString):
    query = parse.parse_qs(queryString)
    table = query['table'][0]
    index = query['index'][0]
    value = query['value'][0]
    ins = {'type': 'select', 'table': table, 'data': {index: value}}
    data = dbProcess(dbPool, [ins])
    return json.dumps(data)


def processPost(env):
    try:
        requestBodySize = int(env.get('CONTENT_LENGTH', 0))
    except:
        requestBodySize = 0

    requestBody = env['wsgi.input'].read(requestBodySize)
    if requestBody != None:
        return str(requestBody)[2:requestBodySize+2]
    else:
        return None
