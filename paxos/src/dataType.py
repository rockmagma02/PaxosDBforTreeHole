import json


class Ins:
    type = None
    table = None
    data = None


class NodeMessage:
    type = None  # 消息类型 目前认为有 'prepareRequest', 'prepareRespond', 'acceptRequest', 'acceptRespond', 'BroadcastAccept'
    source = None  # 发送者的地址
    target = None  # 接收者的地址
    targetAgent = None  # 需要处理该消息的 agent
    turn = None  # 当前处理的轮次（之前版本使用round，但是round是python的内置函数）
    number = None  # 提案编号
    value = None  # 提案内容，应该是 Ins 的 Dict 格式 or json 格式
    promise = None  # acceptor 做出的 promise
    accept = None  # acceptor 是否接受提案


def Ins2json(Ins):
    out = {
        'type': Ins.type,
        'table': Ins.table,
        'data': Ins.data
    }
    return json.dumps(out)


def json2Ins(jsObj):
    obj = json.loads(jsObj)
    out = Ins()
    out.type = obj['type']
    out.table = obj['table']
    out.data = obj['data']
    return out

def NodeMes2json(NodeMes):
    out = {
        'type': NodeMes.type,
        'source': NodeMes.source,
        'target': NodeMes.target,
        'targetAgent': NodeMes.targetAgent,
        'turn': NodeMes.turn,
        'number': NodeMes.number,
        'value': NodeMes.value,
        'promise': NodeMes.promise,
        'accept': NodeMes.accept
    }
    return json.dumps(out)

def json2NodeMes(jsObj):
    obj = json.loads(jsObj)
    out = NodeMessage()
    out.type = obj['type']
    out.source = obj['source']
    out.target = obj['target']
    out.targetAgent = obj['targetAgent']
    out.turn = obj['turn']
    out.number = obj['number']
    out.value = obj['value']
    out.promise = obj['promise']
    out.accept = obj['accept']
    return out


