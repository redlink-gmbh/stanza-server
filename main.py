# This is the webservice exposing functionality of the stanza service.

import json
import cherrypy as cherrypy
import stanzaService

p = stanzaService.StanzaService()


class StanzaWebService(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def process(self):
        input_json = cherrypy.request.json
        return p.process(text=input_json["text"], lang=input_json["lang"])


# main
if __name__ == '__main__':
    config = {'server.socket_host': '0.0.0.0'}
    cherrypy.config.update(config)
    cherrypy.quickstart(StanzaWebService())
