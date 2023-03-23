import requests
import json
import urllib.request
import random
import time
from collections import defaultdict

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
    HTTPclient=HTTPClient('http://localhost:8000/getDst')
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
    req = urllib.request.Request(url='http://localhost:8000/getDst', data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as f:
        response = f.read()

    # 处理响应数据
    result = json.loads(response)
    for order_number, destination in result.items():
        print(order_number, destination)

    # 生成长度为 9 的随机订单号

def generate_order_number():
    return '0'+''.join(random.choices('0123456789', k=8))

def time_test():
    # 生成 10 个不同的订单号
    orders = set()
    while len(orders) < 10:
        orders.add(generate_order_number())
    url = 'http://example.com/orders'
    headers = {'Content-Type': 'application/json'}
    data = {'orders': list(orders)}
    response = requests.post(url, json=data, headers=headers)

    # 处理查询结果并存储到集合中
    results = response.json()
    order_results = {}
    for order in orders:
        for result in results:
            if result['order_number'] == order:
                if order not in order_results:
                    order_results[order] = set()
                order_results[order].add(result['status'])
                break

def time_test_2():
    """ 
    一次查询一个订单
    """
    # 定义HTTP服务器地址和查询地址的前缀
    server_url = "http://localhost:8080"
    query_prefix = "/query?order_id="

    # 定义每组订单号的数量和重复查询次数
    order_count = 10
    repeat_count = 100

    # 定义存储每个订单号查询结果的字典
    results = {}
    # 循环执行多次查询
    total_time = 0
    for i in range(repeat_count):
        # 生成一组订单号
        order_ids = set(generate_order_number() for j in range(order_count))
        
        # 发送HTTP请求查询每个订单号的地址信息
        start_time = time.monotonic()
        for order_id in order_ids:
            query_url = server_url + query_prefix + order_id
            response = requests.get(query_url)
            if response.status_code == 200:
                result = response.text.strip()
                results[order_id] = result
    
    # 计算查询时间
    end_time = time.monotonic()
    query_time = end_time - start_time
    total_time += query_time

    # 输出每个订单号的查询结果
    for order_id, result in results.items():
        print(order_id, result)

    # 输出平均每组查询时间
    average_time = total_time / repeat_count
    print("Average query time per group: {:.2f} seconds".format(average_time))

def query_time():
    url = "http://192.168.0.100:8092/getDst"
    # 定义每组订单号的数量和重复查询次数
    order_count = 10
    repeat_count = 100

    start_time = time.perf_counter()

    for i in range(repeat_count):
        orders = [generate_order_number() for _ in range(order_count)]
        payload = {'orders': orders}
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
        # print(f"data={data}")
        order_address_dict = defaultdict(set)
        for order, address in data.items():
            order_address_dict[order]=address
        # print order and its corresponding addresses
        # for order, addresses in order_address_dict.items():
        #     print(f"Order: {order}, Addresses: {addresses}")
        
    end_time = time.perf_counter()

    avg_time = (end_time - start_time) / repeat_count
    print(f"Average time for each batch of {order_count} orders: {avg_time*1000} ms")

def local_test():
    url = "http://localhost:8000/getDst"
    # 定义每组订单号的数量和重复查询次数
    order_count = 5
    repeat_count = 1

    start_time = time.perf_counter()

    for i in range(repeat_count):
        # orders = [generate_order_number() for _ in range(order_count)]
        orders=["000000005","000000004","000000003","000000009","100000020"]
        payload = {'orders': orders}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload,headers=headers)
        print(response.request.headers)
        print(response.request.body)
        print("response: {}".format(response))
        print("response text content:", response.text)
        #获取字节形式的相应内容并用utf-8格式来解码
        print("response content:", response.content.decode("utf-8"))
        print(response)
        data = response.json()
        order_address_dict = defaultdict(set)
        for order, address in data.items():
            order_address_dict[order].add(address)
        # print order and its corresponding addresses
        for order, addresses in order_address_dict.items():
            print(f"Order: {order}, Addresses: {', '.join(addresses)}")
        
    end_time = time.perf_counter()

    avg_time = (end_time - start_time) / repeat_count
    print(f"Average time for each batch of {order_count} orders: {avg_time} seconds")


if __name__=="__main__":
    # httptets1()
    # httptest2()
    query_time()
    # local_test()