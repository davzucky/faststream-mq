FROM mcr.microsoft.com/devcontainers/python:3.12

ENV MQ_FILE_PATH=/opt/mqm
ENV LD_LIBRARY_PATH=/opt/mqm/lib64

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY scripts/install-mq-client.sh /tmp/install-mq-client.sh
RUN bash /tmp/install-mq-client.sh && rm /tmp/install-mq-client.sh
