FROM python:3.8

WORKDIR /usr/src/app

COPY ./src/* ./
RUN pip install --no-cache-dir -r ./requirements.txt

CMD [ "python", "-u", "main.py" ]