FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip3 install -r requirements.txt
RUN python3 -m nltk.downloader punkt

COPY . /

CMD python3 web_api.py

EXPOSE 5000
