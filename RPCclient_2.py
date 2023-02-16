import requests
import json
import random
import time

#HTTP client
class HTTPClient():
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    def call(self, param):
        Params={'id':''}
        Params['id']=param
        response = requests.get(self.url, params=Params, headers=self.headers)
        return response
        

# RPC client
class RPCClient_1:
    def __init__(self, url):
        self.url = url
        self.headers = {'Content-type': 'application/json'}

    def call(self, rpcMethod, rpcParams):
        payload = {
            'method': rpcMethod,
            'params': rpcParams,
            'jsonrpc': '2.0',
            'id': 0
        }
        response = requests.post(self.url, data=json.dumps(
            payload), headers=self.headers).json()
        return response.get('result')


class RPCClient:
    def __init__(self, url):
        self.url = url
        self.headers = {'Content-type': 'application/json'}

    def call(self, rpcMethod, rpcParams):
        id = random.randint(10**12, 10**13-1)
        payload = {
            'method': rpcMethod,
            'params': rpcParams,
            'jsonrpc': '2.0',
            'id': id
        }
        response = requests.post(self.url, data=json.dumps(
            payload), headers=self.headers).json()
        return response.get('result')


# Usage:
if __name__ == '__main__':
    # 定义多个client客户端分别和机械臂通信
    # url = "http://localhost:9030" 替换为端地址
    Armclient_1 = RPCClient('http://192.168.0.102:9030')
    # DBClient=HTTPClient('http://192.168.0.100:8088')
    # Armclient_2 = RPCClient('URL')
    # Armclient_3 = RPCClient('URL')
    # Armclient_4 = RPCClient('URL')
    # 启动机械臂服务
    # response = Armclient_1.call('LoadFunc', [7],)
    # print(response)
    # response = Armclient_1.call('StartFunc', [])
    # print(response)
    # time.sleep(1)
    # response = Armclient_1.call('GetOrderId', [])
    # print(response)
    # print(response[0])
    response = Armclient_1.call('CargoPlacement', ['red'])
    # print(response[1])
    # if response[0]:
    #     ret=DBClient.call(response[1])
    #     print(ret.text)
    #     response = Armclient_1.call('CargoPlacement', [ret.text])
    #     print(response)
    # else:
    #     print(response)
    # 调用识别接口

    # print(result)
