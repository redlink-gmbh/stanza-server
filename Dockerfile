from python:3.6.4-slim-jessie

RUN pip install stanza
RUN pip install CherryPy

COPY stanzaService.py .
COPY main.py .

#prevent downloading stanza models on every restart
VOLUME ["/root/stanza_resources"]

EXPOSE 8080

ENTRYPOINT ["python", "main.py"]