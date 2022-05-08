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
                str: 取出的消息队列中的内容, 注意, 如果队列为空, 取出None
            """
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
    """ 声明或链接一个存在于 redis 中的带有互斥锁的共享变量, 其类型是str

        Args:
            connectionPool (ConnectionPool): 与redis建立连接的连接池, 使用函数 redisInit 创建
            name (str): 变量名
            timeout (int): 使用 set_withBlockingTimeout() 时最多阻塞时间

    """

    def __init__(self, connectionPool, name, timeout):
        self.__redis = redis.Redis(
            connection_pool=connectionPool, decode_responses=True)
        self.__key = name
        self.__lockKey = 'lock' + name
        self.__timeout = timeout

        self.__lock = redis_lock.Lock(self.__redis, self.__lockKey)

    def set_withBlocking(self, value):
        """ 设置变量的值, 进行设置时会首先 require 该变量的锁, 且使用 Blocking 的方式, 也就是请求锁的线程会直到拿到锁为止再继续执行, 否则一直阻塞

        Args:
            value (str): 设置的变量内容

        Returns:
            boolean: 设置成功后, 会返回 True
        """
        if self.__lock.acquire():
            self.__redis.set(self.__key, value)
            return True

    def set_withBlockingTimeout(self, value):
        """ 设置变量的值, 进行设置时会首先 require 该变量的锁, 且使用 Blocking with Timeout 的方式, 也就是请求锁的线程会直到拿到锁为止再继续执行, 或者在超时后放弃 require, 否则阻塞

        Args:
            value (str): 设置的变量内容

        Returns:
            boolean: 设置成功后, 会返回 True
        """
        if self.__lock.acquire(timeout=timeout):
            self.__redis.set(self.__key, value)
            return True
        else:
            return False

    def set_Nonblocking(self, value):
        """ 设置变量的值, 进行设置时会首先 require 该变量的锁, 且使用 Non-Blocking 的方式, 也就是请求锁的线程拿不到锁会返回 False

        Args:
            value (str): 设置的变量内容

        Returns:
            boolean: 设置成功后, 会返回 True, 否则返回 False
        """
        if self.__lock.acquire(blocking=False):
            self.__redis.set(self.__key, value)
            return True
        else:
            return False

    def get(self):
        """取得变量的值

        Returns:
            str: 变量的值
        """
        return self.__redis.get(self.__key)

    def delV(self):
        """强制删除该变量, 注意删除后, 其他线程也访问不到该变量
        """
        self.__redis.delete(self.__key)
        if self.__lock.locked():
            self.__lock.release()
        del self


def generteMutex(pool, name):
    r = redis.Redis(connection_pool=pool, decode_responses=True)
    lock = redis_lock.Lock(r, name)
    return lock