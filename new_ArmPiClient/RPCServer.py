import sys
import threading
# from jsonrpc import JSONRPCResponseManager, dispatcher
sys.path.append('/home/raspberry/.local/lib/python3.9/site-packages')
from jsonrpc import JSONRPCResponseManager,dispatcher
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response
import time
import ArmPiClient

if sys.version_info.major == 2:
    print("Please run this program with python3!")
    sys.exit(0)

__RPC_E01 = "E01 - Invalid number of parameter!"
__RPC_E02 = "E02 - Invalid parameter!"
__RPC_E03 = "E03 - Operation failed!"
__RPC_E04 = "E04 - Operation timeout!"
__RPC_E05 = "E05 - Not callable"

QUEUE = None


@dispatcher.add_method
def Add_OrderIDs(orderID_list):
    """
    向边服务增加订单
    """
    print("Add Order IDs into orderIDs")
    return runbymainth(ArmPiClient.add_orderIDs, orderID_list)


@dispatcher.add_method
def Get_Adress(id_order):
    """
    从边服务获取订单和抓取状态
    """
    print(f"Get adress from orderIDs id_order={id_order}")
    return runbymainth(ArmPiClient.get_address, (id_order[0],id_order[1]))

@dispatcher.add_method
def Update_state(Armpi_id):
    """
    机械臂抓取后通知边服务更新订单
    """
    return runbymainth(ArmPiClient.update_state, Armpi_id)


@Request.application
def application(request):
    """
    服务的主方法，handle里面的dispatcher就是代理的rpc方法，可以写多个dispatcher
    :param request:
    :return:
    """
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a, b: a + b
    print(request.data)
    response = JSONRPCResponseManager.handle(request.data, dispatcher)
    return Response(response.json, mimetype="application/json")


def runbymainth(req, pas):
    """调用"""
    if callable(req):
        event = threading.Event()
        ret = [event, pas, None]
        QUEUE.put((req, ret))
        count = 0
        # ret[2] =  req(pas)
        # print('ret', ret)
        # 2s以上未返回则超时
        while ret[2] is None:
            time.sleep(0.01)
            count += 1
            if count > 200:
                break
        if ret[2] is not None:
            print(f"ret={ret},ret[2]={ret[2]}")
            if ret[2][0]:
                return ret[2]
            else:
                return (False, __RPC_E03 + " " + ret[2][1])
        else:
            return (False, __RPC_E04)
    else:
        return (False, __RPC_E05)


def startRPCServer():
    #    log = logging.getLogger('werkzeug')
    #    log.setLevel(logging.ERROR)
    # run_simple('',8090,application)
    print("strat Armpi RPC")
    run_simple("", 9030, application)


if __name__ == "__main__":
    startRPCServer()
