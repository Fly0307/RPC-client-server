import threading

# 定义一个全局变量列表
my_list = [1, 2, 3, 4, 5]

# 创建一个线程锁
lock = threading.Lock()

# 定义一个线程函数，向my_list中添加元素
def add_element():
    global my_list  # 声明my_list为全局变量
    lock.acquire()  # 获取锁
    my_list.append(6)
    my_list.append(6)
    lock.release()  # 释放锁

# 定义另一个线程函数，从my_list中删除元素
def remove_element():
    global my_list  # 声明my_list为全局变量
    lock.acquire()  # 获取锁
    my_list.pop()
    lock.release()  # 释放锁

# 创建两个线程，分别调用add_element和remove_element函数
thread1 = threading.Thread(target=add_element)
thread2 = threading.Thread(target=remove_element)

# 启动线程
thread1.start()
thread2.start()

# 等待两个线程结束
thread1.join()
thread2.join()

# 打印最终的my_list
print(my_list)
