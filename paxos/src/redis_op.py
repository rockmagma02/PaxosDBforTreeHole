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
    def __init__(self, connectionPool, name, mode):
        self.__redis = redis.Redis(
            connection_pool=connectionPool, decode_responses=True)
        self.__key = name
        self.__mode = mode

        def produce(value):
            length = self.__redis.lpush(self.__key, value)
            return length

        def consume():
            return self.__redis.rpop(self.__key)

        if mode == 'producer':
            self.produce = produce
        elif mode == 'consumer':
            self.consume = consume

    def __len__(self):
        return self.__redis.llen(self.__key)

    @property
    def mode(self):
        return self.__mode


class MutexVar:
    def __init__(self, connectionPool, name, timeout):
        self.__redis = redis.Redis(
            connection_pool=connectionPool, decode_responses=True)
        self.__key = name
        self.__lockKey = 'lock' + name
        self.__timeout = timeout

        self.__lock = redis_lock.Lock(self.__redis, self.__lockKey)

    def set_withBlocking(self, value):
        if self.__lock.acquire():
            self.__redis.set(self.__key, value)
            return True

    def set_withBlockingTimeout(self, value):
        if self.__lock.acquire(timeout=timeout):
            self.__redis.set(self.__key, value)
            return True
        else:
            return False

    def set_Nonblocking(self, value):
        if self.__lock.acquire(blocking=False):
            self.__redis.set(self.__key, value)
            return True
        else:
            return False

    def get(self):
        return self.__redis.get(self.__key)
