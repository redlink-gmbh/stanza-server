#  Copyright (c) 2021 Redlink GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import logging
import os
import queue

import stanza


class LanguageNotSupportedError(Exception):
    """Raised when the requested language is not supported"""
    pass

class PipelineTimeout(Exception):
    """Raised when no pipeline for the requested language is not available for a given time period"""
    pass


class StanzaService:

    __pipelines = {}
    __pipeline_timeout = None

    def __init__(self):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
        languages = os.environ.get('STANZA_SERVER_LANGUAGES')
        default_pipeline = os.environ.get('STANZA_SERVER_PIPELINE', None)
        pipeline_timeout_str = os.environ.get('STANZA_SERVER_PIPELINE_TIMEOUT', "0")
        pipeline_timeout = int(pipeline_timeout_str) if pipeline_timeout_str is not None else None
        self.__pipeline_timeout = pipeline_timeout if pipeline_timeout > 0 else None
        if languages is not None:
            for lang in languages.split(','):
                stanza.download(lang)  # download the model
                pipeline = os.environ.get("STANZA_SERVER_PIPELINE_{}".format(lang.upper()), default_pipeline)
                count_str = os.environ.get("STANZA_SERVER_PIPELINE_{}_COUNT".format(lang.upper()), "1")
                count = int(count_str) if count_str is not None else 1
                if pipeline is not None:
                    self.__pipelines[lang] = queue.Queue(count)
                    logging.info("Initialize %s pipelines for language '%s' pipeline=%s", count, lang, pipeline)
                    for _ in range(count):
                        self.__pipelines[lang].put(stanza.Pipeline(lang=lang, processors=pipeline))

    def process(self, text, lang):
        # creating a pipeline seems to be expensive ... so we should cache them
        lang_pipelines = self.__pipelines[lang]
        if lang_pipelines is None:
            raise LanguageNotSupportedError()
        try:
            nlp = lang_pipelines.get(timeout=self.__pipeline_timeout)  # max wait is 10sec
            logging.info("got pipeline (language: '%s' available: %s)", lang, lang_pipelines.qsize())
            try:
                return self.map_annotations(nlp(text))
            finally:
                lang_pipelines.put(nlp)
                logging.info("put pipeline for language: '%s' back to the queue", lang)
        except queue.Empty:
            raise PipelineTimeout()

    # TODO: add support for dependency parsing features
    def map_annotations(self, annotations):
        return {
            "sentences": [self.map_sentence(sentence) for sentence in annotations.sentences],
            "entities": [self.map_entity(entity) for entity in annotations.entities]
        }

    def map_sentence(self, s):
        sentence = {
            "text": s.text,
            "tokens": [self.map_token(token) for token in s.tokens],
            "words": [self.map_word(word) for word in s.words]
        }
        try:
            sentence["sentiment"] = s.sentiment
        except AttributeError:
            pass
        return sentence

    def map_token(self, t):
        token = {
            "id": self.token_id(t),
            "text": t.text,
            "start": t.start_char,
            "end": t.end_char,
        }
        try:
            if t.ner != "O":
                token["ner"] = t.ner
        except AttributeError:
            pass
        return token

    def map_word(self, w):
        word = {
            "id": self.word_id(w),
            "text": w.text,
            "token": self.token_id(w.parent),
        }
        # NOTE:
        # * pos/upos hold the universal POS tags (https://universaldependencies.org/u/pos/)
        # * xpos hold the model specific POS tags (see https://stanfordnlp.github.io/stanza/available_models.html)
        # We keep both to allow clients to use upos as a base line but allow for more precise mappings
        # for specific languages/models
        try:  # only present if the pos processor is in the pipeline
            word["pos"] = w.pos
        except AttributeError:
            pass
        try:  # only present if the pos processor is in the pipeline
            word["xpos"] = w.xpos
        except AttributeError:
            pass
        try:  # only present if the lemma processor is in the pipeline
            word["lemma"] = w.lemma
        except AttributeError:
            pass
        try:
            word["features"] = w.feats
        except AttributeError:
            pass
        try:
            word["misc"] = w.misc
        except AttributeError:
            pass
        return word

    def map_entity(self, e):
        entity = {
            "start": e.start_char,
            "end": e.end_char,
            "text": e.text,
            "type": e.type,
        }
        t_ref = []
        for t in e.tokens:
            t_ref.append(self.token_id(t))
        entity["tokens"] = t_ref

        w_ref = []
        for w in e.words:
            w_ref.append(self.word_id(w))
        entity["words"] = w_ref
        return entity

    @staticmethod
    def offset_id(t):
        return f"{t.start_char}-{t.end_char}"

    # The ID of a token is built out of the index of the token in the sentence
    # (a tupel as this reports multi-word tokens on the same index with a sub
    # index for sub-tokens) as well as the start/end offset if the token
    def token_id(self, t):
        index_id = "-".join([str(index) for index in t.id])
        return f"{index_id}.{self.offset_id(t)}"

    # The ID of a word is built out of the index of the token in the sentence
    # as well as the start/end offset if the token
    def word_id(self, w):
        return f"{w.id}.{self.offset_id(w.parent)}"