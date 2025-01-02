FROM alpine:3.9
LABEL MAINTAINER Furkan SAYIM | furkan.sayim@yandex.com

# Update and install dependencies
RUN apk update && \
    apk upgrade && \
    apk add --no-cache python3 git && \
    python3 -m ensurepip && \
    pip3 install --upgrade pip setuptools && \
    rm -r /usr/lib/python*/ensurepip && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip; fi && \
    if [ ! -e /usr/bin/python ]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

# Copy the current directory into the container
COPY . /gitdorker

# Set the working directory
WORKDIR /gitdorker

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Set the entrypoint for running GitDorker
ENTRYPOINT ["python3", "GitDorker.py"]
