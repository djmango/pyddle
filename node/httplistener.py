""" listener """

# imports
import json
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

from handshake import exchangeKeyRespond


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        f = "deeed"
        self.wfile.write(f)

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # set headers and respond with status code
        self._set_headers()
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.end_headers()

        # parse data
        data = json.loads(self.data_string)
        print(data["publicKey"])
        print(self.client_address)
        print(exchangeKeyRespond(self.client_address, data["publicKey"]))
        self.wfile.write(bytes(exchangeKeyRespond(self.client_address, data["publicKey"]), "utf-8"))
        return


def run(server_class=HTTPServer, handler_class=S, port=8081):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()
