import requests
import json
import urllib.request

class HTTPClient():
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    def call(self, param):
        Params={'id':''}
        Params['id']=param
        response = requests.post(self.url, params=Params, headers=self.headers)
        return response
def httptets1():
    # url = 'http://192.168.0.100:8088'
    # params = {'id': '000000003'}
    # headers = {'User-Agent': 'Mozilla/5.0'}

    # response = requests.get(url, params=params, headers=headers)
    # print(response.text)
    HTTPclient=HTTPClient('http://192.168.0.100:8092/getDst')
    orderID="000000004"
    print(f"orderID={orderID}")
    ret=HTTPclient.call(orderID)
    print(f'DBClinet response:{ret}')
    dst=ret.content.decode()
    print(f"put to {dst}")
    # ret=HTTPclient.call('000000004')
    # print(ret)
    print(ret.content.decode())

def httptest2():


    # 要查询的订单号列表
    order_numbers = ["0000000005", "0000000004", "0000000003", "0000000009","1000000020"]

    # 构造请求数据
    data = json.dumps(order_numbers).encode('utf-8')

    # 发送POST请求
    req = urllib.request.Request(url='http://localhost:8000', data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as f:
        response = f.read()

    # 处理响应数据
    result = json.loads(response)
    for order_number, destination in result.items():
        print(order_number, destination)

if __name__=="__main__":
    # httptets1()
    httptest2()