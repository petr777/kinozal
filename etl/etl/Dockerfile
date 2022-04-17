FROM python:3.8.6-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

ENV HOME=/home/etl
RUN mkdir $HOME
WORKDIR $HOME

COPY . $HOME
RUN pip install -r requirements.txt


CMD ["python", "main.py"]