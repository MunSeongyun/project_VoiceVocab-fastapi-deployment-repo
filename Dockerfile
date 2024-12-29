FROM python:3.12.7

WORKDIR /

RUN mkdir credential
WORKDIR /app

COPY ./requirements.txt requirements.txt 

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt 
RUN python -m spacy download ja_core_news_sm
RUN python -m spacy download en_core_web_md
RUN python -m spacy download en

ARG CACHE_BUSTER=1
ENV CACHE_BUSTER=${CACHE_BUSTER}
COPY ./ /app
RUN cat main.py

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8080", "--timeout", "0"]
