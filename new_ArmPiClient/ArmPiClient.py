import RPCServer
import threading
import queue
import time
import RPCClient
from HTTPClient import *
import requests
from collections import defaultdict
from ConditionLock import *


QUEUE_RPC = queue.Queue(10)

addorder_lock = threading.Lock()
con = threading.Condition()
lock = threading.Lock()  # 创建一个互斥锁
lock_manager = ConditionManager(10)


orderIDs = set()
orderID_address = {}

ArmPis_1 = set()
ArmPis_2 = set()
bitmap = 0


# 注册http服务
# url = "http://192.168.0.100:8092/getDst"
url = "http://localhost:8000/getDst"
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
    orderIDs_list = list(orderIDs)
    payload = {"orders": orderIDs_list}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    # print(response.request.headers)
    # print(response.request.body)
    # print("response: {}".format(response))
    # print("response text content:", response.text)
    # 获取字节形式的相应内容并用utf-8格式来解码
    # print("response content:", response.content.decode())
    # print(response)
    data = response.json()
    # print(data)
    # orderID_address = defaultdict(set)
    addorder_lock.acquire()
    for order, address in data.items():
        orderID_address[order] = address
        orderIDs.remove(order)
    addorder_lock.release()

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

    addorder_lock.acquire()
    for orderID in orderID_list:
        if (orderID not in orderIDs) and (orderID not in orderID_address):
            orderIDs.add(orderID)
    addorder_lock.release()

    print(f"orderIDs={orderIDs}")
    get_orders_address()
    return (True, True)


def isFree(ArmId, bitmap):
    """判断ArmID相邻bitmap，均为0时返回True"""
    left = 1
    if ArmId > 0:
        left = bitmap & (1 << (ArmId - 1))
    right = bitmap & (1 << (ArmId + 1))
    return bool(~(left | right))


def get_address(id_order):
    """传入订单号，返回对应地址
    :param id_order:[机械臂号，订单号]
    """
    global orderID_address

    # global ArmPis_1
    # global ArmPis_2
    global bitmap, lock, lock_manager

    ArmPi_id = id_order[0]
    orderID = id_order[1]
    print(f"id_order={id_order},{ArmPi_id} want get lock")

    # 提升容错性
    lock.acquire()
    bitmap = bitmap & (~(1 << (ArmPi_id - 1)))
    lock.release()
    # 没有地址信息则直接返回
    if orderID not in orderID_address:
        res = {"state": False, "des": None}
        return res

    # 有地址信息继续获取
    lock_manager.acquire_lock(ArmPi_id, True)
    # 拿锁阶段 2PL
    while True:
        if ArmPi_id > 0:
            if lock_manager.acquire_lock(ArmPi_id - 1, False):
                if lock_manager.acquire_lock(ArmPi_id + 1, False):
                    # 拿锁成功
                    break
                else:
                    # 拿锁失败放锁
                    lock_manager.release_lock(ArmPi_id - 1)
                    lock_manager.wait(ArmPi_id)
            else:
                lock_manager.wait(ArmPi_id)
        else:
            if lock_manager.acquire_lock(ArmPi_id + 1, False):
                # 拿锁成功
                break
            else:
                # 拿锁失败放锁
                lock_manager.wait(ArmPi_id)

    while isFree(ArmPi_id, bitmap) is not True:
        lock_manager.wait(ArmPi_id)

    print(f"id_order={id_order},{ArmPi_id} get lock")

    if orderID in orderID_address:
        res = {"state": True, "des": orderID_address[orderID]}
        lock.acquire()
        bitmap = bitmap | (1 << ArmPi_id)
        lock.release()
        del orderID_address[orderID]
    else:
        # bitmap=bitmap & (~(1<<(ArmPi_id-1)))
        res = {"state": False, "des": None}
        # return (True,res)
    print(f"{ArmPi_id} release lock")

    # 放锁阶段
    lock_manager.notify(ArmPi_id + 1)

    if ArmPi_id > 0:
        lock_manager.notify(ArmPi_id - 1)
        lock_manager.release_lock(ArmPi_id - 1)
    lock_manager.release_lock(ArmPi_id + 1)
    lock_manager.release_lock(ArmPi_id)
    # con.notify_all()
    # con.notify()
    # con.release()

    return (True, res)


def update_state(ArmPi_id):
    """
    机械臂抓取后通知边服务更新状态
    :param
    """
    global bitmap, lock

    print(f"ArmPi_id {ArmPi_id} finished")
    lock.acquire()
    bitmap = bitmap & (~(1 << (ArmPi_id - 1)))
    lock.release()

    return (True, True)


# def get_address(id_order):
#     """传入订单号，返回对应地址
#     :param id_order:[机械臂号，订单号]
#     """
#     global orderID_address
#     global ArmPis_1
#     global ArmPis_2

#     ArmPi_id = id_order[0]
#     orderID = id_order[1]
#     print(f"id_order={id_order},{ArmPi_id} want get lock")
#     state = False
#     # 没有地址信息则直接返回
#     if orderID not in orderID_address:
#         res = {"state": state, "des": None}
#         return res

#     #有地址信息继续获取
#     con.acquire()
#     if ArmPi_id % 2 == 0:
#         while len(ArmPis_1)!=0:
#             con.notify()
#             con.wait()
#         print(f"id_order={id_order},{ArmPi_id} get lock")
#         ArmPis_2.add(ArmPi_id)
#         state = True
#         # if len(ArmPis_1) == 0:
#         #     ArmPis_2.add(ArmPi_id)
#         #     state = True
#     else:
#         while len(ArmPis_2)!=0:
#             con.notify()
#             con.wait()
#         print(f"id_order={id_order},{ArmPi_id} get lock")
#         ArmPis_1.add(ArmPi_id)
#         state = True

#     if orderID in orderID_address:
#         res = {"state": state, "des": orderID_address[orderID]}
#         # if state:
#         #     del orderID_address[orderID]
#         del orderID_address[orderID]
#     else:
#         res = {"state": False, "des": None}
#         # return (True,res)
#     print(f"{ArmPi_id} release lock")

#     con.notify()
#     con.release()

#     return (True,res)


# def update_state(ArmPi_id):
#     """
#     机械臂抓取后通知边服务更新状态
#     :param
#     """
#     global ArmPis_1
#     global ArmPis_2
#     print(f"ArmPi_id {ArmPi_id} finished")
#     if ArmPi_id % 2 == 0:
#         ArmPis_2.remove(ArmPi_id)
#     else:
#         ArmPis_1.remove(ArmPi_id)
#     time.sleep(0.5)
#     return (True,True)


if __name__ == "__main__":
    # 启动RPC服务
    startClientRPC()
