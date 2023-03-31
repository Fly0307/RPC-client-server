import RPCServer
import threading
import queue
import time
import RPCClient
from HTTPClient import *
import requests
from collections import defaultdict


QUEUE_RPC = queue.Queue(10)

get_address_lock=threading.Lock()

orderIDs = set()
orderID_address = {}

ArmPis_1 = set()
ArmPis_2 = set()

# 注册http服务
# url = "http://192.168.0.100:8092/getDst"
url="http://localhost:8000/getDst"
httpclient = HTTPClient(url)


def startClientRPC():
    """
    启动边服务RPCserver
    """
    RPCServer.QUEUE = QUEUE_RPC
    print("strat Armpi RPC")
    threading.Thread(target=RPCServer.startRPCServer, daemon=True).start()  # rpc服务器
    while True:
        time.sleep(0.005)
        while True:
            try:
                req, ret = QUEUE_RPC.get(False)
                event, params, *_ = ret
                ret[2] = req(params)  # 执行RPC命令
                event.set()
            except:
                break


def get_orders_address():
    """
    通过http请求从数据中心批量获取订单
    """
    print("通过http请求从数据中心批量获取订单")
    global orderIDs
    global orderID_address
    # 遍历orderIDs，发送http请求获取地址信息，并将结果存储到orderID_des中
    # for orderID in orderIDs:
        # 假设获取地址信息的API为"http://example.com/address?orderID={}"，
        # 其中{}表示占位符，用于插入订单号
        # url = "http://example.com/address?orderID={}".format(orderID)
        # response = requests.get(url)
        # response = httpclient.post(orderID)
        # if response.status_code == 200:
        #     des = response.content.decode()  # 假设返回的地址信息为文本类型
        #     orderID_address[orderID] = des
        #     orderIDs.remove(orderID)  # 删除已经获取到地址信息的订单号
    orderIDs_list=list(orderIDs)
    payload = {'orders': orderIDs_list}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload,headers=headers)
    # print(response.request.headers)
    # print(response.request.body)
    # print("response: {}".format(response))
    # print("response text content:", response.text)
    #获取字节形式的相应内容并用utf-8格式来解码
    # print("response content:", response.content.decode())
    # print(response)
    data = response.json()
    # print(data)
    # orderID_address = defaultdict(set)
    for order, address in data.items():
        orderID_address[order]=address
    # del orderIDs
    # orderIDs=None
    for order, addresses in orderID_address.items():
            print(f"Order: {order}, Addresses: {addresses}")

def add_orderIDs(orderID_list):
    """
    向orderIDs批量增加订单号
    :param orderID_list: 订单号列表
    """
    global orderIDs
    global orderID_address
    print(f"orderID_list={orderID_list}")
    for orderID in orderID_list:
        if (orderID not in orderIDs) and (orderID not in orderID_address):
            orderIDs.add(orderID)

    print(f"orderIDs={orderIDs}")
    get_orders_address()
    return (True,True)


def get_address(id_order):
    """传入订单号，返回对应地址
    :param id_order:[机械臂号，订单号]
    """
    global orderID_address
    global ArmPis_1
    global ArmPis_2
    global get_address_lock
    get_address_lock.acquire()

    ArmPi_id = id_order[0]
    orderID = id_order[1]
    print(f"id_order={id_order},{ArmPi_id} get lock")
    state = False
    if ArmPi_id % 2 == 0:
        if len(ArmPis_1) == 0:
            ArmPis_2.add(ArmPi_id)
            state = True
    else:
        if len(ArmPis_2) == 0:
            ArmPis_1.add(ArmPi_id)
            state = True
    if orderID in orderID_address:
        res = {"state": state, "des": orderID_address[orderID]}
        # if state:
        #     del orderID_address[orderID]
        del orderID_address[orderID]
    else:
        res = {"state": state, "des": None}
        # return (True,res)
    get_address_lock.release()
    print(f"{ArmPi_id} release lock")
    return (True,res)
    

def update_state(ArmPi_id):
    """
    机械臂抓取后通知边服务更新状态
    :param
    """
    global ArmPis_1
    global ArmPis_2
    print(f"ArmPi_id {ArmPi_id} finished")
    if ArmPi_id % 2 == 0:
        ArmPis_2.remove(ArmPi_id)
    else:
        ArmPis_1.remove(ArmPi_id)
    time.sleep(0.5)
    return (True,True)


if __name__ == "__main__":
    # 启动RPC服务
    startClientRPC()
