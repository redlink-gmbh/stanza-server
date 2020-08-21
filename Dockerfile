from python:3.6.4-slim-jessie

RUN pip install stanza
RUN pip install CherryPy

COPY stanzaService.py .
COPY main.py .

EXPOSE 8080

ENTRYPOINT ["python", "main.py"]