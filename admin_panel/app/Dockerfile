FROM python:3.8.6-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

ENV HOME=/home/app
RUN mkdir $HOME
WORKDIR $HOME

COPY . $HOME
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

ENTRYPOINT ["/home/app/entrypoint.sh"]