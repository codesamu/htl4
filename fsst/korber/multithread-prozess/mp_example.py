import multiprocessing as mp
import time

# Function to be called with multiple processes
def worker(pid, number):
    print(f"Process {pid} started ...")
    result=number**10
    time.sleep(2)
    print(f"Result of Process {pid}: {result}")
    print(f"Process {pid} beendet")

# without multiprocessing
# worker(1,30)
# worker(2,100)

if __name__=="__main__":

    p1=mp.Process(target=worker,args=(1,10,))
    p2=mp.Process(target=worker,args=(2,100,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
