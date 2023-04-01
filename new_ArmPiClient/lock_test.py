import threading

class ConditionManager:
    def __init__(self, count):
        self.conditions = [threading.Condition() for _ in range(count)]
        self.count = count
    
    def wait(self, index):
        with self.conditions[index]:
            self.conditions[index].wait()
    
    def notify(self, index):
        with self.conditions[index]:
            self.conditions[index].notify()
    
    def notify_all(self):
        for condition in self.conditions:
            with condition:
                condition.notify_all()

manager = ConditionManager(3)

def worker(index):
    print(f"Worker {index} waiting")
    manager.wait(index)
    print(f"Worker {index} notified")

for i in range(3):
    threading.Thread(target=worker, args=(i,)).start()

# 唤醒第1个条件量
manager.notify(1)