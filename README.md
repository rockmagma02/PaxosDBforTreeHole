# PaxosDBforTreeHole

![GitHub](https://img.shields.io/github/license/rockmagma02/PaxosDBforTreeHole) ![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/rockmagma02/PaxosDBforTreeHole) ![GitHub release (latest by date)](https://img.shields.io/github/downloads/rockmagma02/PaxosDBforTreeHole/latest/total)

## Introduce

这是北京大学 2022 年春的算法设计与分析小班的小组 project，该 project 是我们小组在对于分布式算法的简单学习之后，基于 paxos 算法构建的基础“数据库”系统.

Paxos 算法得名于其原始论文中作者 Leslie Lamport 借以比喻算法运行过程的希腊小岛 Paxos. 当此文于 1998 年面世时, 由于其叙述方式为将此算法中多个进程的运行过程以 Paxos 小岛中议会决议的方式比喻写出, 相对较为晦涩, 因此并未得到广泛的理解.在此之后, 于 2001 年在 PODC 会议上, 作者应邀将此算法以更易懂的方式写出更简单的版本， 使得这一算法的影响面显著扩大.

本项目以 Leslie Lamport 于 2001 年撰写的简化叙述为基础, 结合关于 Paxos 算法核心内容的简单工程实践, 对 Paxos 算法的运行过程以及处理网络延迟、错序及丢失的方式进行阐述, 并对 Paxos 算法所不能较好处理的问题进行了进一步的讨论.

> 完整的介绍可以查看 [PDF版本的报告](https://github.com/rockmagma02/PaxosDBforTreeHole/blob/main/%E9%A1%B9%E7%9B%AE%E6%8A%A5%E5%91%8A.pdf)，以下部分重点介绍如何使用我们的代码

## Install

> 本项目基于 docker 构建，请确保您的设备上已经安装了 docker 和 docker-compose

### 本地测试

1. 下载，请使用以下命令：

```bash
git clone https://github.com/rockmagma02/PaxosDBforTreeHole.git
```

2. 确定需要使用的节点数量 $n$，然后将项目复制 $n$份
3. 修改每个节点文件夹中的节点 host
+ 在 `paxos/src/main.py` 下修改常量 `addresses` 和 `host` 前者需要记录所有节点的 host
+ 因为是在本地测试，请在 `docker-compose.yml` 中修改 nginx 的端口映射避免冲突
+ 请修改 `docker-compse.yml` 中 nginx 在 `out-net` 中的别名为相应的 host
4. 在每个节点运行代码

```bash
docker-compose up
```

## Usage

您可以使用 [client](https://github.com/rockmagma02/PaxosDBforTreeHole/releases/download/clinet/client.py) 在本地进行测试，这是一个简单的测试程序，请确保您的运行中的节点有一个对外暴露了 80 端口

## Api

以下是一段压力测试代码，您可以从中了解与数据库沟通的 api

### 写入数据

```python
import time

import hashlib

from datetime import datetime

from faker import Faker

  

# data = {'type': 'insert', 'table':'Account', 'data':{'mail': 'pku@edu.cn', 'passwordHash': str(hashlib.md5(b'111')), 'createDatetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}

  

import requests

import json

  

f = Faker()

dataList = []

for i in range(100):

    data = {'type': 'insert', 'table': 'Account', 'data': {'mail': f.email(

    ), 'passwordHash': f.md5(), 'createDatetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}

    dataList.append(json.dumps(data))

  
  

start_time = time.time()

  

for data in dataList:

    r = requests.post('http://127.0.0.1:80', data=data)

  

print(time.time() - start_time)
```

### 读取数据

```python
import requests

import time

from datetime import datetime

import json

  

params = {'table': 'HoleContent', 'index': 'treeId', 'value': 1}

  

content = {

    'content': 'hahha',

    'author': '田所浩二',

    'createTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')

}

data = {

    'type': 'insert',

    'table': 'HoleContent',

    'data': content  # key-value形式的数据

}

  

r = requests.post('http://127.0.0.1:80', data=json.dumps(data))

  

start_time = time.time()

for i in range(100):

    r = requests.get('http://127.0.0.1:80', params=params)

print(time.time() - start_time)
```

## 代码结构

+ backend：一个 uwsgi 服务器，用来与客户端沟通
+ db：构建数据库，存有数据库初始化命令
+ nginx：nginx 的默认配置文件
+ nodeinfo：一个 uwsgi 服务器，负责节点之间的沟通
+ paxos：
	+ acceptor.py：实现 acceptor 的功能
	+ dataType.py：规定和数据结构和数据格式转换函数
	+ database.py：封装数据库的调用函数
	+ executor.py：执行 paxos 算法的结果，保证了指令执行的顺序性
	+ learner.py：实现 learner 的功能
	+ mail_room.py：处理节点之间的消息，并且被动开启 paxos 算法轮次
	+ main.py：主程序入口，可以主动开启 paxos 算法轮次
	+ paxos.py：一次 paxos 算法执行的入口
	+ proposer.py：实现 proposer 的功能
	+ redis_op.py：实现 redis 功能的封装
+ redis：redis 的配置文件
+ sender：在节点之间发送消息

## Contributing

该项目只是一个课程作业，限于大家的时间和精力，我们并没有很好的完善项目，该项目难免存在各种恶性 bug，所以我们非常不建议您以我们的代码出发学习 paxos 算法或者将我们的项目应用于任何实际工作.

但我们很欢迎任何完善和改进的帮助

[提一个 Issue](https://github.com/rockmagma02/PaxosDBforTreeHole/issues) 或者提交一个 Pull Request。

 PaxosDBforTreeHole 遵循 [Contributor Covenant](http://contributor-covenant.org/version/1/3/0/) 行为规范

## Thanks
+ 感谢小组成员们的辛勤工作
+ 感觉小班老师的指导
+ 感谢小班助教的悉心指导
+ 感谢小班助教的手下留情（划掉）

## License
[MIT](https://github.com/rockmagma02/PaxosDBforTreeHole/blob/main/LICENSE) © Rock Magma
