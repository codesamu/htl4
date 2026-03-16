import multiprocessing as mp 
import time as t

#globale locks

lock1=mp.Lock()
lock2=mp.Lock()

def worker1(i):
    print(f"Process {i} started")
    lock1.acquire()
    t.sleep(2)
    print(f"{i} acquired lock 1")

    print(f"{i} wants to acquire lock 2")
    lock2.acquire()
    t.sleep(2)
    print(f"{i} got the lock 2")
    t.sleep(2)

    lock1.release()
    lock2.release()

    print(f"{i} finished")

def worker2(i):
    print(f"Process {i} started")
    lock2.acquire()
    t.sleep(2)
    print(f"{i} acquired lock 2")

    print(f"{i} wants to acquire lock 1")
    lock1.acquire()
    t.sleep(2)
    print(f"{i} got the lock 1")
    t.sleep(2)

    lock2.release()
    lock1.release()

    print(f"{i} finished")

if __name__=="__main__":
    p1=mp.Process(target=worker1, args=("P1",))
    p2=mp.Process(target=worker2, args=("P2",))
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Finished")
