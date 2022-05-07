from sender import sender
from redis_op import redisInit, MessageQueue
from multiprocessing import Pool
import time

redisConnect = redisInit(host='redis', port=6379)
senderQueue = MessageQueue(redisConnect, 'sender', 'consumer')

POOLNUMBER = 10

if __name__ == '__main__':
    pool = Pool(POOLNUMBER)

    while True:

        message = senderQueue.consume()
        if message == None:
            time.sleep(0.001)
        else:
            pool.apply_async(func=Sender, args=(message, ))
