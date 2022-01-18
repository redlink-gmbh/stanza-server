# Stanza Server

Provides a webservice exposing [Stanford Stanza](https://stanfordnlp.github.io/stanza/index.html) as a webservice.

## Build

First clone the repository

```
git clone git@github.com:redlink-gmbh/stanza-server.git
```

Build the docker image

```
docker build -t stanza-server .
```

Run the server via docker 

```
docker run -p 8080:8080 -v ~/stanza_resources:/var/stanza-server/models stanza-server
```

**Note:**

 * the volume for `/var/stanza-server/models` prevents downloading models on every start.
   Make sure to set the permissions for the volume accordingly (`uid=1000/gid=65534`)

After this you can use the server under `http://localhost:8080/process`

## Configuration

The server can be configured using environment variables

```
# comma separated list of languages (default: en)
STANZA_SERVER_LANGUAGES=en,de
# coma separated list of stanza processors as used by default
# for any languages (default: tokenize,mwt,pos,lemma,ner)
STANZA_SERVER_PIPELINE=tokenize,mwt,pos,lemma,ner
```
In addition language specific pipeline can be configured. 
```
# STANZA_SERVER_PIPELINE_{LANG}
# e.g. to configure a pipeline for de use
STANZA_SERVER_PIPELINE_DE=tokenize,mwt,pos,lemma,ner
```
The server also supports loading a langauge model multiple times
to allow for parallel processing. 

__NOTE: This only provides performance gains if GPU/CUDA support is active.__
When running on a CPU processing will be much slower if this feature is active
 ```
# use STANZA_SERVER_PIPELINE_{LANG}_COUNT to load a model for a 
# language multiple times
# e.g. to load the German model 4 times use
STANZA_SERVER_PIPELINE_DE_COUNT=4
```

## GPU/CUDA Support
To improve performance, stanza can use a Nvidia-CUDA on a GPU.
For CUDA-Support in docker, you have to [install `nvidia-docker2`](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker).
After that, start the container with gpu-support enabled:

```
docker run -p 8080:8080 --gpus all -v ~/stanza_resources/:/root/stanza_resources/ stanza-server
```

__NOTE:__ The current Version of the Stanza Server requires Python 3.8 what
forces the use of CUDA 11+ and ubuntu 20. The versions referenced in the Dockerfile
represent the lower bound. The server was also tested with CUDA 11.4.3

## Example Usage

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

## License:

Free use of this software is granted under the terms of the Apache License Version 2.0.
See the [License](LICENSE.txt) for more details.

## Open Issues:

* Dependency annotations are not supported yet

