from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

# 假设这是服务器端保存的订单号和目的地的数据
order_destinations = {
    "0000000005": "成都",
    "0000000004": "天津",
    "0000000003": "上海",
    "0000000009": "上海",
    "1000000020": "上海"
}

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        if 'value' in query:
            if len(query['value'])>0:
                value = query['value'][0]
                if value=='000000003' or value=='000000005':
                    response="red"
                if value=='000000004' or value=='000000019':
                    response="green"
                if value=='100000020'or value=='000000009':
                    response="blue"
                else:
                    response = 'No value provided'

        self.wfile.write(response.encode())

def run_http_server_1(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

class RequestHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        # 解析请求数据
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        order_numbers = json.loads(post_data)
        
        # 查询订单号对应的目的地
        result = {}
        for order_number in order_numbers:
            if order_number in order_destinations:
                result[order_number] = order_destinations[order_number]
            else:
                result[order_number] = "not found"
        
        # 返回结果
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps(result).encode('utf-8')
        self.wfile.write(response)

def run_http_server_2():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()

if __name__=="__main__":
    # run_httpserver_1()
    run_http_server_2()
