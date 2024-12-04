FROM python:3.12.7

WORKDIR /

RUN mkdir credential
WORKDIR /app

COPY ./requirements.txt requirements.txt 


RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt 
RUN python -m spacy download ja_core_news_sm