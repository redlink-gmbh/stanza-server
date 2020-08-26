from contextlib import redirect_stderr

import stanza


class LanguageNotSupportedError(object):
    """Raised when the requested language is nor supported"""
    pass


class StanzaService:

    pipelines = {}

    def __init__(self):
        stanza.download('de')  # download German model
        stanza.download('en')  # download English model
        self.pipelines["de"] = stanza.Pipeline(lang="de", processors='tokenize,mwt,pos,lemma,ner');
        self.pipelines["en"] = stanza.Pipeline(lang="en", processors='tokenize,mwt,pos,lemma,ner');

    def process(self, text, lang):
        # creating a pipeline seams to be expensive ... so we should cache them
        nlp = self.pipelines.get(lang)
        if nlp != None:
            return self.map_annotations(nlp(text))
        else:
            raise LanguageNotSupportedError

    # TODO: add support for dependency parsing feautres
    def map_annotations(self, annotations):
        return {
            "sentences": list(map(self.map_sentence, annotations.sentences)),
            "entities": list(map(self.map_entity, annotations.entities))}

    def map_sentence(self, s):
        sentence = {
            "text": s.text,
            "tokens": list(map(self.map_token, s.tokens)),
            "words": list(map(self.map_word, s.words))
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
        try:  # only present if the pos processor is in the pipeline
            word["pos"] = w.pos
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
        return "-".join(map(str,[t.start_char, t.end_char]))

    # The ID of a token is built out of the index of the token in the sentence
    # (a tupel as this reports multi-word tokens on the same index with a sub
    # index for sub-tokens) as well as the start/end offset if the token
    def token_id(self, t):
        return ".".join(["-".join(map(str,t.id)), self.offset_id(t)])

    # The ID of a word is built out of the index of the token in the sentence
    # as well as the start/end offset if the token
    def word_id(self, w):
        return ".".join([str(w.id), self.offset_id(w.parent)])
