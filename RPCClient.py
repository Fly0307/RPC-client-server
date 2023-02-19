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

# 0 未识别   3 已经抓取悬空
# 1 抓取阶段 2 放置阶段 
ArmRuning_1=0
#定义一个全局变量列表,可以作为两个机械臂组的‘锁’，
# 为正在抓取阶段(1)则为False，
# 为放置阶段(2)、悬空阶段(3)、未识别(0)则True,允许另一组行动
IsFree=[False,False]
ArmPi_lock=True
# 创建一个线程锁
lock = threading.Lock()
lock2= threading.Lock()
#存储订单信息
orders = set()  # 用 set 来记录订单号

#传入两组机械臂的Url,修改当前
def ArmPis_free(num):
    global IsFree
    
    url_1='http://192.168.0.102:9030'
    url_2='http://192.168.0.104:9030'
    ClientUrls_1=[RPCClient(url_1)]
    ClientUrls_2=[RPCClient(url_2)]
    
    #仅一组在运行，则直接结束
    print('[INFO] start detec IsFree')
    if len(ClientUrls_1)==0 or len(ClientUrls_2)==0:
        IsFree[0]=True
        IsFree[1]=True
        return
    # 0 未识别   3 已经抓取悬空 4 识别到未抓取
    # 1 抓取阶段 2 放置阶段 
    #检测第一组
    if num==0:
        IsFree[0]=False
        for i in range(len(ClientUrls_1)):
            state=ClientUrls_1[i].call('ArmHeartbeat',[False])
            print('ArmPis_free() state=',state)
            #当有机械臂处于抓取状态
            if state[1]==1 or state[1]==4:
                print('No.0 is busy',state)
                lock.acquire()
                IsFree[0]=False
                lock.release()
                return
        print('state',state)
        IsFree[0]=True
    elif num==1:
        #检测第二组
        IsFree[1]=False
        for i in range(len(ClientUrls_2)):
            state2=ClientUrls_2[i].call('ArmHeartbeat',[False])
            #当有机械臂处于抓取状态
            if state2[1]==1 :
                print('No.1 is busy',state2)
                lock.acquire()
                IsFree[1]=False
                lock.release()
                return
        print('state2',state2)
        IsFree[1]=True
    print(IsFree)


#判断机械臂组是否已经完成一轮抓取
# 如果处于悬空阶段和抓取阶段则开始后续操作
def ArmPi_free(ArmPiClient):
    # num=len(ArmPiClient)
    print('[INFO] start detec ArmPi_free()')
    isFree=False
    while not isFree:
        state=ArmPiClient.call('ArmHeartbeat',[False])
        print('state',state)
        if state[1]==0:
            isFree=True
            return False
        if state[1]==1 or state[1]==3 or state[1]==4:
             return True
    #循环等待该组机械臂均为空闲状态
    #两个机械臂均为0(未识别)或者已经抓取待放置阶段

def ArmPis():
    url_1='http://192.168.0.102:9030'
    url_2='http://192.168.0.104:9030'
    # Clients=[RPCClient(url_1)]
    # Clients_2=[RPCClient(url_2)]
    thread1 = threading.Thread(target=ArmPi_client, args=(url_1,0))
    thread2 = threading.Thread(target=ArmPi_client, args=(url_2,1))
    # thread3 = threading.Thread(target=ArmPis_free, args=(Clients,Clients_2))

    # 启动线程
    thread1.start()
    thread2.start()
    # thread3.start()
    # 等待两个线程结束
    thread1.join()
    thread2.join()
    # thread3.join()

#作为一个子线程运行
def ArmPi_client(url,num):
    # url='http://192.168.0.102:9030'
    Armclient = RPCClient(url)
    DBClient=HTTPClient('http://192.168.0.103:8000')
    ArmPi_catch(Armclient,DBClient,num)#机械臂组组号 0 1

#传入一个ArmPi客户端和一个DB控制客户端
def ArmPi_catch(Armclient,DBClient,num):
    global IsFree
    global ArmPi_lock
    global orders
    #机械臂组组号 0 1
    # 启动机械臂服务
    response = Armclient.call('LoadFunc', [7],)
    print(response)
    response = Armclient.call('StartFunc', [])
    print(response)
    while True:
        #判断当前机械臂是否空闲，空闲则开始抓取
        if not ArmPi_free(Armclient):
            time.sleep(0.5)
            continue
        #判断对方是否在抓取 IsFree[1-num]
        #判断当前机械臂组是否可以抓取
        ArmPis_free(1-num)
        while not IsFree[1-num]:
            print("not free",1-num)
            time.sleep(0.1)
            ArmPis_free(1-num)
        # while True:
        # 
        #     if ArmPi_lock and IsFree[1-num]:
        #         lock2.acquire()
        #         ArmPi_lock=False
        #         break
        #     else:
        #         time.sleep(0.5)
        #         continue
        #获取订单号
        response = Armclient.call('GetOrderId', [])
        order_number=response[1]
        while True:
            if order_number in orders:
                # 如果订单号已经存在,通知重新识别,重新获取订单号
                Armclient.call('CargoPlacement', ['double'])
                response = Armclient.call('GetOrderId', [])
                order_number=response[1]
            else:
                # 订单号不存在，将其添加到 set 中
                orders.add(order_number)
                break
        # response = Armclient.call('GetOrderId', [])
        #开始抓取
        IsFree[num]=False
        print("允许抓取",num)
        Armclient.call('ArmHeartbeat',[True])
        print(response)
        print(response[1])
        # state=Armclient.call('ArmHeartbeat',[True])
        # print(state)
        if response[1]=='null':
            # 未识别出，订单号为null
            time.sleep(1)
            # count+=1
            # ArmPi_lock=True
            # lock2.release()
            continue

        if response[0]:
            #开始放置
            ret=DBClient.call(response[1])
            print("put to %s"%(ret.text))
            response = Armclient.call('CargoPlacement', [ret.text])
            # ArmPi_lock=True
            # lock2.release()
            while True:
                response=Armclient.call('ArmHeartbeat', [False])
                if response[1]==0 or response[1]==4:
                    break
                time.sleep(0.5)
            orders.remove(order_number)#处理完订单
            print(response)
        else:
            orders.remove(order_number)#处理完订单
            # ArmPi_lock=True
            # lock2.release()
            print(response)

""" def ArmPis_catch():
    Armclient=RPCClient('http://192.168.0.102:9030')
    DBClient=HTTPClient('http://192.168.0.103:8000')
    Armclients=[Armclient]
    # 启动服务
    response = Armclient.call('LoadFunc', [7],)
    print(response)
    response = Armclient.call('StartFunc', [])
    print(response)
    # count=0
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
            # count+=1
            continue
        if response[0]:
            ret=DBClient.call(response[1])
            print(ret.text)
            response = Armclient.call('CargoPlacement', [ret.text])
            print(response)
        else:
            print(response)
        # if count>5:
        #     return
        # count=0
 """
# Usage:
if __name__ == '__main__':
    # 定义多个client客户端分别和机械臂通信
    # url = "http://localhost:9030" 替换为端地址
    # Armclient_1 = RPCClient('http://192.168.0.102:9030')
    # DBClient=HTTPClient('http://192.168.0.103:8000')
    # Armclient_2 = RPCClient('URL')
    # Armclient_3 = RPCClient('URL')
    # Armclient_4 = RPCClient('URL')
    # 启动机械臂服务
    # response = Armclient_1.call('LoadFunc', [7],)
    # print(response)
    # response = Armclient_1.call('StartFunc', [])
    # print(response)
    # time.sleep(1)
    # count=0
    ArmPis()
    # ArmPi_catch(Armclient_1,DBClient)
    sys.exit()