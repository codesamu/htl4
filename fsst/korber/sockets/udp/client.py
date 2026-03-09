import socket

# Socket - Objekt erstellen
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4, UDP

ip=input("Ip eingeben ")
port=50000

msg=input("Message: ")

s.sendto(msg.encode(),(ip,port))
s.close()

