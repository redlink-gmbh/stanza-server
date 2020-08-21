import stanza

class StanzaService:
    def __init__(self):
        stanza.download('de')  # download German model

    def process(self, text, lang):
        nlp = stanza.Pipeline(lang=lang, processors='tokenize,mwt,pos,lemma')
        return self.convertStanzaResults(nlp(text))

    #TODO: add support for remaining stanza feautres
    def convertStanzaResults(self, anno):
        result = {}
        sentences = []
        result["sentences"] = sentences
        for s in anno.sentences:
            sentence = {
                "text": s.text
            }
            tokens = []
            sentence["tokens"] = tokens
            for t in s.tokens:
                token = {
                    "id": t.id,
                    "text": t.text,
                    "start": t.start_char,
                    "end": t.end_char,
                }
                tokens.append(token)
            words = []
            sentence["words"] = words
            for w in s.words:
                word = {
                    "id": w.id,
                    "lemma": w.lemma,
                    "pos": w.pos,
                    "text": w.text,
                    "token": w.parent.id,
                    "features": w.feats,
                    "misc": w.misc,
                }
                words.append(word)
            sentences.append(sentence)
        return result

