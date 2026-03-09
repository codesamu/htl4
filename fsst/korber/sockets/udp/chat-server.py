import socket

# Socket - Objekt erstellen
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP
ip= input("IP: ")
port= int(input("Port: "))

try:
    s.bind(("",50000)) # "" = alle IPs, Port 50000
    while True:
        data,add=s.recvfrom(1024) # bytes zum empfangen
        print(f"Receive {data.decode()} from {add} ") # decode() wandelt bytecode in string um
        msg=input("send something: ")
        s.sendto(msg.encode(),(ip,port))

finally:
    s.close()
