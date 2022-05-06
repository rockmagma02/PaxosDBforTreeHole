import pymysql
import datetime
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class DatabaseControl:
    def __init__(self, host, username, passward, database, tableName, port=3306):
        self._host = host
        self._username = username
        self._password = passward
        self._database = database
        self._tableName = tableName
        self._port = port

        self._connection = pymysql.connect(
            host=self._host,
            port=self._port,
            user=self._username,
            passwd=self._password,
            db=self._database,
            cursorclass=pymysql.cursors.DictCursor
        )

        cursor = self._connection.cursor()
        sql = 'use {};'.format(self._database)
        cursor.execute(sql)
        self._connection.commit()

        cursor = self._connection.cursor()
        sql = 'desc {};'.format(self._tableName)
        cursor.execute(sql)
        self._connection.commit()
        self._structure = cursor.fetchall()

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def username(self):
        return self._username

    @property
    def database(self):
        return self._database

    @property
    def tableName(self):
        return self._tableName

    @property
    def structure(self):
        return self._structure


class DatabaseReadControl(DatabaseControl):
    def select(self, idx):
        cursor = self._connection.cursor()
        sql = f'select * from {self.tableName} where id={idx};'
        cursor.execute(sql)
        self._connection.commit()
        return cursor.fetchall()[0]

    def searchByChar(self, index, condition):
        cursor = self._connection.cursor()
        sql = f"select * from {self.tableName} where {index} = '{condition}';"
        print(sql)
        cursor.execute(sql)
        self._connection.commit()
        return cursor.fetchall()


class DatabaseWriteControl(DatabaseReadControl):
    def insert(self, data):
        cursor = self._connection.cursor()
        keys = ', '.join(map(str, data.keys()))
        values = map(str, data.values())
        values = map(lambda x: "'"+x+"'", values)
        values = ', '.join(values)
        sql = f'insert into {self.tableName}({keys}) values({values});'
        cursor.execute(sql)
        self._connection.commit()

    def delete(self, idx):
        pass

    def update(self, idx, data):
        pass

