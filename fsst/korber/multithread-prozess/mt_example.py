import threading

result=[]

def squares(id,number):
    print(f"Thread {id} working ...")
    r=number**2
    result.append(r)

def power_of_three(id,number):
    print(f"Thread {id} working ...")
    r=number**3
    result.append(r)

if __name__=="__main__":
    n=int(input("Zahl eingeben "))
    t1=threading.Thread(target=squares,args=(1,n))
    t2=threading.Thread(target=power_of_three,args=(2,n))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print(f"Finished! result: {result}")
