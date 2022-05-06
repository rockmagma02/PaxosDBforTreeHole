"""
Server_Paxos
Node的paxos部分
"""

'''
Sunjq:
待解决:
并行需要保护哪些变量？
''' 

import json
import datetime
import threading
import redis
import datatype
import redis_op

'''
节点常量
'''
NMAXNODENO = 2  #最大节点编号
NMAJORITY = (NMAXNODENO + 1)//2 + 1  #这里定义是严格大于1/2
NODENO = 0

'''
节点全局变量
'''
roundNo = 0  #轮次编号
roundFlag = 0  #进入下一轮 L给P,A提示
redisConnect = redis_op.redisInit(host='redis', port=6379)
sender = redis_op.MessageQueue(redisConnect,'sender','producer')
insQueue = redis_op.MessageQueue(redisConnect,'insQueue','consumer')
proposerQueue = redis_op.MessageQueue(redisConnect,'proposerQueue','consumer')
acceptorQueue = redis_op.MessageQueue(redisConnect,'acceptorQueue','consumer')
learnerQueue = redis_op.MessageQueue(redisConnect,'learnerQueue','consumer')

'''
Messenger
用来为三个角色发送消息的函数类
'''
class Messenger (object):
    global sender
    global roundNo
    def send_prepare(self, proposal_id):
        '''
        Broadcasts a Prepare message to all Acceptors
        '''
        prepare_request = datatype.passed_instruction()
        prepare_request.type = datatype.TPROPOSAL_ACCEPTOR_1
        prepare_request.source = NODENO
        prepare_request.round = roundNo
        prepare_request.number = proposal_id
        prepare_request.accepted = False
        prepare_request.content = ''
        #向其他节点发送prepare请求
        for tgt in range(0,NMAXNODENO):
            if tgt != NODENO:
                prepare_request.target = tgt
                message = datatype.passed2json(prepare_request)
                sender.produce(json.dumps(message))

    def send_promise(self, proposer_uid, proposal_id, previous_id, accepted_value):
        '''
        Sends a Promise message to the specified Proposer
        '''

    def send_accept(self, proposal_id, proposal_value):
        '''
        Broadcasts an Accept message to all Acceptors
        '''
        #准备accept请求的内容
        accept_request = datatype.passed_instruction()
        accept_request.type = datatype.TPROPOSAL_ACCEPTOR_2
        accept_request.source = NODENO
        accept_request.round = roundNo
        accept_request.number = proposal_id
        accept_request.accepted = False
        accept_request.content = proposal_value
        #向其他节点发送accept请求
        for tgt in range(0,NMAXNODENO):
            if tgt != NODENO:
                accept_request.target = tgt
                message = datatype.passed2json(accept_request)
                sender.produce(json.dumps(message))

    def send_accepted(self, proposal_id, accepted_value):
        '''
        Broadcasts an Accepted message to all Learners
        '''

    def on_resolution(self, proposal_id, value):
        '''
        Called when a resolution is reached
        '''
        
messenger = Messenger()

class Proposer:
    '''
    Sunjq:
    Proposer的任务
    从Ins消息队列里取一条指令,或者增加上一条指令优先级
    发送prepare
    如果得到多数accept,发送propose,否则停止
    等待节点通知轮次结束
    开始下一个轮次

    Note:
    提案编号为3位优先级+20位(8<yyyymmdd>+6<hhmmss>+6<ms>)Ins时间戳
    '''

    def __init__(self, messenger, uid, quorum_size) -> None:
        self.priority = 0
        self.rejected = False
        self.proposal_id = ''
        self.instruction = datatype.input_instruction()
        self.messenger            = messenger
        self.proposer_uid         = uid
        self.quorum_size          = quorum_size
        self.promises_rcvd        = None

    '''
    main func
    '''

    def Proposer_Main(self):
        global roundFlag
        while 1:
        #新一轮次开始，检查上一提案的状态
            if self.rejected:
                self.rejected = False
                self.priority += 1
            else:
                self.instruction = self.Get_Next_Ins()
                self.priority = 0
            self.Prepare()
            self.Listen_Response()
            if not self.rejected:
                self.Propose()
            while roundFlag == 0:  #等待当前轮次结束
                pass

    def Prepare(self):
        #生成proposal_id
        strPriority = '%03d' % self.priority
        strTime = str(datetime.datetime.now())
        timeStamp = strTime[0:4]+strTime[5:7]+strTime[8:10]\
            +strTime[11:13]+strTime[14:16]+strTime[17:19]+strTime[20:26]
        strPriority += timeStamp
        self.proposal_id = strPriority
        #发送
        self.messenger.send_prepare(self.proposal_id)
        

    def Propose(self):
        content = json.dump(self.instruction)
        self.messenger.send_accept(self.proposal_id,content)

    def Listen_Response(self):
        '''
        监听Acceptor的回复消息,直到把该prepare的回复消息处理完
        如果得到大多数的同意,则进入Propose
        否则,避让,等待轮次结束
        '''
        global proposerQueue
        acceptNum = 0
        if acceptNum >= NMAJORITY:
            self.rejected = False
        else: 
            self.rejected = True

    
    '''
    helper func
    '''
        

    def Get_Next_Ins(self):  
        '''
        从Ins列表中取下一个指令
        这里,proposer可能会挂起:当消息队列为空,等待client的消息
        '''
        

    def Get_Next_Response(self):  #从Response列表中取下一个消息
        pass

class Acceptor:
    def Acceptor_Main():
        pass

class Learner:
    def Learner_Main():
        pass


def Start_Proposer():  #在节点的一个线程中执行
    proposer = Proposer(messenger,NODENO,NMAJORITY)
    proposer.Proposer_Main()

def Start_Acceptor():  #在节点的一个线程中执行
    acceptor = Acceptor()
    acceptor.Acceptor_Main()

def Start_Learner():  #在节点的一个线程中执行
    learner = Learner()
    learner.Learner_Main()
    
def Run_Threads():
    tp = threading.Thread(target=Start_Proposer,args=())
    ta = threading.Thread(target=Start_Acceptor,args=())
    tl = threading.Thread(target=Start_Learner,args=())

    tp.start()
    ta.start()
    tl.start()

def Node_Initialize():
    pass

def main():
    Node_Initialize()
    Run_Threads()

if __name__ == '__main__':
    main()
