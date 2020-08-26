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
docker run -p 8080:8080 -v -v ~/stanza_resources/:/root/stanza_resources/ stanza-server
```

Note:

 * the volume for `/root/stanza_resources` prevents downloading models on every start

After this you can use the server under `http://localhost:8080/process`

### Example Usage:

```
curl -X POST -H "content-type: application/json" \
    'http://localhost:8080/process' \
    -d '{"lang":"de","text":"Das ist ein Test"}'
```

and the response format:

```
{
	"sentences": [{
		"text": "Das ist ein Test",
		"tokens": [{
			"id": [1],
			"text": "Das",
			"start": 0,
			"end": 3
		}, {
			"id": [2],
			"text": "ist",
			"start": 4,
			"end": 7
		}, {
			"id": [3],
			"text": "ein",
			"start": 8,
			"end": 11
		}, {
			"id": [4],
			"text": "Test",
			"start": 12,
			"end": 16
		}],
		"words": [{
			"id": 1,
			"lemma": "der",
			"pos": "PRON",
			"text": "Das",
			"token": [1],
			"features": "Case=Nom|Gender=Neut|Number=Sing|PronType=Dem",
			"misc": "start_char=0|end_char=3"
		}, {
			"id": 2,
			"lemma": "sein",
			"pos": "AUX",
			"text": "ist",
			"token": [2],
			"features": "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin",
			"misc": "start_char=4|end_char=7"
		}, {
			"id": 3,
			"lemma": "ein",
			"pos": "DET",
			"text": "ein",
			"token": [3],
			"features": "Case=Nom|Definite=Ind|Gender=Masc|Number=Sing|PronType=Art",
			"misc": "start_char=8|end_char=11"
		}, {
			"id": 4,
			"lemma": "Test",
			"pos": "NOUN",
			"text": "Test",
			"token": [4],
			"features": "Case=Nom|Gender=Masc|Number=Sing",
			"misc": "start_char=12|end_char=16"
		}]
	}]
}
```

### Open Issues:

* Currently CUDA is not supported in the current Docker image: See this 
[Stackoverflow Post](https://stackoverflow.com/questions/60718574/containerization-of-a-python-code-with-stanfordnlp-that-uses-gpu)
for a starting point.
* Stanza can load models for languages (e.g. `stanza.download('en')`). I would like to have this configureable.
For now it only downloads the German and English models are downloaded when it starts. 
* Dependency annotations are not supported yet
* The analysis pipeline is currently hardcoded. One could make this configurable 
