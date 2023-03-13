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
        Params={'id':''}
        Params['id']=param
        response = requests.post(self.url, params=Params, headers=self.headers)
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
    DBClient=HTTPClient('http://192.168.0.100:8092/getDst')
    # DBClient=HTTPClient('http://192.168.0.103:8000')
    # Armclient_2 = RPCClient('URL')
    # Armclient_3 = RPCClient('URL')
    # Armclient_4 = RPCClient('URL')
    # 启动机械臂服务
    response = Armclient_1.call('LoadFunc', [2],)
    print(f'LoadFunc{response}')
    response = Armclient_1.call('StartFunc', [])
    print(f'StartFunc{response}')
    time.sleep(1)
    while True:
        response = Armclient_1.call('', [])
        print(f'GetOrderId{response}')
        print(response[0])
        print(response[2])
        if response[0]:
            ret=DBClient.call(response[2])
            print(ret.text)
            response = Armclient_1.call('CargoPlacement', [ret.text])
            print(response)
        else:
            print(response)
        break

# 0 未识别   3 已经抓取悬空
# 1 抓取阶段 2 放置阶段
ArmRuning_1=0
#定义一个全局变量列表,可以作为两个机械臂组的‘锁’，
# 为正在抓取阶段(1)则为False，
# 为放置阶段(2)、悬空阶段(3)、未识别(0)则True,允许另一组行动
IsFree=[False,False]
# 创建一个线程锁
lock = threading.Lock()

#传入两组机械臂的Url,修改当前
def ArmPis_free(ClientUrls_1,ClientUrls_2):
    global IsFree
    #仅一组在运行，则直接结束
    print('[INFO] start detec IsFree')
    if len(ClientUrls_1)==0 or len(ClientUrls_2)==0:
        IsFree[0]=True
        IsFree[1]=True
        return
    while True:
        #检测第一组
        print('[INFO] detec IsFree')
        IsFree[0]=True
        for i in range(len(ClientUrls_1)):
            state=ClientUrls_1[i].call('ArmHeartbeat',[False])
            print('ArmPis_free() state=',state)
            #当有机械臂处于抓取状态
            if state[1]==1:
                print('No.1 busy')
                lock.acquire()
                IsFree[0]=False
                IsFree[1]=True
                lock.release()
                break
        # #检测第二组
        IsFree[1]=True
        for i in range(len(ClientUrls_2)):
            state=ClientUrls_2[i].call('ArmHeartbeat',[False])
            #当有机械臂处于抓取状态
            if state[1]==1:
                print('No.2 busy')
                lock.acquire()
                IsFree[1]=False
                IsFree[0]=True
                lock.release()
                break
        time.sleep(1)#切换组状态后停顿2s(周期)


#判断机械臂组是否已经完成一轮抓取
# 如果处于悬空阶段和抓取阶段则开始后续操作
def ArmPi_free(ArmPiClient):
    print('[INFO] start detec ArmPi_free()')
    isFree=False
    while not isFree:
        state=ArmPiClient.call('ArmHeartbeat',[False])
        print('state',state)
        if state[1]==0 :
            return False
        if state[1]==1 or state[1]==3 or state[1]==4:
             return True
    
def ArmPis():
    url_1='http://192.168.0.102:9030'
    Clients=[RPCClient(url_1)]
    thread1 = threading.Thread(target=ArmPis_free, args=(Clients,[]))
    thread2 = threading.Thread(target=ArmPi_client, args=(url_1,0))
    # 启动线程
    thread1.start()
    thread2.start()
    # thread3.start()
    # 等待两个线程结束
    thread1.join()
    thread2.join()

#作为一个子线程运行
def ArmPi_client(url,num):
    # url='http://192.168.0.102:9030'
    Armclient = RPCClient(url)
    # DBClient=HTTPClient('http://192.168.0.103:8000')
    DBClient=HTTPClient('http://192.168.0.100:8092/getDst')
    ArmPi_catch(Armclient,DBClient,num)#机械臂组组号 0 1

#传入一个ArmPi客户端和一个DB控制客户端
def ArmPi_catch(Armclient,DBClient,num):
    global IsFree
    # Armclients=[Armclient]
    # count=0
    #机械臂组组号 0 1
    # num=0
    # 启动机械臂服务
    response = Armclient.call('LoadFunc', [2],)
    print(f'LoadFunc{response}')
    response = Armclient.call('StartFunc', [])
    print(f'StartFunc{response}')
    time.sleep(1)
    while True:
        #判断当前机械臂组是否可以抓取
        print('Is Free',IsFree[1-num])
        if not IsFree[1-num]:
            continue
        #判断当前机械臂是否空闲，空闲则开始抓取
        if not ArmPi_free(Armclient):
            continue
        #开始抓取
        print("允许抓取",num)
        Armclient.call('ArmHeartbeat',[True])
        #获取订单号
        response = Armclient.call('GetOrderId', [])
        print(f'GetOrderId{response}')
        print(response[0])
        print(response[1])
        if response[1]=='null':
            time.sleep(1)
            # count+=1
            continue
        if response[0]:
            #开始放置
            orderID=str(response[1])
            print(f"orderID={orderID}")
            DB_req_start=time.perf_counter()
            ret=DBClient.call(orderID)
            DB_req_end=time.perf_counter()
            print(f'DBClinet response:{ret},req_time={(DB_req_end-DB_req_start)*1000}ms')
            dst=ret.content.decode()
            print(f"put to {dst}")
            response = Armclient.call('CargoPlacement', [dst])
            if response[0]:
                IsFree[num]=False
                time.sleep(2)#睡眠2s
            print(response)
        else:
            print(response)
        
        # if count>5:
        #     return
        # count=0


# Usage:
if __name__ == '__main__':
    # 定义多个client客户端分别和机械臂通信
    ArmPis()
    # ArmPi_catch(Armclient_1,DBClient)
    sys.exit()