import socket 

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

ip= input("IP: ")
try:
    s.connect((ip,50000))

    while True:
        msg= input("Message: ")
        if msg.lower()=="exit":
            print("Exiting ...")
            break

        s.send(msg.encode())
        answer=s.recv(1024)
        if not answer:
            print("Server closed connection")
            break
        print(f"Server says: {answer.decode()}")

except:
    print("Something went wrong")

finally:
    s.close()
