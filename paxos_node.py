"""
Server_Paxos
Node的paxos部分
"""

'''
Sunjq:
待解决:
需要一些接口完成列表和消息传递
节点在那些地方需要挂起?可能是从消息队列中取东西的时候
节点如何结束？
''' 

from asyncio import SendfileNotAvailableError
from glob import glob
import json
import datetime
import threading

from redis import ConnectionPool
from datatype import input_instruction, passed_instruction
from datatype import passed2json
from datatype import json2passed
from redis_op import MessageQueue, redisInit

'''
数据结构常量
'''
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

'''
节点常量
'''
NMAXNODENO = 2  #最大节点编号
NMAJORITY = (NMAXNODENO + 1)//2 + 1  #这里定义是严格大于1/2
NODENO = 0

'''
节点全局变量
'''
global roundNo #轮次编号
global roundFlag  #进入下一轮 L给P,A提示
global redisConnect

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
    提案编号为3位优先级+20(8<yyyymmdd>+6<hhmmss>+6<ms>)位Ins时间戳
    '''

    def __init__(self):
        self.priority = 0
        self.rejected = False
        self.propNo = ''
        self.instruction = input_instruction()

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
        global roundNo
        #准备prepare请求的内容
        self.Gen_PropNo()
        prepare_request = passed_instruction()
        prepare_request.type = TPROPOSAL_ACCEPTOR_1
        prepare_request.source = NODENO
        prepare_request.round = roundNo
        prepare_request.number = self.propNo
        prepare_request.accepted = False
        prepare_request.content = ''
        #向其他节点发送prepare请求
        for tgt in range(0,NMAXNODENO):
            if tgt != NODENO:
                prepare_request.target = tgt
                self.Pass_Instruction(prepare_request)

    def Propose(self):
        global roundNo
        #准备propose请求的内容
        propose_request = passed_instruction()
        propose_request.type = TPROPOSAL_ACCEPTOR_2
        propose_request.source = NODENO
        propose_request.round = roundNo
        propose_request.number = self.propNo
        propose_request.accepted = False
        propose_request.content = self.instruction
        #向其他节点发送propose请求
        for tgt in range(0,NMAXNODENO):
            if tgt != NODENO:
                propose_request.target = tgt
                self.Pass_Instruction(propose_request)

    def Listen_Response(self):
        '''
        监听Acceptor的回复消息,直到把该prepare的回复消息处理完
        如果得到大多数的同意,则进入Propose
        否则,避让,等待轮次结束
        '''
        acceptNum = 0
        if acceptNum >= NMAJORITY:
            self.rejected = False
        else: 
            self.rejected = True

    
    '''
    helper func
    '''
    def Gen_PropNo(self): #将整数priority和字符串timestamp合并
        strPriority = '%03d' % self.priority
        strTime = str(datetime.datetime.now())
        timeStamp = strTime[0:4]+strTime[5:7]+strTime[8:10]\
            +strTime[11:13]+strTime[14:16]+strTime[17:19]+strTime[20:26]
        strPriority += timeStamp
        self.propNo = strPriority
    
    def Pass_Instruction(self,passIns: passed_instruction):  #发送格式消息
        global sender
        message = passed2json(passIns)
        sender.produce(json.dumps(message))
        pass

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
    proposer = Proposer()
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
    '''
    创建一个连接,创建独立的消息队列
    '''
    global redisConnect
    redisConnect = redisInit(host='redis', port=6379)
    sender = MessageQueue(redisConnect,'sender','producer')
    pass

def main():
    Node_Initialize()
    Run_Threads()

if __name__ == '__main__':
    main()
