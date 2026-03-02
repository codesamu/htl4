import threading
import time

balance = 1000
lock=threading.Lock()

def withdraw(amount):
    """ only withdraw amount if it's smaller then your balance"""
    global balance

    lock.acquire()

    if balance >= amount:
        time.sleep(0.1)
        balance-=amount
        print(f"{amount} withdrawn, new balance: {balance}")

    else:
        print(f"Insufficient funds!")

    lock.release()

# withdraw(500)
# withdraw(600)

w1= threading.Thread(target=withdraw, args=(500,))
w2= threading.Thread(target=withdraw, args=(600,))
w1.start()
w2.start()
w1.join()
w2.join()
print(f"Final balance: {balance}")
