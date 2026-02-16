import threading
import random
import time

ref=random.randint(0,100)
stop_event=threading.Event()

def timer():
    time.sleep(10)
    if not stop_event.is_set():
        print(f"\nTime is over, correct number was: {ref}")
        stop_event.set()

def guess():
    print("Guess the number (between 1 and 100) as fast as you can!")
    n = int(input("Your guess: "))

    match n:
        case _ if n > ref:
            print("try a smaller number")
        case _ if n < ref:
            print("try a bigger number")
        case _ if n == ref:
            print("you got it right!!!")
            stop_event.set()
    guess()

if __name__=="__main__":
    t1=threading.Thread(target=timer,args=())
    t2=threading.Thread(target=guess,args=(),daemon=True)
    t1.start()
    t2.start()
    t1.join()

