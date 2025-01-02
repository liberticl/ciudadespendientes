FROM python:3.11-slim
COPY requirements.txt /

RUN pip3 install -r requirements.txt

RUN mkdir /code
WORKDIR /code
COPY . /code/
CMD ["gunicorn", "-w", "4", "--timeout", "120", "app.server:app", "-p", "8080:8080", "--bind", "0.0.0.0"]
