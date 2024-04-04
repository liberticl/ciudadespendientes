FROM python:3.11-slim
COPY requirements.txt /

RUN pip3 install -r requirements.txt

RUN mkdir /code
WORKDIR /code
COPY . /code/
CMD ["python3", "server.py"]