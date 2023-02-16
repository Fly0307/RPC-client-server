import requests
import json
import sys
import random
import time
import threading

#HTTP client
class HTTPClient():
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    def call(self, param):
        Params={'value':param}
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

def clientcode():
    # 定义多个client客户端分别和机械臂通信
    # url = "http://localhost:9030" 替换为端地址
    Armclient_1 = RPCClient('http://192.168.0.102:9030')
    DBClient=HTTPClient('http://192.168.0.103:8000')
    # Armclient_2 = RPCClient('URL')
    # Armclient_3 = RPCClient('URL')
    # Armclient_4 = RPCClient('URL')
    # 启动机械臂服务
    response = Armclient_1.call('LoadFunc', [7],)
    print(response)
    response = Armclient_1.call('StartFunc', [])
    print(response)
    time.sleep(1)
    while True:
        response = Armclient_1.call('GetOrderId', [])
        print(response)
        print(response[0])
        print(response[1])
        if response[0]:
            ret=DBClient.call(response[1])
            print(ret.text)
            response = Armclient_1.call('CargoPlacement', [ret.text])
            print(response)
        else:
            print(response)
        break

# 0未识别未抓取  1抓取阶段
# 2 放置阶段
ArmRuning_1=0
#定义一个全局变量列表,可以作为两个机械臂组的‘锁’
IsFree=[True,True]

#判断机械臂组是否已经完成一轮抓取，即当前状态是否为0
def ArmPi_free(ArmPiClients):
    num=len(ArmPiClients)
    isFree=False
    #循环等待该组机械臂均为空闲状态
    while not isFree:
        for i in range(num):
            state=ArmPiClients[i].call('ArmHeartbeat',[True])
            if state!=0:
                isFree=False
                break
        isFree=True
    return isFree

def ArmPi_catch(Armclient):
    Armclients=[Armclient]
    while True:
        #判断机械臂是否空闲，空闲则开始抓取
        if not ArmPi_free(Armclients):
            continue
        response = Armclient.call('GetOrderId', [])
        
        print(response)
        print(response[0])
        print(response[1])
        state=Armclient.call('ArmHeartbeat',[True])
        print(state)
        if response[1]=='null':
            time.sleep(1)
            count+=1
            continue
        if response[0]:
            ret=DBClient.call(response[1])
            print(ret.text)
            response = Armclient.call('CargoPlacement', [ret.text])
            print(response)
        else:
            print(response)
        if count>5:
            break
        count=0

# Usage:
if __name__ == '__main__':
    # 定义多个client客户端分别和机械臂通信
    # url = "http://localhost:9030" 替换为端地址
    Armclient_1 = RPCClient('http://192.168.0.102:9030')
    DBClient=HTTPClient('http://192.168.0.103:8000')
    # Armclient_2 = RPCClient('URL')
    # Armclient_3 = RPCClient('URL')
    # Armclient_4 = RPCClient('URL')
    # 启动机械臂服务
    response = Armclient_1.call('LoadFunc', [7],)
    print(response)
    response = Armclient_1.call('StartFunc', [])
    print(response)
    time.sleep(1)
    count=0
    ArmPi_catch(Armclient_1)
    # while True:
    #     response = Armclient_1.call('GetOrderId', [])
        
    #     print(response)
    #     print(response[0])
    #     print(response[1])
    #     state=Armclient_1.call('ArmHeartbeat',[True])
    #     print(state)
    #     if response[1]=='null':
    #         time.sleep(1)
    #         count+=1
    #         continue
    #     if response[0]:
    #         ret=DBClient.call(response[1])
    #         print(ret.text)
    #         response = Armclient_1.call('CargoPlacement', [ret.text])
    #         print(response)
    #     else:
    #         print(response)
    #     if count>5:
    #         break
    #     count=0
    # my_thread = threading.Thread(target = my_code, daemon=True).start()
    # keyboard.wait("esc")
    sys.exit()