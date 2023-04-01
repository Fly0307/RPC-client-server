import random
import json
from HTTPClient import *
import requests
from collections import defaultdict
from ConditionLock import *
import sys

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

def demo_clients_1():
    # Armclient_1 = RPCClient('http://192.168.0.104:9030')
    Armclient_2 = RPCClient('http://192.168.0.102:9030')
    # Armclient_3 = RPCClient('http://192.168.0.106:9030')
    response = Armclient_2.call('LoadFunc', [8],)
    print(f'LoadFunc{response}')
    response = Armclient_2.call('StartFunc', [])
    print(f'StartFunc{response}')
    res=Armclient_2.call('CargoPlacement', [['000000005',"成都"]])
    print(f"CargoPlacement res={res}")
    
# Usage:
if __name__ == '__main__':
    # 定义多个client客户端分别和机械臂通信
    demo_clients_1()
    # ArmPi_catch(Armclient_1,DBClient)
    sys.exit()