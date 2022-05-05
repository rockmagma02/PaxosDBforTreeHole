import json

TPROPOSAL_ACCEPTOR_1 = 0
TPROPOSAL_ACCEPTOR_2 = 1
TACCEPTOR_PROPOSAL_1 = 2
TACCEPTOR_PROPOSAL_2 = 3
TACCEPTOR_LEARNER = 4
TLEARNER_LEARNER = 5

PDATA = 0
PACCOUNT = 1
#这里定义了数据和账户存储的表号

TADD = 1024
TDELETE = 1025
TBROWSE = 1026
TSIGNUP = 1027
TLOGIN = 1028


class input_instruction:
    type = TADD  #输入信息类型
    table = PDATA  #访问表号
    content = ''  #若type为增加，content存储增加内容;若type为删或改，content存储树洞号;若type为注册或登录，content存储为一个Account


class Account:
    email = ''
    username = ''
    password = ''


class passed_instruction:
    type = TPROPOSAL_ACCEPTOR_1  #发送信息类型。
    source = 0  #发送信息的结点编号
    target = 0  #目标结点编号
    round = 0  #轮次数
    number = 0  #提案编号
    accepted = True
    content = ''  #若为learner之间请求不足指令，存储需要补全的所有指令;否则存储当前指令。


def passed2json(input):
    output = {
        "type": input.type,
        "source": input.source,
        "target": input.target,
        "round": input.round,
        "number": input.number,
        "accepted": input.accepted,
        "content": input.content
    }
    return output


def json2passed(input):
    output = passed_instruction()
    output.type = input['type']
    output.source = input['source']
    output.target = input['target']
    output.round = input['round']
    output.number = input['number']
    output.accepted = input['accepted']
    output.content = input['content']
    return output


def input2json(input):
    output = {
        "type": input.type,
        "table": input.table,
        "content": input.content
    }
    return output


def json2input(input):
    output = input_instruction()
    output.type = input['type']
    output.table = input['table']
    output.content = input['content']
    return output


def account2json(input):
    output = {
        "email": input.email,
        "username": input.username,
        "password": input.password
    }
    return output


def json2account(input):
    output = Account()
    output.email = input['email']
    output.username = input['username']
    output.password = input['password']
    return output


def getinput(input: str):
    input = input.split(sep=' ')
    output = input_instruction()
    if input.__len__ == 0:
        return
    elif input[0] == 'add':
        output.type = TADD
        output.table = PDATA
        output.content = input[1]

    elif input[0] == 'del':
        output.type = TDELETE
        output.table = PDATA
        output.content = input[1]

    elif input[0] == 'browse':
        output.type = TBROWSE
        output.table = PDATA
        output.content = input[1]

    elif input[0] == 'signup':
        output.type = TSIGNUP
        output.table = PACCOUNT
        acc = Account()
        acc.email = input[1]
        acc.username = input[2]
        acc.password = input[3]
        output.content = json.dumps(account2json(acc))

    elif input[0] == 'login':
        output.type = TLOGIN
        output.table = PACCOUNT
        acc = Account()
        acc.email = input[1]
        acc.username = input[2]
        acc.password = input[3]
        output.content = json.dumps(account2json(acc))
    else:
        print('Syntax error')
    return output
