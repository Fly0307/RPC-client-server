# -*- coding:utf-8 -*-
import threading
import time


num = 0
con = threading.Condition()


class Producer(threading.Thread):
    """生产者"""
    def run(self):
        global num
        # 获取锁
        con.acquire()
        while True:
            num += 1
            print('生产了1个，现在有{0}个'.format(num))
            time.sleep(1)
            if num >= 5:
                print('已达到5个，不再生产')
                # 唤醒消费者
                con.notify()
                # 等待-释放锁；被唤醒-获取锁
                con.wait()
        # 释放锁
        con.release()


class Customer(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.money = 7

    def run(self):
        global num
        while self.money > 0:
            # 由于场景是多个消费者进行抢购，如果将获取锁操作放在循环外(如生产者),
            # 那么一个消费者线程被唤醒时会锁住整个循环，无法实现另一个消费者的抢购。
            # 在循环中添加一套"获取锁-释放锁",一个消费者购买完成后释放锁，其他消费者
            # 就可以获取锁来参与购买。
            con.acquire()
            if num <= 0:
                print('没货了，{0}通知生产者'.format(
                    threading.current_thread().name))
                con.notify()
                con.wait()
            self.money -= 1
            num -= 1
            print('{0}消费了1个, 剩余{1}个'.format(
                threading.current_thread().name, num))
            con.release()
            time.sleep(1)
        print('{0}没钱了-回老家'.format(threading.current_thread().name))


if __name__ == '__main__':
    p = Producer(daemon=True)
    c1 = Customer(name='Customer-1')
    c2 = Customer(name='Customer-2')
    p.start()
    c1.start()
    c2.start()
    c1.join()
    c2.join()