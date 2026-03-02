import threading
import time 
import random

sem=threading.Semaphore(3) # 3 threads gleichzeitig

def square(id,num):
    print(f"Thread {id} is waiting for semaphore")
    sem.acquire()
    print(f"Thread {id} is working ...")

    time.sleep(3)
    result=num**2
    print(f"Thread {id} calculated: {result}")
    print(f"Thread {id} is finished ...")
    sem.release()
    print(f"Thread {id} released the semaphore")

threads=[]
for idx in range(16):
    t=threading.Thread(target=square,args=(idx,random.randint(1,100)))
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

print("All finished")
