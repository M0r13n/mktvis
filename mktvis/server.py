from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from urllib.parse import parse_qs, urlparse

from mktvis.collector import COLLECTOR


def _encode_json(json_dict):
    string = json.dumps(json_dict)
    return string.encode('utf-8')

def _bake_output(collector):
    """Bake output for metrics output."""

    headers = [
        ('Content-Type', 'application/json'), 
        ('Access-Control-Allow-Origin', '*'), 
        ]

    response = collector.collect()
    output = _encode_json(response)
    return '200 OK', headers, output


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler that returns the connections currently opened by the routerboard"""

    collector = COLLECTOR

    def do_GET(self) -> None:
        # Prepare parameters - Do I even need them?
        _ = parse_qs(urlparse(self.path).query)

        # Bake output
        status, headers, output = _bake_output(self.collector)

        # Return output
        self.send_response(int(status.split(' ')[0]))
        for header in headers:
            self.send_header(*header)
        self.end_headers()
        self.wfile.write(output)


class ExportProcessor:

    @staticmethod
    def run(server_class=HTTPServer, handler_class=MetricsHandler, port=None):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()
