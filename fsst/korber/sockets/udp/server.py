import socket

# Socket - Objekt erstellen
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP

try:
    s.bind(("",50000)) # "" = alle IPs, Port 50000
    while True:
        data,add=s.recvfrom(1024) # bytes zum empfangen
        print(f"Receive {data.decode()} from {add} ") # decode() wandelt bytecode in string um

finally:
    s.close()
