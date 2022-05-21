import pymysql
from dbutils.pooled_db import PooledDB
import datetime
import sys
import logging
import time
import json

logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)


def dbInit(host, username, password, database, port=3306, connectionNUm=5):
    """创建与数据库的连接池

    Args:
        host (str): 数据库的 host
        username (str): 访问数据库的 username
        password (str): 访问数据库的密码
        database (str): 需要连接的数据库名
        port (int, optional): 数据库的端口. Defaults to 3306.
        connectionNUm (int, optional): 连接池中最少的连接数量. Defaults to 5.

    Returns:
        pool: 创建好的连接池
    """
    logging.info('try to connect to database')
    while True:
        try:
            dbPool = PooledDB(pymysql, connectionNUm, host=host,
                              user=username, passwd=password, db=database, port=port)
            logging.info('connect db successfully')
            return dbPool
            break
        except Exception as e:
            print(e)
            logging.info('db is not exists, try again')
            time.sleep(1)


class Ins2Sql:
    def insert(ins):
        """将插入指令转换为sql指令

        Args:
            ins (dict): Dict 格式的指令 {'type':'insert', 'table': , 'data':{index1:value1, index2:value2, ...}}

        Returns:
            str: sql语句
        """
        data = ins['data']
        index = ', '.join(map(str, data.keys()))
        values = map(str, data.values())
        values = map(lambda x: "'"+x+"'", values)
        values = ', '.join(values)
        sql = f"insert into {ins['table']}({index}) values({values});"
        return sql

    def update(ins):
        pass

    def select(ins):
        """讲选择数据的指令转换为sql语句

        Args:
            ins (dict): Dict 格式的指令 {'type':'select', 'table': , 'data':{index1:value1, index2:value2, ...}}

        Raises:
            TypeError: ins 格式不能正常解析

        Returns:
            str: sql语句
        """
        data = ins['data']
        index = list(data.keys())
        value = list(data.values())
        if len(index) == 1:
            sql = f"select * from {ins['table']} where {index[0]} = '{value[0]}';"
        elif len(index) > 1:
            preSql = f"{index[0]} = '{value[0]}'"
            for i in range(1, len(index)):
                preSql += f" and {index[i]} = '{value[i]}'"
            sql = f"select * from {ins['table']} where " + preSql + ";"
        else:
            raise TypeError('ins is wrong')
        return sql


def dbProcess(pool, insList):
    sql = ''
    for ins in insList:
        if ins['type'] == 'insert':
            sql += Ins2Sql.insert(ins)
        elif ins['type'] == 'update':
            sql += Ins2Sql.update(ins)
        elif ins['type'] == 'select':
            sql += Ins2Sql.select(ins)
    con = pool.connection()
    cursor = con.cursor()
    cursor.execute(sql)
    con.commit()
    res = cursor.fetchall()
    cursor.close()
    con.close()
    return res
