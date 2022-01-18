ARG CUDA_VERSION="11.0.3"
ARG OS_VERSION="ubuntu20.04"
FROM nvidia/cuda:${CUDA_VERSION}-base-${OS_VERSION}

RUN useradd --create-home \
    --home-dir /var/stanza-server \
    --shell /usr/sbin/nologin \
    --gid nogroup \
    --uid 1000 \
    stanza

RUN apt-get update -qq \
    && apt-get install -qq -y --no-install-recommends \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel

WORKDIR /opt/stanza-server
COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir \
    -r requirements.txt

COPY *.py ./

USER stanza:nogroup
WORKDIR /var/stanza-server
RUN mkdir -p /var/stanza-server/models

ENV STANZA_RESOURCES_DIR=/var/stanza-server/models
ENV STANZA_SERVER_LANGUAGES=de,en
ENV STANZA_SERVER_PIPELINE=tokenize,mwt,pos,lemma,ner

#prevent downloading stanza models on every restart
VOLUME ["/var/stanza-server/models"]

EXPOSE 8080

ENTRYPOINT ["/usr/bin/python3", "/opt/stanza-server/main.py"]
