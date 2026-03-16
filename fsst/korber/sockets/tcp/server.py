import socket 

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.bind(("",50000))
s.listen(4) #3 clients akzeptieren

try:
    while True:
        print("waiting for connection")
        comm, addr=s.accept() # get comm- variable and address of client

        try:
            while True:
                data= comm.recv(1024)
                if not data:
                    print("connection closed")
                    break
                print(f"Got {data.decode()} from {addr}")
                answer= input("Antwort: ")
                comm.send(answer.encode())

        finally:
            comm.close()

except:
    print("Something went wrong")

finally:
    s.close()
