from database import DatabaseReadControl
import logging
import sys
from urllib import parse
import json
import time

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

while True:
    try:
        dbAccount = DatabaseReadControl(
            'db', 'root', 'sry200253', 'TreeHole', 'Account')
        break
    except Exception as e:
        logging.info(e)
        time.sleep(1)

def application(env, start_response):
    print(str(env))
    logging.info('env is' + str(env))
    start_response('200 OK', [('Content-Type','text/html')])
    if env['QUERY_STRING'] != '':
        data = str(processGet(env['QUERY_STRING']))
        logging.info(data)
        jj = json.dumps(data)
        logging.info(jj)
        return [bytes(jj, 'utf-8')]
    else:
        return [b"Hello World"]

def processGet(queryString):
    query = parse.parse_qs(queryString)
    logging.info(str(query))
    table = query['table'][0]
    index = query['index'][0]
    value = query['value'][0]
    if table == 'Account':
        data = dbAccount.searchByChar(index, value)
        return data