import requests
import logging
from dataType import NodeMessage, NodeMes2json, json2NodeMes
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def sender(messageJson):
    mes = json2NodeMes(messageJson)
    target = mes.target
    url = 'http://' + target + ':90'
    r = requests.post(url, data=messageJson)
    if r.status_code == 202:
        logging.info('send successfully')
    else:
        logging.info('send failed')