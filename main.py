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

# This is the webservice exposing functionality of the stanza service.

import logging
import os
import queue
import cherrypy
import stanza
from stanzaService import StanzaService
import analysisProcess

stanzaService = None


class StanzaWebService(object):


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def process(self):
        input_json = cherrypy.request.json
        return stanzaService.process(text=input_json["text"], lang=input_json["lang"])


# main
if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    languages = os.environ.get('STANZA_SERVER_LANGUAGES', 'en')
    default_pipeline = os.environ.get('STANZA_SERVER_PIPELINE', 'tokenize,mwt,pos,lemma,ner')
    timeout_str = os.environ.get('STANZA_SERVER_PIPELINE_TIMEOUT', "0")
    timeout = int(timeout_str) if timeout_str is not None else None
    analysis_process_timeout = timeout if timeout > 0 else None
    analysis_processes = {}
    if languages is not None:
        for lang in languages.split(','):
            stanza.download(lang)  # download the model
            pipeline = os.environ.get("STANZA_SERVER_PIPELINE_{}".format(lang.upper()), default_pipeline)
            count_str = os.environ.get("STANZA_SERVER_PIPELINE_{}_COUNT".format(lang.upper()), "1")
            count = int(count_str) if count_str is not None else 1
            if pipeline is not None:
                analysis_processes[lang] = queue.Queue(count)
                logging.info("Initialize %d analysis process%s for language '%s' with pipeline: %s",
                             count, "es" if count > 1 else "", lang, pipeline)
                for _ in range(count):
                    analysis_processes[lang].put(analysisProcess.AnalysisProcess(lang, pipeline))

    stanzaService = StanzaService(analysis_processes, analysis_process_timeout)

    config = {'server.socket_host': '0.0.0.0'}
    cherrypy.config.update(config)
    cherrypy.quickstart(StanzaWebService())
