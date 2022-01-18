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
import queue


class LanguageNotSupportedError(Exception):
    """Raised when the requested language is not supported"""
    pass


class PipelineTimeout(Exception):
    """Raised when no pipeline for the requested language is not available for a given time period"""
    pass


class ProcessingException(Exception):
    """Raised when processing the parsed text failed"""
    pass


class StanzaService:

    def __init__(self, analysis_processes, analysis_process_timeout):
        self.analysis_processes = analysis_processes
        self.analysis_process_timeout = analysis_process_timeout

    def __del__(self):
        """Ensures that all analysis processors are terminated"""
        for analysis_processors in self.analysis_processes.values():
            for analysis_processor in analysis_processors:
                # sending None as text is the termination signal
                analysis_processor.parent_con.send([None])

    def process(self, text, lang):
        # creating a pipeline seems to be expensive ... so we should cache them
        if lang not in self.analysis_processes:
            raise LanguageNotSupportedError()
        lang_analysis_processes = self.analysis_processes[lang]
        try:
            analysis_process = lang_analysis_processes.get(timeout=self.analysis_process_timeout)
            logging.info("got analysis process for language: '%s' (others available: %s)",
                         lang, lang_analysis_processes.qsize())
            try:
                analysis_process.parent_con.send(text)
                response = analysis_process.parent_con.recv()
                if "error" in response:
                    raise ProcessingException(response["error"])
                else:
                    return response["result"]
            finally:
                lang_analysis_processes.put(analysis_process)
                logging.info("put pipeline for language: '%s' back to the queue", lang)
        except queue.Empty:
            raise PipelineTimeout()
