FROM xshuden/alppython3
LABEL MAINTAINER furkan.sayim@yandex.com

RUN git clone --depth=1 'https://github.com/obheda12/GitDorker.git' /tmp/gitdorker

WORKDIR /tmp/gitdorker
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "GitDorker.py"]
