import logging
import sys
from urllib import parse
import json
import time
from redis_op import redisInit, MessageQueue
from database import dbInit, dbProcess
import datetime

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
        return [bytes(res, 'utf-8')]


def processGet(queryString):
    DELAY = 0
    time.sleep(DELAY)
    query = parse.parse_qs(queryString)
    table = query['table'][0]
    index = query['index'][0]
    value = query['value'][0]
    ins = {'type': 'select', 'table': table, 'data': {index: value}}
    data = dbProcess(dbPool, [ins])
    if query['table'][0] == 'Account':
        d = {
            'id': data[0][0],
            'mail': data[0][1],
            'passwordHash': data[0][2],
            'passwordHash': data[0][3].strftime('%Y-%m-%d %H:%M:%S')
        }
    elif query['table'][0] == 'HoleContent':
        d = {
            'treeId': data[0][0],
            'content': data[0][1],
            'author': data[0][2],
            'createTime': data[0][3].strftime('%Y-%m-%d %H:%M:%S')
        }
    return json.dumps(d)


def processPost(env):
    try:
        requestBodySize = int(env.get('CONTENT_LENGTH', 0))
    except:
        requestBodySize = 0

    requestBody = env['wsgi.input'].read(requestBodySize)
    if requestBody != '':
        return requestBody.decode()
    else:
        return None
