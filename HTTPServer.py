from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        if 'value' in query:
            value = query['value'][0]
            if value=='000000003':
                response='red'
            if value=='000000004':
                response='green'
            if value=='100000020':
                response='blue'
        else:
            response = 'No value provided'

        self.wfile.write(response.encode())

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

run()
