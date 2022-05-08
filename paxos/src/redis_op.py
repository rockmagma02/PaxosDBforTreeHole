import redis
import redis_lock


def redisInit(host='redis', port=6379):
    """请在程序程序开始前, 使用该函数新建创建一个与 redis 的连接池, 后续使用消息队列和带互斥的共享内存时请传入该连接池

    Args:
        host (str, optional): redis 的 host. Defaults to 'redis'.
        port (int, optional): redis 的端口. Defaults to 6379.

    Returns:
        _type_: 一个 redis 数据库的连接池
    """
    pool = redis.ConnectionPool(host=host, port=port)
    return pool


class MessageQueue:
    """该类用于创建一个基于 redis 的消息队列, 使用唯一的标识 name 可以链接到 redis 中的对应的消息队列

        Args:
            connectionPool (ConnectionPool): 与redis建立连接的连接池, 使用函数 redisInit 创建
            name (str): 标识 redis 中需要使用的消息队列
            mode (str): producer(作为生产者向消息队列放入消息)/consumer(作为消费者处理消息队列内的内容)
    """

    def __init__(self, connectionPool, name, mode):
        self.__redis = redis.Redis(
            connection_pool=connectionPool, decode_responses=True)
        self.__key = name
        self.__mode = mode

        def produce(value):
            """向消息队列中放入消息

            Args:
                value (str): 放入消息, 支持字符串类型

            Returns:
                int: 当前消息队列当中的内容
            """
            length = self.__redis.lpush(self.__key, value)
            return length

        def consume():
            """取出消息队列中的内容

            Returns:
                str: 取出的消息队列中的内容, 注意, 如果队列为空, 则会阻塞2s后,取出None
            """
            return self.__redis.brpop(self.__key, 2)

        def consume_withoutBreaking():
            return self.__redis.rpop(self.__key)

        if mode == 'producer':
            self.produce = produce
        elif mode == 'consumer':
            self.consume = consume
            self.consume_withoutBreaking = consume_withoutBreaking

    def __len__(self):
        return self.__redis.llen(self.__key)

    def pushR(self, value):
        length = self.__redis.rpush(self.__key, value)
        return length

    @property
    def mode(self):
        return self.__mode

def generteMutex(pool, name):
    r = redis.Redis(connection_pool=pool, decode_responses=True)
    lock = redis_lock.Lock(r, name)
    return lock