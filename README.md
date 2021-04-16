# Stanza Server

Provides a webservice exposing [Stanford Stanza](https://stanfordnlp.github.io/stanza/index.html) as a webservice.

# Usage:

First clone the repository

```
git clone git@bitbucket.org:redlinkgmbh/stanza-server.git
```

Build the docker image

```
docker build -t stanza-server .
```

Run the server via docker 

```
docker run -p 8080:8080 -v ~/stanza_resources/:/root/stanza_resources/ stanza-server
```

Note:

 * the volume for `/root/stanza_resources` prevents downloading models on every start

After this you can use the server under `http://localhost:8080/process`

## GPU/CUDA Support
To improve performance, stanza can use a Nvidia-CUDA on a GPU.
For CUDA-Support in docker, you have to [install `nvidia-docker2`](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker).
After that, start the container with gpu-support enabled:

```
docker run -p 8080:8080 --gpus all -v ~/stanza_resources/:/root/stanza_resources/ stanza-server
```

### Example Usage:

```
curl -X POST -H "content-type: application/json" \
    'http://localhost:8080/process' \
    -d '{"lang":"de","text":"Der Hauptsitz von Redlink ist in Salzburg"}'
```

and the response format:

```
{
  "sentences": [
    {
      "text": "Der Hauptsitz von Redlink ist in Salzburg",
      "tokens": [
        {
          "id": "1.0-3",
          "text": "Der",
          "start": 0,
          "end": 3
        },
        {
          "id": "2.4-13",
          "text": "Hauptsitz",
          "start": 4,
          "end": 13
        },
        {
          "id": "3.14-17",
          "text": "von",
          "start": 14,
          "end": 17
        },
        {
          "id": "4.18-25",
          "text": "Redlink",
          "start": 18,
          "end": 25,
          "ner": "S-ORG"
        },
        {
          "id": "5.26-29",
          "text": "ist",
          "start": 26,
          "end": 29
        },
        {
          "id": "6.30-32",
          "text": "in",
          "start": 30,
          "end": 32
        },
        {
          "id": "7.33-41",
          "text": "Salzburg",
          "start": 33,
          "end": 41,
          "ner": "S-LOC"
        }
      ],
      "words": [
        {
          "id": "1.0-3",
          "text": "Der",
          "token": "1.0-3",
          "pos": "DET",
          "xpos": "ART",
          "lemma": "der",
          "features": "Case=Nom|Definite=Def|Gender=Masc|Number=Sing|PronType=Art",
          "misc": "start_char=0|end_char=3"
        },
        {
          "id": "2.4-13",
          "text": "Hauptsitz",
          "token": "2.4-13",
          "pos": "NOUN",
          "xpos": "NN",
          "lemma": "Hauptsitz",
          "features": "Case=Nom|Gender=Masc|Number=Sing",
          "misc": "start_char=4|end_char=13"
        },
        {
          "id": "3.14-17",
          "text": "von",
          "token": "3.14-17",
          "pos": "ADP",
          "xpos": "APPR",
          "lemma": "von",
          "features": null,
          "misc": "start_char=14|end_char=17"
        },
        {
          "id": "4.18-25",
          "text": "Redlink",
          "token": "4.18-25",
          "pos": "PROPN",
          "xpos": "NE",
          "lemma": "Redlink",
          "features": "Case=Dat|Gender=Neut|Number=Sing",
          "misc": "start_char=18|end_char=25"
        },
        {
          "id": "5.26-29",
          "text": "ist",
          "token": "5.26-29",
          "pos": "AUX",
          "xpos": "VAFIN",
          "lemma": "sein",
          "features": "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin",
          "misc": "start_char=26|end_char=29"
        },
        {
          "id": "6.30-32",
          "text": "in",
          "token": "6.30-32",
          "pos": "ADP",
          "xpos": "APPR",
          "lemma": "in",
          "features": null,
          "misc": "start_char=30|end_char=32"
        },
        {
          "id": "7.33-41",
          "text": "Salzburg",
          "token": "7.33-41",
          "pos": "PROPN",
          "xpos": "NE",
          "lemma": "Salzburg",
          "features": "Case=Dat|Gender=Neut|Number=Sing",
          "misc": "start_char=33|end_char=41"
        }
      ]
    }
  ],
  "entities": [
    {
      "start": 18,
      "end": 25,
      "text": "Redlink",
      "type": "ORG",
      "tokens": [
        "4.18-25"
      ],
      "words": [
        "4.18-25"
      ]
    },
    {
      "start": 33,
      "end": 41,
      "text": "Salzburg",
      "type": "LOC",
      "tokens": [
        "7.33-41"
      ],
      "words": [
        "7.33-41"
      ]
    }
  ]
}
```

### License:

Free use of this software is granted under the terms of the Apache License Version 2.0.
See the [License](LICENSE.txt) for more details.

### Open Issues:

* Stanza can load models for languages (e.g. `stanza.download('en')`). I would like to have this configureable.
For now it only downloads the German and English models are downloaded when it starts. 
* Dependency annotations are not supported yet
* The analysis pipeline is currently hardcoded. One could make this configurable
* Concurrency: We need to sync the process method as stanza does not support concurrent analysis

