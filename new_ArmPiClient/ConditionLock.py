import threading

class ConditionManager:
    def __init__(self, count):
        self.count = count
        self.conditions = [threading.Condition() for _ in range(count)]
        
    def acquire_lock(self, index,flg):
        with self.conditions[index]:
            self.locks[index].acquire(flg)

    def release_lock(self, index,):
        with self.conditions[index]:
            self.locks[index].release()

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