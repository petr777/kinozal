FROM python:3.8.6-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV HOME=/src
RUN mkdir $HOME
WORKDIR $HOME

COPY . $HOME

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]