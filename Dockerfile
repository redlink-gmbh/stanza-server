ARG CUDA_VERSION="10.1"
FROM nvidia/cuda:${CUDA_VERSION}-base

RUN apt-get update -qq \
    && apt-get install -qq -y --no-install-recommends \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel

COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir \
    -r requirements.txt

COPY *.py ./

#prevent downloading stanza models on every restart
VOLUME ["/root/stanza_resources"]

EXPOSE 8080

ENTRYPOINT ["python3", "main.py"]
