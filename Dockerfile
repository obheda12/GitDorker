FROM alpine:3.9
LABEL MAINTAINER Furkan SAYIM | furkan.sayim@yandex.com

RUN apk update && \
    apk upgrade

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN apk add git
RUN git clone https://github.com/obheda12/GitDorker.git /tmp/gitdorker

WORKDIR /tmp/gitdorker

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "GitDorker.py"]
