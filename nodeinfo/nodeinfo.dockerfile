FROM python:3.8

WORKDIR /usr/src/app

COPY ./src/* ./

RUN pip install -r ./requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD [ "uwsgi", "--ini", "nodeinfo.ini" ]
